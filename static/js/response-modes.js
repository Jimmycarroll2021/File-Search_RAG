/**
 * Response Modes Manager
 * Handles mode selection state and UI updates
 */

(function() {
    'use strict';

    // Mode configurations (matching backend)
    const MODES = {
        tender: {
            name: 'Tender Response',
            icon: '📋',
            description: 'Formal, polished responses for tender submissions'
        },
        quick: {
            name: 'Quick Answer',
            icon: '⚡',
            description: 'Brief, bullet-point answers'
        },
        analysis: {
            name: 'Deep Analysis',
            icon: '🔍',
            description: 'Detailed insights with citations'
        },
        strategy: {
            name: 'Strategy Advisor',
            icon: '💡',
            description: 'Recommendations and next steps'
        },
        checklist: {
            name: 'Compliance Checklist',
            icon: '✅',
            description: 'Action items and requirements'
        }
    };

    // Current active mode
    let activeMode = 'quick';

    /**
     * Initialize response modes functionality
     */
    function init() {
        const modeCards = document.querySelectorAll('.mode-card');

        // Add click handlers to all mode cards
        modeCards.forEach(card => {
            card.addEventListener('click', () => handleModeSelect(card));

            // Add keyboard support
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleModeSelect(card);
                }
            });
        });

        // Set initial mode from localStorage if available
        const savedMode = localStorage.getItem('responseMode');
        if (savedMode && MODES[savedMode]) {
            const savedCard = document.querySelector(`.mode-card[data-mode="${savedMode}"]`);
            if (savedCard) {
                handleModeSelect(savedCard);
            }
        }
    }

    /**
     * Handle mode card selection
     */
    function handleModeSelect(card) {
        const mode = card.getAttribute('data-mode');

        if (!mode || !MODES[mode]) {
            console.error('Invalid mode selected:', mode);
            return;
        }

        // Update active mode
        activeMode = mode;

        // Save to localStorage
        localStorage.setItem('responseMode', mode);

        // Update UI
        updateModeUI(card, mode);

        // Trigger custom event for other components
        const event = new CustomEvent('modeChanged', {
            detail: {
                mode: mode,
                config: MODES[mode]
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Update mode selection UI
     */
    function updateModeUI(selectedCard, mode) {
        // Remove active class from all cards
        const allCards = document.querySelectorAll('.mode-card');
        allCards.forEach(card => card.classList.remove('active'));

        // Add active class to selected card
        selectedCard.classList.add('active');

        // Add selection animation
        selectedCard.classList.add('selecting');
        setTimeout(() => {
            selectedCard.classList.remove('selecting');
        }, 300);

        // Update indicator
        updateModeIndicator(mode);
    }

    /**
     * Update active mode indicator
     */
    function updateModeIndicator(mode) {
        const config = MODES[mode];
        const indicatorIcon = document.querySelector('.indicator-icon');
        const indicatorName = document.querySelector('.indicator-name');

        if (indicatorIcon && indicatorName) {
            indicatorIcon.textContent = config.icon;
            indicatorName.textContent = config.name;
        }
    }

    /**
     * Get current active mode
     */
    function getActiveMode() {
        return activeMode;
    }

    /**
     * Get mode configuration
     */
    function getModeConfig(mode) {
        return MODES[mode] || MODES.quick;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export functions for use by other scripts
    window.ResponseModes = {
        getActiveMode,
        getModeConfig,
        MODES
    };

})();
