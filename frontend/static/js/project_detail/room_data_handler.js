/**
 * Handles room data operations for the project detail page
 */
document.addEventListener("DOMContentLoaded", function () {
    const roomItems = document.querySelectorAll(".room-item");
    const tabContents = document.querySelectorAll(".tab-content");
    const selectedRoomNames = document.querySelectorAll(".selected-room-name span");

    // Function to filter table rows by room
    function filterRoomData(roomId) {
        tabContents.forEach(tab => {
            const rows = tab.querySelectorAll("tbody tr");
            rows.forEach(row => {
                const rowRoomId = row.getAttribute("data-room-id");
                row.style.display = (rowRoomId === roomId) ? "" : "none";
            });
        });
    }

    // Function to get functionality form for functionality tab
    function showFunctionalityForRoom(roomId) {
        const allForms = document.querySelectorAll(".functionality-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    }

    // Function to get arch requirements form for arch requirements tab
    function showArchRequirementsForRoom(roomId) {
        const allForms = document.querySelectorAll(".arch_requirements-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    }

    // Function to get struct requirements form
    function showStructRequirementsForRoom(roomId) {
        const allForms = document.querySelectorAll(".struct-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    }

    // Function to get risk elements form
    function showRiskElementsForRoom(roomId) {
        const allForms = document.querySelectorAll(".risk-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    }

    // Function to get ventilation cvac form
    function showVentilationForRoom(roomId) {
        const allForms = document.querySelectorAll(".ventilation-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    }

    // Function to get electricity form
    function showElectricityForRoom(roomId) {
        const allForms = document.querySelectorAll(".electricity-form");
        allForms.forEach(form => {
            form.style.display = (form.dataset.roomId === roomId) ? "block" : "none";
        });
    }

    // On click on a room in the left tree menu
    roomItems.forEach(room => {
        room.addEventListener("click", function () {
            const roomId = this.getAttribute("data-room-id");
            const roomName = this.innerText.trim();

            // Update display
            document.querySelectorAll(".room-item").forEach(item => item.classList.remove("active-room"));
            this.classList.add("active-room");

            // Store in session
            sessionStorage.setItem("selectedRoom", roomId);
            sessionStorage.setItem("selectedRoomName", roomName);

            // Display room name
            selectedRoomNames.forEach(span => {
                span.textContent = roomName;
            });

            // Filter tables and display appropriate forms
            filterRoomData(roomId);
            showFunctionalityForRoom(roomId);
            showArchRequirementsForRoom(roomId);
            showStructRequirementsForRoom(roomId);
            showRiskElementsForRoom(roomId);
            showVentilationForRoom(roomId);
            showElectricityForRoom(roomId);
        });
    });

    // On page load, reload filters/form if a room is selected
    const savedRoomId = sessionStorage.getItem("selectedRoom");
    const savedRoomName = sessionStorage.getItem("selectedRoomName");

    if (savedRoomId) {
        // Apply active class to the selected room
        const selectedRoomItem = document.querySelector(`.room-item[data-room-id="${savedRoomId}"]`);
        if (selectedRoomItem) {
            selectedRoomItem.classList.add("active-room");

            // Make sure parent folders are open
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

        // Update room name display
        selectedRoomNames.forEach(span => {
            span.textContent = savedRoomName;
        });

        // Apply filters and show appropriate forms
        filterRoomData(savedRoomId);
        showFunctionalityForRoom(savedRoomId);
        showArchRequirementsForRoom(savedRoomId);
        showStructRequirementsForRoom(savedRoomId);
        showRiskElementsForRoom(savedRoomId);
        showVentilationForRoom(savedRoomId);
        showElectricityForRoom(savedRoomId);
    }

    // Handle escape key to cancel additions/edits
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            const inputRow = document.querySelector(".input-row");
            if (inputRow) {
                inputRow.remove();
                console.log("➖ Ligne d'ajout annulée avec Escape");

                // Display + button
                document.querySelectorAll(".add-item-button").forEach(btn => {
                    btn.style.display = "inline-block";
                });
            }
        }
    });
});