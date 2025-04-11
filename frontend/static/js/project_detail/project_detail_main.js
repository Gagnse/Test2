/**
 * Main JavaScript for project_detail.html
 * Handles core functionality like tab switching, room selection, etc.
 */
document.addEventListener("DOMContentLoaded", function () {
    // Global variables for the selected room
    let selectedRoomId = "";
    let selectedRoomName = "";

    // Hide all + buttons on load
    document.querySelectorAll(".add-item-button").forEach(btn => {
        btn.style.display = "none";
    });

    // Managing opened/closed folders
    document.querySelectorAll(".folder-toggle").forEach(folder => {
        folder.addEventListener("click", function () {
            const nestedList = this.nextElementSibling;
            nestedList.style.display = nestedList.style.display === "block" ? "none" : "block";
            this.classList.toggle("open");
        });
    });

    // Select a room and show data
    document.querySelectorAll(".room-item").forEach(room => {
        room.addEventListener("click", function () {
            const roomId = this.getAttribute("data-room-id");
            const roomName = this.innerText.trim();

            // Update selection
            selectedRoomId = roomId;
            selectedRoomName = roomName;

            // Show name in "Salle sélectionnée :"
            document.querySelectorAll(".selected-room-name span").forEach(span => {
                span.textContent = roomName;
            });

            // CSS to show selection
            document.querySelectorAll(".room-item").forEach(r => r.classList.remove("selected"));
            this.classList.add("selected");

            // Show + buttons
            document.querySelectorAll(".add-item-button").forEach(btn => {
                btn.style.display = "inline-block";
            });
        });
    });

    // Tab switching functionality
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabContents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(button => {
        button.addEventListener("click", function () {
            tabButtons.forEach(btn => btn.classList.remove("active"));
            tabContents.forEach(content => content.classList.remove("active"));

            this.classList.add("active");
            document.getElementById(this.dataset.tab).classList.add("active");
        });
    });

    // Sort columns with arrows
    document.querySelectorAll(".sortable").forEach(header => {
        header.addEventListener("click", function () {
            const column = this.getAttribute("data-column");
            const table = this.closest("table");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));
            const currentOrder = this.dataset.order;

            let newOrder;
            if (currentOrder === "asc") {
                newOrder = "desc";
            } else {
                newOrder = "asc";
            }
            this.dataset.order = newOrder;

            // Determine if values are numeric or text
            const isNumeric = !isNaN(parseFloat(rows[0].querySelector(`[data-key='${column}']`)?.textContent));

            rows.sort((rowA, rowB) => {
                let a = rowA.querySelector(`[data-key='${column}']`)?.textContent.trim();
                let b = rowB.querySelector(`[data-key='${column}']`)?.textContent.trim();

                if (isNumeric) {
                    a = parseFloat(a);
                    b = parseFloat(b);
                } else {
                    a = a.toLowerCase();
                    b = b.toLowerCase();
                }

                return newOrder === "asc" ? (a > b ? 1 : -1) : (a < b ? 1 : -1);
            });

            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));

            // Update display of sort icons
            document.querySelectorAll(".sort-icon").forEach(icon => icon.textContent = "↕️");
            this.querySelector(".sort-icon").textContent = newOrder === "asc" ? "⬆️" : "⬇️";
        });
    });

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

    // Initialize the room info panel functionality
    document.addEventListener("DOMContentLoaded", function() {
        // Make sure the room info panel exists in the DOM
        if (!document.querySelector('.room-info-panel')) {
            console.error('Room info panel not found in the DOM');
            return;
        }

        // Get previously selected room from session storage
        const savedRoomId = sessionStorage.getItem("selectedRoom");
        const savedRoomName = sessionStorage.getItem("selectedRoomName");

        if (savedRoomId && savedRoomName) {
            updateRoomInfoPanel(savedRoomId, savedRoomName);
        }

        // Add event listeners to all room items to update the panel when clicked
        document.querySelectorAll(".room-item").forEach(room => {
            room.addEventListener("click", function() {
                const roomId = this.getAttribute("data-room-id");
                const roomName = this.innerText.trim();
                updateRoomInfoPanel(roomId, roomName);
            });
        });
    });

    // Initialize dropdown handlers
    document.addEventListener("DOMContentLoaded", function() {
        console.log("Initializing dropdown handlers...");

        // Clear any existing click handlers on dropdown toggles to avoid conflicts
        document.querySelectorAll(".dropdown-toggle").forEach(toggle => {
            const newToggle = toggle.cloneNode(true);
            toggle.parentNode.replaceChild(newToggle, toggle);
        });

        // Re-add click handlers to all dropdown toggles
        document.querySelectorAll(".dropdown-toggle").forEach(toggle => {
            console.log("Adding click handler to dropdown toggle", toggle);

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
                console.log("Dropdown active state:", dropdown.classList.contains('active'));
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
    });
});