(function() {
    // Keep track of initialized elements to avoid duplication
    const initialized = new Set();

    // The main initialization function
    function initSpecialTabDropdowns() {
        console.log("Initializing special tab dropdowns");

        // Get all dropdown toggles in special tabs
        const specialTabDropdowns = document.querySelectorAll('.special-tab-container .dropdown-toggle');
        console.log(`Found ${specialTabDropdowns.length} special tab dropdowns`);

        specialTabDropdowns.forEach(toggle => {
            // Skip if already initialized
            if (initialized.has(toggle)) return;

            // Mark as initialized
            initialized.add(toggle);

            // Clone toggle to remove existing listeners
            const newToggle = toggle.cloneNode(true);
            toggle.parentNode.replaceChild(newToggle, toggle);

            // Add the click handler to the new toggle
            newToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                // Get the dropdown container
                const dropdown = this.closest('.project-actions-dropdown');
                console.log("Clicked dropdown:", dropdown);

                // Close all other dropdowns
                document.querySelectorAll('.project-actions-dropdown.active').forEach(openDropdown => {
                    if (openDropdown !== dropdown) {
                        openDropdown.classList.remove('active');
                    }
                });

                // Toggle this dropdown
                dropdown.classList.toggle('active');
            });

            // Mark the new toggle as initialized
            initialized.add(newToggle);
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initSpecialTabDropdowns();
            setupTabSwitchListeners();
        });
    } else {
        // DOM already loaded
        initSpecialTabDropdowns();
        setupTabSwitchListeners();
    }

    // Set up listeners for tab switches
    function setupTabSwitchListeners() {
        // Initialize after tab switch
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', function() {
                // Small delay to ensure the DOM is updated
                setTimeout(initSpecialTabDropdowns, 100);
            });
        });

        // Set up global click listener (only once)
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.project-actions-dropdown')) {
                document.querySelectorAll('.project-actions-dropdown.active').forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });

        // MutationObserver to watch for dynamically added content
        const observer = new MutationObserver(mutations => {
            let shouldInit = false;

            mutations.forEach(mutation => {
                if (mutation.addedNodes.length > 0) {
                    shouldInit = true;
                }
            });

            if (shouldInit) {
                setTimeout(initSpecialTabDropdowns, 100);
            }
        });

        // Observe the tab content container for changes
        const tabContentContainer = document.querySelector('.tab-content-container');
        if (tabContentContainer) {
            observer.observe(tabContentContainer, { childList: true, subtree: true });
        }
    }
})();