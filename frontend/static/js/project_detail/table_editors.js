/**
 * Handles table editing functionality for the project detail page
 */
document.addEventListener("DOMContentLoaded", function () {
    const tables = document.querySelectorAll("table");
    let editingRow = null;
    const originalRowValues = new Map();

    // Save original values when editing
    document.addEventListener("focusin", function (event) {
        const cell = event.target;
        if (cell.tagName === "TD" && cell.isContentEditable) {
            const row = cell.closest("tr");
            if (row && row !== editingRow) {
                editingRow = row;
                originalRowValues.clear();
                row.querySelectorAll("td[data-key]").forEach(td => {
                    originalRowValues.set(td, td.innerText);
                });
            }
        }
    });

    // ESCAPE to cancel modify mode for normal tabs
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && editingRow) {
            originalRowValues.forEach((val, td) => {
                td.innerText = val;
                td.setAttribute("contenteditable", "false");
            });
            originalRowValues.clear();
            editingRow = null;
            console.log("🔁 Édition annulée");
        }
    });

    // Handle edit and delete icons
    tables.forEach(table => {
        table.addEventListener("click", function (event) {
            const target = event.target;
            const row = target.closest("tr");

            if (!row) return;

            const rowId = row.getAttribute("data-id");
            const category = row.getAttribute("data-category");

            if (target.classList.contains("edit-icon")) {
                // Activate edition mode
                const cells = row.querySelectorAll("td[contenteditable]");
                cells.forEach(cell => cell.setAttribute("contenteditable", "true"));
                cells[0].focus(); // Focus on the first editable cell
            }

            if (target.classList.contains("delete-icon")) {
                if (confirm("Voulez-vous vraiment supprimer cet élément ?")) {
                    fetch(`/workspace/projects/{{ project.id }}/delete_item`, {
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
                        .catch(error => console.error(" Erreur fetch :", error));
                }
            }
        });

        // Detect the Enter key to save
        table.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();

                const cell = event.target;
                if (cell.getAttribute("contenteditable") === "true") {
                    const row = cell.closest("tr");
                    const rowId = row.getAttribute("data-id");
                    const category = row.getAttribute("data-category");

                    // Get modified data
                    const updatedData = {};
                    updatedData[cell.getAttribute("data-key")] = cell.innerText.trim();

                    // Send update to the server
                    fetch(`/workspace/projects/{{ project.id }}/edit_item`, {
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
                        .catch(error => console.error(" Erreur fetch :", error));
                }
            }
        });
    });

    // Handling + button to add row to a table
    document.querySelectorAll(".add-item-button").forEach(button => {
        button.addEventListener("click", function () {
            const category = this.dataset.category;
            const table = document.querySelector(`#tab-${category} table tbody`);

            // Retrieve columns from injected variable
            const columns = window.columnsToDisplay[category];

            if (!columns) {
                alert("Colonnes inconnues pour cette catégorie");
                return;
            }

            const roomId = sessionStorage.getItem("selectedRoom") || "";
            if (!roomId) {
                alert("Veuillez sélectionner une salle avant d'ajouter un élément.");
                return;
            }

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

            row.querySelector(".confirm-add").addEventListener("click", function () {
                const inputs = row.querySelectorAll("input");
                const newData = {};
                inputs.forEach(input => newData[input.name] = input.value);

                fetch(`/workspace/projects/{{ project.id }}/add_item`, {
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
                            const newRow = document.createElement("tr");
                            newRow.setAttribute("data-id", data.id);
                            newRow.setAttribute("data-category", category);
                            newRow.setAttribute("data-room-id", roomId);

                            columns.forEach(key => {
                                newRow.innerHTML += `<td data-key="${key}">${newData[key]}</td>`;
                            });
                            document.querySelectorAll(".add-item-button").forEach(btn => {
                              btn.style.display = "inline-flex";
                            });

                            newRow.innerHTML += `
                                <td>
                                    <span class="edit-icon" title="Modifier">&#9998;</span>
                                    <span class="delete-icon" title="Supprimer">&#128465;</span>
                                </td>
                            `;

                            row.replaceWith(newRow);
                        } else {
                            alert("Erreur : " + data.message);
                        }
                    });
            });

            const cancelAddition = function() {
                row.remove();
                // Make sure the add button is still visible and enabled
                document.querySelectorAll(".add-item-button").forEach(btn => {
                  btn.style.display = "inline-flex";
                });
            };

            row.querySelector(".cancel-add").addEventListener("click", cancelAddition);
        });
    });
});