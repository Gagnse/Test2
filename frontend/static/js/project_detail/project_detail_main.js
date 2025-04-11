/**
 * Main JavaScript for project_detail.html
 * This file handles the core functionality that must be present for all components to work
 */
document.addEventListener("DOMContentLoaded", function() {
    // Global variables for the selected room
    let selectedRoomId = "";
    let selectedRoomName = "";

    // Initialize room info panel
    initRoomInfoPanel();

    // Hide all + buttons on load
    document.querySelectorAll(".add-item-button").forEach(btn => {
        btn.style.display = "none";
    });

    // Managing opened/closed folders
    document.querySelectorAll(".folder-toggle").forEach(folder => {
        folder.addEventListener("click", function() {
            const nestedList = this.nextElementSibling;
            nestedList.style.display = nestedList.style.display === "block" ? "none" : "block";
            this.classList.toggle("open");
        });
    });

    // Tab switching functionality
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabContents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(button => {
        button.addEventListener("click", function() {
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove("active"));
            tabContents.forEach(content => content.classList.remove("active"));

            // Add active class to clicked tab
            this.classList.add("active");
            document.getElementById(this.dataset.tab).classList.add("active");

            // Store active tab in localStorage
            localStorage.setItem("activeTab", this.dataset.tab);
        });
    });

    // Restore active tab on load
    const savedTab = localStorage.getItem("activeTab");
    if (savedTab) {
        const activeTabButton = document.querySelector(`.tab-button[data-tab="${savedTab}"]`);
        if (activeTabButton) {
            activeTabButton.click();
        }
    }

    // Select a room and show data
    document.querySelectorAll(".room-item").forEach(room => {
        room.addEventListener("click", function() {
            const roomId = this.getAttribute("data-room-id");
            const roomName = this.innerText.trim();

            // Update selection
            selectedRoomId = roomId;
            selectedRoomName = roomName;

            // Store in session storage for persistence
            sessionStorage.setItem("selectedRoom", roomId);
            sessionStorage.setItem("selectedRoomName", roomName);

            // Show name in "Salle sélectionnée :"
            document.querySelectorAll(".selected-room-name span").forEach(span => {
                span.textContent = roomName;
            });

            // CSS to show selection
            document.querySelectorAll(".room-item").forEach(r => r.classList.remove("active-room"));
            this.classList.add("active-room");

            // Update room info panel
            updateRoomInfoPanel(roomId, roomName);

            // Show + buttons
            document.querySelectorAll(".add-item-button").forEach(btn => {
                btn.style.display = "inline-block";
            });

            // Filter table data and show appropriate forms
            filterRoomData(roomId);
            showSpecialTabForms(roomId);
        });
    });

    // Filter table rows by room
    function filterRoomData(roomId) {
        tabContents.forEach(tab => {
            const rows = tab.querySelectorAll("tbody tr");
            rows.forEach(row => {
                const rowRoomId = row.getAttribute("data-room-id");
                row.style.display = (rowRoomId === roomId) ? "" : "none";
            });
        });
    }

    // Show the appropriate forms for special tabs
    function showSpecialTabForms(roomId) {
        // Handle all special form tabs
        const specialFormTypes = [
            ".functionality-form",
            ".arch_requirements-form",
            ".struct-form",
            ".risk-form",
            ".ventilation-form",
            ".electricity-form"
        ];

        specialFormTypes.forEach(formType => {
            const forms = document.querySelectorAll(formType);
            forms.forEach(form => {
                form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
            });
        });
    }

    // Initialize dropdown handlers
    function initDropdownHandlers() {
        console.log("Initializing dropdown handlers...");

        // First remove existing click handlers to avoid duplicates
        document.querySelectorAll(".dropdown-toggle").forEach(toggle => {
            const newToggle = toggle.cloneNode(true);
            toggle.parentNode.replaceChild(newToggle, toggle);
        });

        // Add click handlers to all dropdown toggles
        document.querySelectorAll(".dropdown-toggle").forEach(toggle => {
            toggle.addEventListener("click", function(e) {
                console.log("Dropdown toggle clicked");
                e.preventDefault();
                e.stopPropagation();

                // First close all other dropdowns
                document.querySelectorAll('.project-actions-dropdown.active').forEach(openDropdown => {
                    if (openDropdown !== this.closest('.project-actions-dropdown')) {
                        openDropdown.classList.remove('active');
                    }
                });

                // Then toggle this dropdown
                const dropdown = this.closest('.project-actions-dropdown');
                dropdown.classList.toggle('active');
            });
        });

        // Close dropdowns when clicking elsewhere on the page
        document.addEventListener("click", function(e) {
            if (!e.target.closest('.project-actions-dropdown')) {
                document.querySelectorAll('.project-actions-dropdown.active').forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });
    }

    // Initialize room info panel
    function initRoomInfoPanel() {
        const roomInfoPanel = document.querySelector('.room-info-panel');

        if (!roomInfoPanel) {
            console.error('Room info panel not found in the DOM');
            return;
        }

        // Get previously selected room from session storage
        const savedRoomId = sessionStorage.getItem("selectedRoom");
        const savedRoomName = sessionStorage.getItem("selectedRoomName");

        if (savedRoomId && savedRoomName) {
            // Make room info panel visible
            roomInfoPanel.style.display = 'block';

            // Update values
            updateRoomInfoPanel(savedRoomId, savedRoomName);

            // Find and highlight the room in the sidebar
            const roomItem = document.querySelector(`.room-item[data-room-id="${savedRoomId}"]`);
            if (roomItem) {
                roomItem.classList.add("active-room");

                // Open parent folders to show the selected room
                let parent = roomItem.parentElement;
                while (parent) {
                    if (parent.classList.contains("nested")) {
                        parent.style.display = "block";
                        const toggle = parent.previousElementSibling;
                        if (toggle && toggle.classList.contains("toggle")) {
                            toggle.classList.add("open");
                        }
                    }
                    parent = parent.parentElement;
                }
            }

            // Filter tables based on selected room
            filterRoomData(savedRoomId);
            showSpecialTabForms(savedRoomId);

            // Show + buttons for the selected room
            document.querySelectorAll(".add-item-button").forEach(btn => {
                btn.style.display = "inline-block";
            });
        }
    }

    // Update the room info panel when a room is selected
    function updateRoomInfoPanel(roomId, roomName) {
        const roomInfoPanel = document.querySelector('.room-info-panel');

        if (!roomId || !roomName) {
            roomInfoPanel.style.display = 'none';
            return;
        }

        // Show the panel with minimal info first (fast user feedback)
        roomInfoPanel.style.display = 'block';
        document.querySelector('.selected-room-title').textContent = roomName;

        // Find the room item in the sidebar (for fallback data)
        const roomItem = document.querySelector(`.room-item[data-room-id="${roomId}"]`);
        if (roomItem) {
            // Try to get sector and unit from DOM structure as a fallback
            try {
                const sectorElement = roomItem.closest('ul').previousElementSibling;
                const unitElement = sectorElement.closest('ul').previousElementSibling;

                const sector = sectorElement ? sectorElement.textContent.replace('📁', '').trim() : '-';
                const unit = unitElement ? unitElement.textContent.replace('📂', '').trim() : '-';

                document.querySelector('.selected-room-sector').textContent = sector;
                document.querySelector('.selected-room-unit').textContent = unit;
            } catch (e) {
                console.log('Could not extract sector/unit from DOM:', e);
            }
        }

        // Fetch complete room details from the server
        fetch(`/workspace/api/rooms/${roomId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const room = data.room;

                    // Update room details with accurate data from the database
                    document.querySelector('.selected-room-sector').textContent = room.sector || '-';
                    document.querySelector('.selected-room-unit').textContent = room.functional_unit || '-';

                    // Format planned area with 2 decimal places if it's a number
                    let areaDisplay = '-';
                    if (room.planned_area) {
                        const areaNum = parseFloat(room.planned_area);
                        areaDisplay = !isNaN(areaNum) ? areaNum.toFixed(2) + ' m²' : room.planned_area;
                    }
                    document.querySelector('.selected-room-area').textContent = areaDisplay;

                    // Add room data attributes to the selected room item for future use
                    if (roomItem) {
                        roomItem.setAttribute('data-program-number', room.program_number || '');
                        roomItem.setAttribute('data-sector', room.sector || '');
                        roomItem.setAttribute('data-unit', room.functional_unit || '');
                        roomItem.setAttribute('data-area', room.planned_area || '');
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching room details:', error);
                // Keep using the fallback data from the DOM if the fetch fails
            });
    }

    // Setup handlers for modals
    function setupModalHandlers() {
        // Project Parameters Modal
        const parametersButtons = document.querySelectorAll('.open-parameters-modal');
        parametersButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();

                // Close the dropdown menu if it's open
                const dropdown = this.closest('.project-actions-dropdown');
                if (dropdown) {
                    dropdown.classList.remove('active');
                }

                // Open the parameters modal
                if (typeof window.openProjectParametersModal === 'function') {
                    window.openProjectParametersModal();
                } else {
                    console.error('openProjectParametersModal function not found');
                    // Get project ID from URL
                    const urlParts = window.location.pathname.split('/');
                    const projectsIndex = urlParts.indexOf('projects');
                    if (projectsIndex !== -1 && urlParts.length > projectsIndex + 1) {
                        const projectId = urlParts[projectsIndex + 1];
                        window.location.href = `/workspace/projects/${projectId}/project_parameters`;
                    }
                }
            });
        });

        // Project Members Modal
        const membersBtn = document.querySelector('.manage-members-btn');
        if (membersBtn) {
            membersBtn.addEventListener('click', function(e) {
                e.preventDefault();

                // Close the dropdown
                const dropdown = this.closest('.project-actions-dropdown');
                if (dropdown) {
                    dropdown.classList.remove('active');
                }

                // Open the members modal
                const membersModal = document.getElementById('project-members-modal');
                if (membersModal) {
                    membersModal.classList.add('active');
                    membersModal.style.display = 'block';
                }
            });
        }

        // Room Creation Modal
        const addRoomBtn = document.getElementById('add-room-btn');
        if (addRoomBtn) {
            addRoomBtn.addEventListener('click', function() {
                const modal = document.getElementById('create-room-modal');
                if (modal) {
                    modal.style.display = 'flex';
                }
            });
        }

        // View Room History Button
        const historyButtons = document.querySelectorAll('.view-history-btn');
        historyButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                // Close dropdown
                const dropdown = this.closest('.project-actions-dropdown');
                if (dropdown) {
                    dropdown.classList.remove('active');
                }

                // Get selected room
                const roomId = sessionStorage.getItem('selectedRoom');
                const roomName = sessionStorage.getItem('selectedRoomName');

                if (!roomId || !roomName) {
                    alert('Veuillez sélectionner une pièce d\'abord');
                    return;
                }

                // Open history modal
                const historyModal = document.getElementById('room-history-modal');
                if (historyModal) {
                    // Update modal title
                    const titleElement = historyModal.querySelector('.room-history-title');
                    if (titleElement) {
                        titleElement.textContent = roomName;
                    }

                    // Show modal
                    historyModal.style.display = 'flex';
                    document.body.classList.add('modal-open');

                    // Load history data
                    loadRoomHistoryData(roomId, roomName);
                }
            });
        });
    }

    // Load room history data
    function loadRoomHistoryData(roomId, roomName) {
        const historyModal = document.getElementById('room-history-modal');
        if (!historyModal) return;

        // Show loading indicator
        const loadingEl = historyModal.querySelector('.loading-history');
        const tableEl = historyModal.querySelector('.history-table');
        const noHistoryEl = historyModal.querySelector('.no-history');

        if (loadingEl) loadingEl.style.display = 'block';
        if (tableEl) tableEl.style.display = 'none';
        if (noHistoryEl) noHistoryEl.style.display = 'none';

        // Extract project ID from the URL
        const urlParts = window.location.pathname.split('/');
        const projectsIndex = urlParts.indexOf('projects');
        let projectId = '';

        if (projectsIndex !== -1 && urlParts.length > projectsIndex + 1) {
            projectId = urlParts[projectsIndex + 1];
        }

        if (!projectId) {
            console.error('Could not extract project ID from URL');
            if (loadingEl) loadingEl.style.display = 'none';
            if (noHistoryEl) {
                noHistoryEl.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <h3>Erreur</h3>
                    <p>ID du projet non trouvé.</p>
                `;
                noHistoryEl.style.display = 'block';
            }
            return;
        }

        // Fetch room history from the server
        fetch(`/workspace/projects/${projectId}/rooms/${roomId}/history`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Hide loading indicator
                if (loadingEl) loadingEl.style.display = 'none';

                if (data.success && data.history && data.history.length > 0) {
                    // Populate table with history data
                    const tbody = tableEl.querySelector('tbody');
                    if (tbody) {
                        tbody.innerHTML = '';

                        data.history.forEach(item => {
                            const row = document.createElement('tr');

                            // Format the timestamp to a readable date/time
                            const date = new Date(item.timestamp);
                            const formattedDate = date.toLocaleString();

                            // Create cells
                            const dateCell = document.createElement('td');
                            dateCell.textContent = formattedDate;

                            const userCell = document.createElement('td');
                            userCell.textContent = item.user_name || 'Système';

                            const actionCell = document.createElement('td');
                            actionCell.textContent = item.action_type || 'Modification';

                            const detailsCell = document.createElement('td');
                            // Use pre element to preserve formatting of the details
                            const preElement = document.createElement('pre');
                            preElement.style.whiteSpace = 'pre-wrap';
                            preElement.style.fontFamily = 'inherit';
                            preElement.style.margin = '0';
                            preElement.textContent = item.details || '-';
                            detailsCell.appendChild(preElement);

                            // Add all cells to the row
                            row.appendChild(dateCell);
                            row.appendChild(userCell);
                            row.appendChild(actionCell);
                            row.appendChild(detailsCell);

                            tbody.appendChild(row);
                        });

                        if (tableEl) tableEl.style.display = 'table';
                    }
                } else {
                    // Show no history message
                    if (noHistoryEl) {
                        noHistoryEl.innerHTML = `
                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 2a10 10 0 1 0 10 10H12V2z"></path>
                                <path d="M12 2v10h10"></path>
                            </svg>
                            <h3>Aucun historique</h3>
                            <p>Aucune modification n'a été enregistrée pour cette pièce.</p>
                        `;
                        noHistoryEl.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching room history:', error);
                // Hide loading indicator
                if (loadingEl) loadingEl.style.display = 'none';
                // Show error message
                if (noHistoryEl) {
                    noHistoryEl.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="12"></line>
                            <line x1="12" y1="16" x2="12.01" y2="16"></line>
                        </svg>
                        <h3>Erreur</h3>
                        <p>Impossible de charger l'historique: ${error.message}</p>
                    `;
                    noHistoryEl.style.display = 'block';
                }
            });
    }

    // Initialize all components
    initDropdownHandlers();
    setupModalHandlers();

    // Add data-entity-type attribute to all entity history buttons
    document.querySelectorAll('.functionality-history-btn').forEach(btn => {
        // If the button already has a data-category attribute, use that
        let entityType = btn.getAttribute('data-category');

        // Otherwise, try to determine the entity type from the parent tab
        if (!entityType) {
            const tabContent = btn.closest('.tab-content');
            if (tabContent && tabContent.id) {
                entityType = tabContent.id.replace('tab-', '');
            }
        }

        if (entityType) {
            btn.setAttribute('data-entity-type', entityType);
        }
    });

    // Handle escape key to cancel edits and additions
    document.addEventListener("keydown", function(event) {
        if (event.key === "Escape") {
            // Handle canceling row additions
            const inputRow = document.querySelector(".input-row");
            if (inputRow) {
                inputRow.remove();
                console.log("➖ Ligne d'ajout annulée avec Escape");

                // Show add buttons
                document.querySelectorAll(".add-item-button").forEach(btn => {
                    btn.style.display = "inline-block";
                });
            }

            // Handle canceling row edits - this is handled in table_editors.js
        }
    });

    // Close modal buttons
    document.querySelectorAll('.close-modal-btn, .cancel-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                document.body.classList.remove('modal-open');
            }
        });
    });

    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        document.querySelectorAll('.modal').forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
                document.body.classList.remove('modal-open');
            }
        });
    });
});