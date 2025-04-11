/**
 * Main JavaScript for project_detail.html
 * This file handles the core initialization and shared functionality
 */
(function() {
    // Execute when DOM is fully loaded
    document.addEventListener("DOMContentLoaded", function() {
        console.log("Initializing Project Detail App");

        // Store essential DOM elements in the shared namespace
        const App = window.ProjectApp;
        App.elements = {
            tabButtons: document.querySelectorAll(".tab-button"),
            tabContents: document.querySelectorAll(".tab-content"),
            roomItems: document.querySelectorAll(".room-item"),
            dropdownToggles: document.querySelectorAll(".dropdown-toggle"),
            roomInfoPanel: document.querySelector('.room-info-panel')
        };

        // Register core utility functions
        App.functions.getProjectIdFromUrl = function() {
            const urlParts = window.location.pathname.split('/');
            const projectsIndex = urlParts.indexOf('projects');
            if (projectsIndex !== -1 && urlParts.length > projectsIndex + 1) {
                return urlParts[projectsIndex + 1];
            }
            return null;
        };

        // Initialize the dropdown toggles
        function initDropdowns() {
            // Remove any existing event listeners first (to avoid duplicates)
            App.elements.dropdownToggles.forEach(toggle => {
                const newToggle = toggle.cloneNode(true);
                toggle.parentNode.replaceChild(newToggle, toggle);
            });

            // Re-query the DOM for the new toggles
            App.elements.dropdownToggles = document.querySelectorAll(".dropdown-toggle");

            // Add click handlers to all dropdown toggles
            App.elements.dropdownToggles.forEach(toggle => {
                toggle.addEventListener("click", function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    // Close all other dropdowns first
                    document.querySelectorAll('.project-actions-dropdown.active').forEach(dropdown => {
                        if (dropdown !== this.closest('.project-actions-dropdown')) {
                            dropdown.classList.remove('active');
                        }
                    });

                    // Toggle this dropdown
                    const dropdown = this.closest('.project-actions-dropdown');
                    dropdown.classList.toggle('active');
                });
            });

            // Close dropdowns when clicking elsewhere
            document.addEventListener("click", function(e) {
                if (!e.target.closest('.project-actions-dropdown')) {
                    document.querySelectorAll('.project-actions-dropdown.active').forEach(dropdown => {
                        dropdown.classList.remove('active');
                    });
                }
            });
        }

        // Initialize tree view folders
        function initTreeView() {
            document.querySelectorAll(".folder-toggle").forEach(toggle => {
                toggle.addEventListener("click", function() {
                    const nestedList = this.nextElementSibling;
                    nestedList.classList.toggle("active");
                    this.classList.toggle("open");
                });
            });

            // Also support the regular .toggle class for backward compatibility
            document.querySelectorAll(".toggle:not(.folder-toggle)").forEach(toggle => {
                toggle.addEventListener("click", function() {
                    const nestedList = this.nextElementSibling;
                    if (nestedList) {
                        nestedList.classList.toggle("active");
                        this.classList.toggle("open");
                    }
                });
            });
        }

        // Initialize tab switching
        function initTabSwitching() {
            App.elements.tabButtons.forEach(button => {
                button.addEventListener("click", function() {
                    // Remove active class from all tabs
                    App.elements.tabButtons.forEach(btn => btn.classList.remove("active"));
                    App.elements.tabContents.forEach(content => content.classList.remove("active"));

                    // Add active class to clicked tab
                    this.classList.add("active");
                    document.getElementById(this.dataset.tab).classList.add("active");

                    // Store active tab in localStorage
                    localStorage.setItem("activeTab", this.dataset.tab);
                });
            });
        }

        // Restore previously selected tab
        function restoreActiveTab() {
            const savedTab = localStorage.getItem("activeTab");
            if (savedTab) {
                const tabButton = document.querySelector(`.tab-button[data-tab="${savedTab}"]`);
                if (tabButton) {
                    tabButton.click();
                }
            }
        }

        // Hide all add buttons initially, until a room is selected
        function hideAddButtons() {
            document.querySelectorAll(".add-item-button").forEach(btn => {
                btn.style.display = "none";
            });
        }

        // Global escape key handler
        function setupGlobalEscapeHandler() {
            document.addEventListener("keydown", function(event) {
                if (event.key === "Escape") {
                    // Handle canceling row additions (input rows)
                    const inputRow = document.querySelector(".input-row");
                    if (inputRow) {
                        inputRow.remove();

                        // Show add buttons again
                        document.querySelectorAll(".add-item-button").forEach(btn => {
                            btn.style.display = "inline-block";
                        });
                    }

                    // Row editing cancellation is handled in table_editors.js
                }
            });
        }

        // Register all initialization functions
        function initializeAll() {
            initDropdowns();
            initTreeView();
            initTabSwitching();
            hideAddButtons();
            setupGlobalEscapeHandler();
            restoreActiveTab();

            // These functions will be called from their respective modules
            // when they have finished loading
            if (typeof initRoomDataHandlers === 'function') {
                initRoomDataHandlers();
            }

            if (typeof initTableEditors === 'function') {
                initTableEditors();
            }

            if (typeof initFormEditors === 'function') {
                initFormEditors();
            }

            if (typeof initModalHandlers === 'function') {
                initModalHandlers();
            }
        }

        // Start the initialization process
        initializeAll();
    });
})();