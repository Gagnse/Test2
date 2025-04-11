/**
 * Handles table editing functionality for the project detail page
 */
function initTableEditors() {
    const App = window.ProjectApp;

    // Click handler for edit and delete icons
    function setupTableRowActions() {
        document.addEventListener("click", function(event) {
            if (!event.target.classList.contains("edit-icon") &&
                !event.target.classList.contains("delete-icon")) {
                return;
            }

            const target = event.target;
            const row = target.closest("tr");

            if (!row) return;

            const rowId = row.getAttribute("data-id");
            const category = row.getAttribute("data-category");

            if (target.classList.contains("edit-icon")) {
                // Activate edition mode
                const cells = row.querySelectorAll("td[data-key]");
                cells.forEach(cell => cell.setAttribute("contenteditable", "true"));
                cells[0].focus(); // Focus on the first editable cell
            } else if (target.classList.contains("delete-icon")) {
                if (confirm("Voulez-vous vraiment supprimer cet élément ?")) {
                    const projectId = App.functions.getProjectIdFromUrl();

                    fetch(`/workspace/projects/${projectId}/delete_item`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({id: rowId, category})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert("Suppression réussie !");
                            row.remove();
                        } else {
                            alert("Erreur : " + data.message);
                        }
                    })
                    .catch(error => console.error("Erreur fetch :", error));
                }
            }
        });
    }

    // Save edited cells with Enter key
    function setupCellEditing() {
        document.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                const cell = event.target;
                if (cell.tagName === "TD" && cell.getAttribute("contenteditable") === "true") {
                    event.preventDefault();

                    const row = cell.closest("tr");
                    const rowId = row.getAttribute("data-id");
                    const category = row.getAttribute("data-category");
                    const projectId = App.functions.getProjectIdFromUrl();

                    // Get modified data
                    const updatedData = {};
                    updatedData[cell.getAttribute("data-key")] = cell.innerText.trim();

                    // Send update to the server
                    fetch(`/workspace/projects/${projectId}/edit_item`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({id: rowId, category, updatedData})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert("Modification enregistrée !");
                            const editableCells = row.querySelectorAll("td[contenteditable='true']");
                            editableCells.forEach(cell => {
                                cell.setAttribute("contenteditable", "false");
                            });
                        } else {
                            alert("Erreur : " + data.message);
                        }
                    })
                    .catch(error => console.error("Erreur fetch :", error));
                }
            }
        });
    }

    // Save original values when editing starts
    function setupOriginalValueTracking() {
        document.addEventListener("focusin", function(event) {
            const cell = event.target;
            if (cell.tagName === "TD" && cell.isContentEditable) {
                const row = cell.closest("tr");
                if (row && row !== App.data.editingRow) {
                    App.data.editingRow = row;
                    App.data.originalRowValues.clear();
                    row.querySelectorAll("td[data-key]").forEach(td => {
                        App.data.originalRowValues.set(td, td.innerText);
                    });
                }
            }
        });

        // Cancel editing with Escape
        document.addEventListener("keydown", function(event) {
            if (event.key === "Escape" && App.data.editingRow) {
                App.data.originalRowValues.forEach((val, td) => {
                    td.innerText = val;
                    td.setAttribute("contenteditable", "false");
                });
                App.data.originalRowValues.clear();
                App.data.editingRow = null;
                console.log("🔁 Édition annulée");
            }
        });
    }

    // Handle add item buttons
    function setupAddItemButtons() {
        document.querySelectorAll(".add-item-button").forEach(button => {
            button.addEventListener("click", function() {
                const category = this.dataset.category;
                const tabContent = document.getElementById(`tab-${category}`);
                const table = tabContent.querySelector("table tbody");

                // Retrieve columns from the window variable
                const columns = window.columnsToDisplay[category];

                if (!columns) {
                    alert("Colonnes inconnues pour cette catégorie");
                    return;
                }

                const roomId = App.data.selectedRoomId || sessionStorage.getItem("selectedRoom");
                if (!roomId) {
                    alert("Veuillez sélectionner une salle avant d'ajouter un élément.");
                    return;
                }

                // Create input row
                const row = document.createElement("tr");
                row.classList.add("input-row");

                row.innerHTML = columns.map(key => {
                    const labelMap = {
                        "category": "Catégorie",
                        "number": "Numéro",
                        "name": "Nom",
                        "quantity": "Quantité"
                    };
                    return `<td><input type="text" name="${key}" placeholder="${labelMap[key] || key}" /></td>`;
                }).join("");

                row.innerHTML += `
                    <td class="action-buttons">
                        <button class="confirm-add" title="Ajouter">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                        </button>
                        <button class="cancel-add" title="Annuler">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </td>
                `;

                table.prepend(row);

                // Hide all add buttons while adding an item
                document.querySelectorAll(".add-item-button").forEach(btn => {
                    btn.style.display = "none";
                });

                // Handle confirm button click
                row.querySelector(".confirm-add").addEventListener("click", function() {
                    const inputs = row.querySelectorAll("input");
                    const newData = {};
                    inputs.forEach(input => newData[input.name] = input.value);

                    const projectId = App.functions.getProjectIdFromUrl();

                    fetch(`/workspace/projects/${projectId}/add_item`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({
                            category,
                            room_id: roomId,
                            new_data: newData
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert("Ajout réussi !");

                            // Create new row with the data
                            const newRow = document.createElement("tr");
                            newRow.setAttribute("data-id", data.id);
                            newRow.setAttribute("data-category", category);
                            newRow.setAttribute("data-room-id", roomId);

                            // Add data cells
                            columns.forEach(key => {
                                newRow.innerHTML += `<td data-key="${key}">${newData[key] || ''}</td>`;
                            });

                            // Add action buttons
                            newRow.innerHTML += `
                                <td>
                                    <span class="edit-icon" title="Modifier">&#9998;</span>
                                    <span class="delete-icon" title="Supprimer">&#128465;</span>
                                </td>
                            `;

                            // Replace input row with new data row
                            row.replaceWith(newRow);

                            // Show add buttons again
                            document.querySelectorAll(".add-item-button").forEach(btn => {
                                btn.style.display = "inline-block";
                            });
                        } else {
                            alert("Erreur : " + data.message);
                        }
                    })
                    .catch(error => {
                        console.error("Error adding item:", error);
                        alert("Erreur lors de l'ajout de l'élément");

                        // Show add buttons again in case of error
                        document.querySelectorAll(".add-item-button").forEach(btn => {
                            btn.style.display = "inline-block";
                        });
                    });
                });

                // Handle cancel button click
                row.querySelector(".cancel-add").addEventListener("click", function() {
                    row.remove();

                    // Show add buttons again
                    document.querySelectorAll(".add-item-button").forEach(btn => {
                        btn.style.display = "inline-block";
                    });
                });
            });
        });
    }

    // Initialize all table editor functionality
    setupTableRowActions();
    setupCellEditing();
    setupOriginalValueTracking();
    setupAddItemButtons();
}