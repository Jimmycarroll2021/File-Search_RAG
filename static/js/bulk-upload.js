/**
 * Bulk Upload JavaScript
 * Handles bulk upload functionality including scanning, uploading, and progress tracking
 */

// Global state
let scanResults = null;
let uploadResults = null;

/**
 * Open the bulk upload modal
 */
function openBulkUploadModal() {
    const modal = document.getElementById('bulkUploadModal');
    modal.classList.add('active');
    resetBulkUpload();
    loadStoresForBulkUpload(); // Load stores when modal opens
}

/**
 * Close the bulk upload modal
 */
function closeBulkUploadModal() {
    const modal = document.getElementById('bulkUploadModal');
    modal.classList.remove('active');
}

/**
 * Reset the bulk upload UI to initial state
 */
function resetBulkUpload() {
    // Hide sections
    document.getElementById('scanResultsSection').style.display = 'none';
    document.getElementById('uploadProgressSection').style.display = 'none';
    document.getElementById('resultsTableSection').style.display = 'none';

    // Reset state
    scanResults = null;
    uploadResults = null;

    // Reset buttons
    document.getElementById('scanDirectoryBtn').disabled = false;
    document.getElementById('startUploadBtn').disabled = true;

    // Clear status
    document.getElementById('bulkUploadStatus').innerHTML = '';
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Scan directory for files
 */
async function scanDirectory() {
    const sourceDirectory = document.getElementById('bulkSourceDirectory').value.trim();
    const autoCategorize = document.getElementById('autoCategorize').checked;

    // Validate input
    if (!sourceDirectory) {
        showStatus('Please enter a source directory', 'error');
        return;
    }

    // Disable button and show loading
    const scanBtn = document.getElementById('scanDirectoryBtn');
    scanBtn.disabled = true;
    scanBtn.textContent = 'Scanning...';

    try {
        showStatus('Scanning directory...', 'info');

        const response = await fetch('/api/files/bulk_upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_directory: sourceDirectory,
                auto_categorize: autoCategorize,
                scan_only: true
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to scan directory');
        }

        if (!data.success) {
            throw new Error(data.error || 'Scan failed');
        }

        // Store results
        scanResults = data;

        // Display results
        displayScanResults(data);

        // Enable upload button
        document.getElementById('startUploadBtn').disabled = false;

        showStatus(`Found ${data.total} files in ${Object.keys(data.category_distribution).length} categories`, 'success');

    } catch (error) {
        console.error('Scan error:', error);
        showStatus(`Error: ${error.message}`, 'error');
        document.getElementById('startUploadBtn').disabled = true;
    } finally {
        scanBtn.disabled = false;
        scanBtn.textContent = 'Scan Directory';
    }
}

/**
 * Display scan results
 */
function displayScanResults(data) {
    // Show section
    document.getElementById('scanResultsSection').style.display = 'block';

    // Update summary
    document.getElementById('scanTotalFiles').textContent = data.total;
    document.getElementById('scanTotalCategories').textContent = Object.keys(data.category_distribution).length;

    // Display category distribution
    const distributionContainer = document.getElementById('categoryDistribution');
    distributionContainer.innerHTML = '';

    for (const [category, count] of Object.entries(data.category_distribution)) {
        const card = document.createElement('div');
        card.className = 'category-card';
        card.innerHTML = `
            <span class="category-name">${category || 'uncategorized'}</span>
            <span class="category-count">${count}</span>
        `;
        distributionContainer.appendChild(card);
    }
}

/**
 * Start bulk upload
 */
async function startBulkUpload() {
    const sourceDirectory = document.getElementById('bulkSourceDirectory').value.trim();
    const storeName = document.getElementById('bulkStoreName').value;
    const autoCategorize = document.getElementById('autoCategorize').checked;
    const batchSize = parseInt(document.getElementById('batchSize').value);

    // Validate inputs
    if (!sourceDirectory) {
        showStatus('Please enter a source directory', 'error');
        return;
    }

    if (!storeName) {
        showStatus('Please select a target store', 'error');
        return;
    }

    if (!scanResults || scanResults.total === 0) {
        showStatus('Please scan the directory first', 'error');
        return;
    }

    // Disable buttons
    document.getElementById('scanDirectoryBtn').disabled = true;
    document.getElementById('startUploadBtn').disabled = true;
    document.getElementById('startUploadBtn').textContent = 'Uploading...';

    // Show progress section
    document.getElementById('uploadProgressSection').style.display = 'block';
    resetProgressDisplay();

    // Start animated progress bar
    const progressBar = document.getElementById('uploadProgressBar');
    progressBar.classList.add('animating');
    progressBar.style.width = '10%'; // Show initial progress

    try {
        showStatus('Uploading and indexing files...', 'info');

        // Simulate gradual progress during upload
        const totalFiles = scanResults.total;
        let simulatedProgress = 0;
        const progressInterval = setInterval(() => {
            simulatedProgress += Math.random() * 15;
            if (simulatedProgress > 85) simulatedProgress = 85; // Cap at 85% until real data arrives
            updateProgressDisplay(Math.floor((simulatedProgress / 100) * totalFiles), totalFiles, 0, 0, 0);
        }, 500);

        const response = await fetch('/api/files/bulk_upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_directory: sourceDirectory,
                store_name: storeName,
                auto_categorize: autoCategorize,
                batch_size: batchSize
            })
        });

        // Stop simulated progress
        clearInterval(progressInterval);

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        if (!data.success) {
            throw new Error(data.error || 'Upload failed');
        }

        // Store results
        uploadResults = data;

        // Stop animation and update with final progress
        progressBar.classList.remove('animating');
        updateProgressDisplay(data.total, data.total, data.success_count, data.failed_count, data.skipped_count || 0);

        // Display results table
        displayUploadResults(data);

        showStatus(data.message || 'Upload completed!', 'success');

    } catch (error) {
        console.error('Upload error:', error);
        const progressBar = document.getElementById('uploadProgressBar');
        progressBar.classList.remove('animating');
        progressBar.style.backgroundColor = '#dc3545'; // Red for error
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        document.getElementById('scanDirectoryBtn').disabled = false;
    }
}

/**
 * Reset progress display
 */
function resetProgressDisplay() {
    document.getElementById('uploadProgressBar').style.width = '0%';
    document.getElementById('uploadProgressText').textContent = '0 / 0 files uploaded (0%)';
    document.getElementById('uploadSuccessCount').textContent = '0';
    document.getElementById('uploadFailedCount').textContent = '0';
    document.getElementById('uploadSkippedCount').textContent = '0';
}

/**
 * Update progress display
 */
function updateProgressDisplay(processed, total, success, failed, skipped) {
    const percentage = total > 0 ? Math.round((processed / total) * 100) : 0;

    // Update progress bar
    const progressBar = document.getElementById('uploadProgressBar');
    progressBar.style.width = `${percentage}%`;

    // Update progress text
    document.getElementById('uploadProgressText').textContent =
        `${processed} / ${total} files uploaded (${percentage}%)`;

    // Update stats
    document.getElementById('uploadSuccessCount').textContent = success;
    document.getElementById('uploadFailedCount').textContent = failed;
    document.getElementById('uploadSkippedCount').textContent = skipped;
}

/**
 * Display upload results in table
 */
function displayUploadResults(data) {
    // Show section
    document.getElementById('resultsTableSection').style.display = 'block';

    // Populate table
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';

    data.files.forEach(file => {
        const row = document.createElement('tr');
        row.className = `result-row result-${file.status}`;
        row.innerHTML = `
            <td>${file.filename}</td>
            <td>${file.category || 'uncategorized'}</td>
            <td>${file.file_size ? formatFileSize(file.file_size) : '-'}</td>
            <td>
                <span class="status-badge status-${file.status}">
                    ${file.status}
                </span>
            </td>
            <td>${file.error || '-'}</td>
        `;
        tbody.appendChild(row);
    });

    // Update summary
    const summaryText = `
        Uploaded ${data.success_count} of ${data.total} files successfully.
        ${data.failed_count} failed, ${data.skipped_count} skipped.
    `;
    document.getElementById('resultsSummaryText').textContent = summaryText;
}

/**
 * Filter results table
 */
function filterResults() {
    if (!uploadResults) return;

    const statusFilter = document.getElementById('statusFilter').value;
    const searchText = document.getElementById('filenameSearch').value.toLowerCase();

    const rows = document.querySelectorAll('.result-row');

    rows.forEach(row => {
        const status = row.querySelector('.status-badge').textContent.trim();
        const filename = row.querySelector('td:first-child').textContent.toLowerCase();

        const matchesStatus = statusFilter === 'all' || status === statusFilter;
        const matchesSearch = filename.includes(searchText);

        row.style.display = (matchesStatus && matchesSearch) ? '' : 'none';
    });
}

/**
 * Show status message
 */
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('bulkUploadStatus');
    statusDiv.textContent = message;
    statusDiv.className = 'status-message';

    if (type === 'success') {
        statusDiv.style.color = '#28a745';
    } else if (type === 'error') {
        statusDiv.style.color = '#dc3545';
    } else {
        statusDiv.style.color = '#666';
    }
}

/**
 * Load stores into dropdown
 */
async function loadStoresForBulkUpload() {
    try {
        const response = await fetch('/api/files/list_stores');
        const data = await response.json();

        if (data.success && data.stores) {
            const select = document.getElementById('bulkStoreName');
            select.innerHTML = '<option value="">Select a store...</option>';

            data.stores.forEach(store => {
                const option = document.createElement('option');
                option.value = store;
                option.textContent = store;
                select.appendChild(option);
            });

            // If only one store exists, select it by default
            if (data.stores.length === 1) {
                select.value = data.stores[0];
            }
        }
    } catch (error) {
        console.error('Error loading stores:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Close modal when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('bulkUploadModal');
        if (event.target === modal) {
            closeBulkUploadModal();
        }
    };
});
