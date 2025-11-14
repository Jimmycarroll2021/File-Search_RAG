/**
 * Main JavaScript for Google Gemini File Search
 * Handles file upload, queries, and markdown rendering
 */

(function() {
    'use strict';

    // DOM elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const uploadStatus = document.getElementById('uploadStatus');
    const queryBtn = document.getElementById('queryBtn');
    const questionInput = document.getElementById('questionInput');
    const responseArea = document.getElementById('responseArea');
    const queryStatus = document.getElementById('queryStatus');
    const storeName = document.getElementById('storeName');

    let selectedFile = null;

    /**
     * Initialize event listeners
     */
    function init() {
        // File upload area click
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);

        // File input change
        fileInput.addEventListener('change', handleFileInputChange);

        // Query button
        queryBtn.addEventListener('click', handleQuery);

        // Enter key to submit question
        questionInput.addEventListener('keydown', handleKeyDown);
    }

    /**
     * Handle drag over event
     */
    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    }

    /**
     * Handle drag leave event
     */
    function handleDragLeave() {
        uploadArea.classList.remove('dragover');
    }

    /**
     * Handle drop event
     */
    function handleDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    }

    /**
     * Handle file input change
     */
    function handleFileInputChange(e) {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    }

    /**
     * Handle file selection
     */
    function handleFileSelect(file) {
        selectedFile = file;
        fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        uploadFile();
    }

    /**
     * Upload file to server
     */
    async function uploadFile() {
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('store_name', storeName.value);

        // Show animated upload message
        uploadStatus.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="upload-spinner"></div>
                <span>Uploading and indexing "${selectedFile.name}"...</span>
            </div>
        `;
        uploadStatus.className = 'status-message show success';

        try {
            const response = await fetch('/upload_file', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                uploadStatus.innerHTML = `✓ ${data.message}`;
                uploadStatus.className = 'status-message show success';
                if (data.category) {
                    uploadStatus.innerHTML += `<br><small>Category: ${data.category}</small>`;
                }
            } else {
                uploadStatus.innerHTML = `✗ Error: ${data.error}`;
                uploadStatus.className = 'status-message show error';
            }

            // Auto-hide after 5 seconds
            setTimeout(() => {
                uploadStatus.classList.remove('show');
            }, 5000);
        } catch (error) {
            uploadStatus.innerHTML = `✗ Error: ${error.message}`;
            uploadStatus.className = 'status-message show error';

            setTimeout(() => {
                uploadStatus.classList.remove('show');
            }, 5000);
        }
    }

    /**
     * Handle query submission
     */
    async function handleQuery() {
        const question = questionInput.value.trim();

        if (!question) {
            showStatus(queryStatus, 'Please enter a question', 'error');
            return;
        }

        queryBtn.disabled = true;
        queryBtn.innerHTML = 'Searching... <span class="loader"></span>';
        responseArea.classList.remove('show');
        queryStatus.classList.remove('show');

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    store_name: storeName.value
                })
            });

            const data = await response.json();

            if (data.success) {
                // Use markdown renderer if available
                if (typeof renderMarkdown === 'function') {
                    responseArea.innerHTML = '<strong>Answer:</strong><br><br>' +
                        renderMarkdown(data.answer);
                } else {
                    // Fallback to plain text rendering
                    console.warn('renderMarkdown function not available, using fallback');
                    responseArea.innerHTML = '<strong>Answer:</strong><br><br>' +
                        escapeHtml(data.answer).replace(/\n/g, '<br>');
                }
                responseArea.classList.add('show');
            } else {
                showStatus(queryStatus, 'Error: ' + data.error, 'error');
            }
        } catch (error) {
            showStatus(queryStatus, 'Error: ' + error.message, 'error');
        } finally {
            queryBtn.disabled = false;
            queryBtn.textContent = 'Ask Question';
        }
    }

    /**
     * Handle keyboard events
     */
    function handleKeyDown(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            queryBtn.click();
        }
    }

    /**
     * Show status message
     */
    function showStatus(element, message, type, loading = false) {
        element.textContent = message;
        element.className = 'status-message show ' + type;

        if (!loading) {
            setTimeout(() => {
                element.classList.remove('show');
            }, 5000);
        }
    }

    /**
     * Escape HTML special characters
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
