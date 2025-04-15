/**
 * Handles room data operations for the project detail page
 */
function initRoomDataHandlers() {
    const App = window.ProjectApp;

    // Cache for storing loaded room data
    App.data.roomDataCache = {};

    // Filter table data by room ID
    App.functions.filterRoomData = function(roomId) {
        App.elements.tabContents.forEach(tab => {
            const rows = tab.querySelectorAll("tbody tr");
            rows.forEach(row => {
                const rowRoomId = row.getAttribute("data-room-id");
                row.style.display = (rowRoomId === roomId) ? "" : "none";
            });
        });
    };

    // Show loading indicators for tables
    App.functions.showTableLoadingIndicators = function() {
        App.elements.tabContents.forEach(tab => {
            const tableBody = tab.querySelector("tbody");
            if (tableBody) {
                const loadingRow = document.createElement("tr");
                loadingRow.className = "loading-indicator-row";
                loadingRow.innerHTML = `
                    <td colspan="100%" class="loading-indicator">
                        <div class="loading-spinner"></div>
                        <span>Chargement des données...</span>
                    </td>
                `;

                // Remove any existing loading indicators first
                const existingIndicators = tableBody.querySelectorAll(".loading-indicator-row");
                existingIndicators.forEach(indicator => indicator.remove());

                tableBody.appendChild(loadingRow);
            }
        });
    };

    // Remove all loading indicators
    App.functions.removeLoadingIndicators = function() {
        document.querySelectorAll(".loading-indicator-row").forEach(indicator => {
            indicator.remove();
        });
    };

    // Function to load room data from the server
    App.functions.loadRoomData = function(roomId, roomName) {
        // If we already have this room's data in cache, use it
        if (App.data.roomDataCache[roomId]) {
            console.log(`Using cached data for room ${roomId}`);
            App.functions.updateRoomTables(App.data.roomDataCache[roomId]);
            return Promise.resolve();
        }

        // Show loading indicators
        App.functions.showTableLoadingIndicators();

        // Get project ID from URL
        const projectId = App.functions.getProjectIdFromUrl();
        if (!projectId) {
            console.error("Could not extract project ID from URL");
            return Promise.reject("Project ID not found");
        }

        // Fetch room data from the server
        return fetch(`/workspace/api/projects/${projectId}/room_data/${roomId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error fetching room data: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Cache the room data
                    App.data.roomDataCache[roomId] = data.room_data;

                    // Update tables with the fetched data
                    App.functions.updateRoomTables(data.room_data);
                } else {
                    throw new Error(data.message || "Unknown error");
                }
            })
            .catch(error => {
                console.error("Error loading room data:", error);
                // Show error message
                window.toast && window.toast.error(`Erreur de chargement des données: ${error.message}`);
            })
            .finally(() => {
                // Remove loading indicators
                App.functions.removeLoadingIndicators();
            });
    };

    // Update table content with room data
    App.functions.updateRoomTables = function(roomData) {
        // Clear existing table data first
        App.elements.tabContents.forEach(tab => {
            const categoryMatch = tab.id.match(/tab-(\w+)/);
            if (categoryMatch) {
                const category = categoryMatch[1];
                const tableBody = tab.querySelector("tbody");

                if (tableBody) {
                    // Remove all rows except loading indicators
                    Array.from(tableBody.children).forEach(child => {
                        if (!child.classList.contains("loading-indicator-row")) {
                            child.remove();
                        }
                    });

                    // Add new rows based on the data
                    if (roomData[category] && roomData[category].length) {
                        const columns = window.columnsToDisplay[category];

                        roomData[category].forEach(item => {
                            const row = document.createElement("tr");
                            row.setAttribute("data-id", item[`${category}_id`]);
                            row.setAttribute("data-category", category);
                            row.setAttribute("data-room-id", item.room_id);
                            row.setAttribute("data-room-name", item.room_name);

                            // Add hidden cells for room_id and room_name
                            row.innerHTML = `
                                <td style="display: none;">${item.room_id || ''}</td>
                                <td style="display: none;">${item.room_name || ''}</td>
                            `;

                            // Add data cells
                            columns.forEach(key => {
                                const cell = document.createElement("td");
                                cell.setAttribute("data-key", key);
                                cell.setAttribute("contenteditable", "false");
                                cell.textContent = item[key] || '';
                                row.appendChild(cell);
                            });

                            // Add action buttons
                            const actionsCell = document.createElement("td");
                            actionsCell.innerHTML = `
                                <span class="edit-icon" title="Modifier">&#9998;</span>
                                <span class="delete-icon" title="Supprimer">&#128465;</span>
                            `;
                            row.appendChild(actionsCell);

                            tableBody.appendChild(row);
                        });
                    }
                }
            }
        });
    };

    // Show forms for special tabs based on selected room
    App.functions.showFunctionalityForRoom = function(roomId) {
        const allForms = document.querySelectorAll(".functionality-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    };

    App.functions.showArchRequirementsForRoom = function(roomId) {
        const allForms = document.querySelectorAll(".arch_requirements-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    };

    App.functions.showStructRequirementsForRoom = function(roomId) {
        const allForms = document.querySelectorAll(".struct-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    };

    App.functions.showRiskElementsForRoom = function(roomId) {
        const allForms = document.querySelectorAll(".risk-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    };

    App.functions.showVentilationForRoom = function(roomId) {
        const allForms = document.querySelectorAll(".ventilation-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    };

    App.functions.showElectricityForRoom = function(roomId) {
        const allForms = document.querySelectorAll(".electricity-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    };

    // Update room info panel
    App.functions.updateRoomInfoPanel = function(roomId, roomName) {
        const roomInfoPanel = App.elements.roomInfoPanel;
        if (!roomInfoPanel) return;

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
    };

    // Initialize room selection
    function initRoomSelection() {
        App.elements.roomItems.forEach(room => {
            room.addEventListener("click", function() {
                const roomId = this.getAttribute("data-room-id");
                const roomName = this.innerText.trim();

                // Update selection
                App.data.selectedRoomId = roomId;
                App.data.selectedRoomName = roomName;

                // Store in session storage for persistence
                sessionStorage.setItem("selectedRoom", roomId);
                sessionStorage.setItem("selectedRoomName", roomName);

                // Update room display
                document.querySelectorAll(".selected-room-title").forEach(span => {
                    span.textContent = roomName;
                });

                // CSS to show selection
                document.querySelectorAll(".room-item").forEach(r => r.classList.remove("active-room"));
                this.classList.add("active-room");

                // Update room info panel
                App.functions.updateRoomInfoPanel(roomId, roomName);

                // Show add buttons
                document.querySelectorAll(".add-item-button").forEach(btn => {
                    btn.style.display = "inline-block";
                });

                // Load room data on demand
                App.functions.loadRoomData(roomId, roomName)
                    .then(() => {
                        // Filter table data and show appropriate forms
                        App.functions.filterRoomData(roomId);
                        App.functions.showFunctionalityForRoom(roomId);
                        App.functions.showArchRequirementsForRoom(roomId);
                        App.functions.showStructRequirementsForRoom(roomId);
                        App.functions.showRiskElementsForRoom(roomId);
                        App.functions.showVentilationForRoom(roomId);
                        App.functions.showElectricityForRoom(roomId);
                    });
            });
        });
    }

    // Restore previously selected room
    function restoreSelectedRoom() {
        const savedRoomId = sessionStorage.getItem("selectedRoom");
        const savedRoomName = sessionStorage.getItem("selectedRoomName");

        if (savedRoomId && savedRoomName) {
            // Update app data
            App.data.selectedRoomId = savedRoomId;
            App.data.selectedRoomName = savedRoomName;

            // Show room info panel
            if (App.elements.roomInfoPanel) {
                App.elements.roomInfoPanel.style.display = 'block';
            }

            // Find and highlight the room in sidebar
            const selectedRoomItem = document.querySelector(`.room-item[data-room-id="${savedRoomId}"]`);
            if (selectedRoomItem) {
                selectedRoomItem.classList.add("active-room");

                // Open parent folders
                let parent = selectedRoomItem.parentElement;
                while (parent) {
                    if (parent.classList.contains("nested")) {
                        parent.classList.add("active");
                        const toggle = parent.previousElementSibling;
                        if (toggle && toggle.classList.contains("toggle")) {
                            toggle.classList.add("open");
                        }
                    }
                    parent = parent.parentElement;
                }
            }

            // Update room details
            document.querySelectorAll(".selected-room-title").forEach(span => {
                span.textContent = savedRoomName;
            });

            // Update room info panel
            App.functions.updateRoomInfoPanel(savedRoomId, savedRoomName);

            // Load room data on demand
            App.functions.loadRoomData(savedRoomId, savedRoomName)
                .then(() => {
                    // Filter tables and show appropriate forms
                    App.functions.filterRoomData(savedRoomId);
                    App.functions.showFunctionalityForRoom(savedRoomId);
                    App.functions.showArchRequirementsForRoom(savedRoomId);
                    App.functions.showStructRequirementsForRoom(savedRoomId);
                    App.functions.showRiskElementsForRoom(savedRoomId);
                    App.functions.showVentilationForRoom(savedRoomId);
                    App.functions.showElectricityForRoom(savedRoomId);

                    // Show add buttons
                    document.querySelectorAll(".add-item-button").forEach(btn => {
                        btn.style.display = "inline-block";
                    });
                });
        }
    }

    // Initialize room handlers
    initRoomSelection();
    restoreSelectedRoom();
}

