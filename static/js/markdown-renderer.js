/**
 * Markdown Renderer with Syntax Highlighting
 * Uses marked.js for markdown parsing and highlight.js for code highlighting
 */

(function(window) {
    'use strict';

    /**
     * Configure marked.js with GFM (GitHub Flavored Markdown) options
     */
    function configureMarked() {
        if (typeof marked === 'undefined') {
            throw new Error('marked.js library not loaded');
        }

        // Set marked options for GFM support
        marked.setOptions({
            gfm: true,              // GitHub Flavored Markdown
            breaks: true,           // Convert \n to <br>
            headerIds: true,        // Add IDs to headers
            mangle: false,          // Don't escape autolinked emails
            sanitize: false,        // Allow HTML (be careful in production)
            smartLists: true,       // Use smarter list behavior
            smartypants: false,     // Don't use smart quotes
            xhtml: false            // Don't use self-closing tags
        });
    }

    /**
     * Apply syntax highlighting to code blocks
     * @param {string} code - The code content
     * @param {string} language - The programming language
     * @returns {string} Highlighted HTML
     */
    function highlightCode(code, language) {
        if (typeof hljs === 'undefined') {
            console.warn('highlight.js library not loaded, returning plain code');
            return escapeHtml(code);
        }

        try {
            if (language && hljs.getLanguage(language)) {
                return hljs.highlight(code, { language: language }).value;
            } else {
                // Auto-detect language
                return hljs.highlightAuto(code).value;
            }
        } catch (error) {
            console.error('Highlight error:', error);
            return escapeHtml(code);
        }
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
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

    /**
     * Create a copy button for code blocks
     * @param {string} code - The code content to copy
     * @returns {string} HTML for copy button
     */
    function createCopyButton(code) {
        // Unescape HTML entities for clipboard
        const unescapedCode = code
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&quot;/g, '"')
            .replace(/&#039;/g, "'");

        const escapedCode = escapeHtml(unescapedCode).replace(/"/g, '&quot;');

        return `<button class="copy-button" onclick="copyCodeToClipboard(this, '${escapedCode}')" title="Copy code">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5.5 4.5V2.5C5.5 1.94772 5.94772 1.5 6.5 1.5H13.5C14.0523 1.5 14.5 1.94772 14.5 2.5V9.5C14.5 10.0523 14.0523 10.5 13.5 10.5H11.5M5.5 4.5H2.5C1.94772 4.5 1.5 4.94772 1.5 5.5V13.5C1.5 14.0523 1.94772 14.5 2.5 14.5H9.5C10.0523 14.5 10.5 14.0523 10.5 13.5V5.5C10.5 4.94772 10.0523 4.5 9.5 4.5H5.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Copy
        </button>`;
    }

    /**
     * Custom renderer for marked.js
     */
    function createCustomRenderer() {
        const renderer = new marked.Renderer();

        // Override code block rendering
        renderer.code = function(code, language, isEscaped) {
            const validLanguage = language || 'plaintext';
            const highlightedCode = highlightCode(code, validLanguage);
            const languageLabel = validLanguage !== 'plaintext' ? validLanguage : '';
            const copyButton = createCopyButton(code);

            return `<div class="code-block-wrapper">
                <div class="code-block-header">
                    <span class="code-language">${languageLabel}</span>
                    ${copyButton}
                </div>
                <pre><code class="hljs language-${validLanguage}">${highlightedCode}</code></pre>
            </div>`;
        };

        // Override inline code rendering
        renderer.codespan = function(code) {
            return `<code class="inline-code">${escapeHtml(code)}</code>`;
        };

        // Override table rendering to add responsive wrapper
        renderer.table = function(header, body) {
            return `<div class="table-wrapper">
                <table>
                    <thead>${header}</thead>
                    <tbody>${body}</tbody>
                </table>
            </div>`;
        };

        // Override link rendering to add target="_blank" for external links
        renderer.link = function(href, title, text) {
            const isExternal = href && (href.startsWith('http://') || href.startsWith('https://'));
            const target = isExternal ? ' target="_blank" rel="noopener noreferrer"' : '';
            const titleAttr = title ? ` title="${title}"` : '';
            return `<a href="${href}"${titleAttr}${target}>${text}</a>`;
        };

        return renderer;
    }

    /**
     * Main function to render markdown with syntax highlighting
     * @param {string} text - Raw markdown text
     * @returns {string} Rendered HTML
     */
    function renderMarkdown(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }

        try {
            // Configure marked.js
            configureMarked();

            // Create custom renderer
            const renderer = createCustomRenderer();

            // Parse markdown with custom renderer
            const html = marked.parse(text, { renderer: renderer });

            return html;
        } catch (error) {
            console.error('Markdown rendering error:', error);
            return `<div class="markdown-error">
                <strong>Error rendering markdown:</strong> ${escapeHtml(error.message)}
            </div>`;
        }
    }

    /**
     * Copy code to clipboard
     * This function is called by the copy button onclick handler
     * @param {HTMLElement} button - The button element that was clicked
     * @param {string} code - The escaped code to copy
     */
    window.copyCodeToClipboard = function(button, code) {
        // Unescape the code
        const unescapedCode = code
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&quot;/g, '"')
            .replace(/&#039;/g, "'");

        // Try modern clipboard API first
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(unescapedCode).then(() => {
                showCopyFeedback(button, true);
            }).catch(err => {
                console.error('Clipboard API failed, trying fallback:', err);
                fallbackCopyToClipboard(button, unescapedCode);
            });
        } else {
            // Fallback for older browsers or non-secure contexts
            fallbackCopyToClipboard(button, unescapedCode);
        }
    };

    /**
     * Fallback copy method using textarea
     * @param {HTMLElement} button - The button element
     * @param {string} text - Text to copy
     */
    function fallbackCopyToClipboard(button, text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();

        try {
            const successful = document.execCommand('copy');
            showCopyFeedback(button, successful);
        } catch (err) {
            console.error('Fallback copy failed:', err);
            showCopyFeedback(button, false);
        }

        document.body.removeChild(textarea);
    }

    /**
     * Show visual feedback when code is copied
     * @param {HTMLElement} button - The button element
     * @param {boolean} success - Whether copy was successful
     */
    function showCopyFeedback(button, success) {
        const originalContent = button.innerHTML;

        if (success) {
            button.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3.5 8.5L6.5 11.5L12.5 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>Copied!`;
            button.classList.add('copied');
        } else {
            button.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4.5 4.5L11.5 11.5M11.5 4.5L4.5 11.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>Failed`;
            button.classList.add('copy-failed');
        }

        // Reset button after 2 seconds
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.classList.remove('copied', 'copy-failed');
        }, 2000);
    }

    // Export the main function to global scope
    window.renderMarkdown = renderMarkdown;

})(window);
