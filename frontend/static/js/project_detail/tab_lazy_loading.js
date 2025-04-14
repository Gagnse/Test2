// Improved tab_lazy_loading.js - Fix naming and functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log("Tab lazy loading initialized");

    // Initialize the global namespace if not already done
    window.ProjectApp = window.ProjectApp || {
        data: {
            selectedRoomId: null,
            selectedRoomName: null,
            loadedTabs: new Set()
        },
        elements: {},
        functions: {}
    };

    // Get the current project ID from the URL
    const pathParts = window.location.pathname.split('/');
    const projectsIndex = pathParts.indexOf('projects');
    const projectId = projectsIndex >= 0 && pathParts.length > projectsIndex + 1
        ? pathParts[projectsIndex + 1]
        : null;

    console.log("Project ID:", projectId);

    // Store function for fetching tab data globally
    window.ProjectApp.functions.fetchTabData = function(category, tabElement) {
        fetchTabData(category, projectId, tabElement);
    };

    // Function to refresh the current active tab
    window.ProjectApp.functions.refreshActiveTab = function() {
        const activeTab = document.querySelector('.tab-button.active');
        if (activeTab) {
            activeTab.click();
        }
    };

    // Select all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');

    // Initialize tab click handlers
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            console.log("Tab clicked:", tabId);

            const tabCategory = tabId.replace('tab-', '');

            // Make all tabs inactive
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });

            // Make all buttons inactive
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
            });

            // Make the clicked button active
            this.classList.add('active');

            // Get the tab content element
            const tabContent = document.getElementById(tabId);
            if (!tabContent) {
                console.error(`Tab content element not found for ID: ${tabId}`);
                return;
            }

            // Always make the tab content visible
            tabContent.classList.add('active');

            // Check if we have a selected room
            const selectedRoomId = window.ProjectApp.data.selectedRoomId ||
                                  sessionStorage.getItem('selectedRoom');

            // If no room is selected yet, show a message
            if (!selectedRoomId) {
                tabContent.innerHTML = `
                    <div class="no-room-selected">
                        <p>Veuillez sélectionner une pièce dans le menu à gauche pour afficher les données.</p>
                    </div>
                `;
                return;
            }

            // Show loading indicator
            tabContent.innerHTML = `
                <div class="loading-indicator">
                    <div class="spinner"></div>
                    <p>Chargement des données...</p>
                </div>
            `;

            // Fetch tab data from server
            fetchTabData(tabCategory, projectId, tabContent);
        });
    });

    // Look for room selection events to trigger tab refresh
    document.querySelectorAll('.room-item').forEach(roomItem => {
        roomItem.addEventListener('click', function() {
            // When a room is selected, refresh the active tab
            setTimeout(() => {
                const activeTab = document.querySelector('.tab-button.active');
                if (activeTab) {
                    activeTab.click();
                }
            }, 100); // Small delay to ensure room selection is processed
        });
    });

    // Activate the first tab by default or the one from localStorage
    const savedTab = localStorage.getItem('activeTab');
    let tabToActivate;

    if (savedTab) {
        tabToActivate = document.querySelector(`.tab-button[data-tab="${savedTab}"]`);
    }

    if (!tabToActivate) {
        tabToActivate = document.querySelector('.tab-button');
    }

    if (tabToActivate) {
        console.log("Activating tab:", tabToActivate.getAttribute('data-tab'));
        tabToActivate.click();
    }
});

function fetchTabData(category, projectId, tabContentElement) {
    if (!projectId) {
        console.error("No project ID available for fetching tab data");
        tabContentElement.innerHTML = `
            <div class="error-message">
                <p>Erreur: Impossible de déterminer l'ID du projet.</p>
            </div>
        `;
        return;
    }

    const selectedRoomId = window.ProjectApp.data.selectedRoomId ||
                          sessionStorage.getItem('selectedRoom');

    if (!selectedRoomId) {
        console.warn("No room selected, cannot fetch tab data");
        return;
    }

    // Construct the API URL - CHANGED: Updated URL to match the backend route
    let url = `/workspace/api/projects/${projectId}/tabs/${category}`;
    if (selectedRoomId) {
        url += `?room_id=${selectedRoomId}`;
    }

    console.log(`Fetching tab data from: ${url}`);

    tabContentElement.innerHTML = `
        <div class="loading-indicator">
            <div class="spinner"></div>
            <p>Chargement des données...</p>
        </div>
    `;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Tab data received for ${category}:`, data);

            if (data.success) {
                if (['functionality', 'arch_requirements', 'struct_requirements',
                     'risk_elements', 'ventilation_cvac', 'electricity'].includes(category)) {
                    renderSpecialTab(category, data.items || [], tabContentElement);
                } else {
                    renderRegularTab(category, data.items || [], tabContentElement);
                }
            } else {
                throw new Error(data.message || 'Server reported error');
            }
        })
        .catch(error => {
            console.error('Error loading tab data:', error);
            tabContentElement.innerHTML = `
                <div class="error-message">
                    <p>Erreur lors du chargement des données: ${error.message}</p>
                    <button class="retry-button" onclick="window.ProjectApp.functions.fetchTabData('${category}', this.parentElement.parentElement)">
                        Réessayer
                    </button>
                </div>
            `;
        });
}

// Function to render a regular table-based tab
function renderRegularTab(category, items, tabContentElement) {
    // Get column display configuration
    const columnsToDisplay = window.columnsToDisplay?.[category] || [];

    // Create tab HTML
    let tabHtml = `
        <div class="tab-header">
            <h2>${getTabTitle(category)}</h2>
            <div class="project-actions-dropdown">
                <button class="dropdown-toggle">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="1"></circle>
                        <circle cx="12" cy="5" r="1"></circle>
                        <circle cx="12" cy="19" r="1"></circle>
                    </svg>
                </button>
                <div class="dropdown-menu">
                    <a href="#" class="add-item-button" data-category="${category}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        Ajouter un élément
                    </a>
                    <a href="#" class="entity-history-btn" data-category="${category}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2a10 10 0 1 0 10 10H12V2z"></path>
                            <path d="M12 2v10h10"></path>
                        </svg>
                        Historique
                    </a>
                </div>
            </div>
        </div>
    `;

    // Check if we have data and columns
    if (items && items.length > 0 && columnsToDisplay.length > 0) {
        tabHtml += `<div class="table-container"><table>
            <thead>
                <tr>`;

        // Add header cells
        columnsToDisplay.forEach(key => {
            const columnTitle = window.columnTitles?.[key] ||
                              key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

            tabHtml += `
                <th class="sortable" data-column="${key}" data-order="none">
                    ${columnTitle}
                    <span class="sort-icon">↕️</span>
                </th>`;
        });

        tabHtml += `<th>Actions</th></tr></thead><tbody>`;

        // Add table rows
        items.forEach(item => {
            const itemId = item[`${category}_id`] || '';
            const roomId = item['room_id'] || '';
            const roomName = item['room_name'] || '';

            tabHtml += `
                <tr data-id="${itemId}" data-category="${category}" data-room-id="${roomId}">`;

            // Add data cells
            columnsToDisplay.forEach(key => {
                let cellValue = '';

                if (item[key] !== undefined) {
                    if (Array.isArray(item[key])) {
                        cellValue = item[key].join(', ');
                    } else {
                        cellValue = item[key];
                    }
                }

                tabHtml += `<td data-key="${key}">${cellValue}</td>`;
            });

            tabHtml += `
                <td class="actions-cell">
                    <button class="edit-icon" title="Modifier">✎</button>
                    <button class="delete-icon" title="Supprimer">🗑️</button>
                </td>
                </tr>`;
        });

        tabHtml += `</tbody></table></div>`;
    } else {
        // If no data or no columns to display
        if (!items || items.length === 0) {
            tabHtml += `<p class="no-data-message">Aucune donnée disponible pour cet onglet.</p>`;
        } else if (columnsToDisplay.length === 0) {
            tabHtml += `<p class="no-data-message">Configuration des colonnes manquante pour cet onglet.</p>`;
        }
    }

    // Update the tab content
    tabContentElement.innerHTML = tabHtml;

    // Initialize event handlers for the table
    initializeTableActions(tabContentElement, category);
}

// Function to render special tabs with form structures
function renderSpecialTab(category, items, tabContentElement) {
    const selectedRoomId = window.ProjectApp.data.selectedRoomId ||
                          sessionStorage.getItem('selectedRoom');

    // Special tabs are loaded directly from server templates
    const urlParams = new URLSearchParams();
    urlParams.append('items', JSON.stringify(items));
    urlParams.append('room_id', selectedRoomId);

    const url = `/workspace/projects/${getProjectIdFromUrl()}/get_tab_template/${category}?${urlParams.toString()}`;

    console.log(`Loading special tab template from: ${url}`);

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Template fetch error: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            // Insert the HTML
            tabContentElement.innerHTML = html;

            // Initialize event handlers
            initializeSpecialTabEvents(tabContentElement, category);
        })
        .catch(error => {
            console.error(`Error loading template for ${category}:`, error);
            tabContentElement.innerHTML = `
                <div class="error-message">
                    <p>Erreur lors du chargement du template: ${error.message}</p>
                    <button class="retry-button" onclick="window.ProjectApp.functions.fetchTabData('${category}', this.parentElement.parentElement)">
                        Réessayer
                    </button>
                </div>
            `;
        });
}

// Helper function to get project ID from URL
function getProjectIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    const projectsIndex = pathParts.indexOf('projects');
    return projectsIndex >= 0 && pathParts.length > projectsIndex + 1
        ? pathParts[projectsIndex + 1]
        : null;
}

// Helper function to get tab title
function getTabTitle(category) {
    // First check window.tabTitles
    if (window.tabTitles && window.tabTitles[category]) {
        return window.tabTitles[category];
    }

    // Default titles if not found
    const defaultTitles = {
        "exterior_fenestration": "Fenestration Extérieure",
        "interior_fenestration": "Fenestration Intérieure",
        "doors": "Portes",
        "built_in_furniture": "Mobilier Intégré",
        "accessories": "Accessoires",
        "plumbings": "Plomberie",
        "fire_protection": "Protection Incendie",
        "lighting": "Éclairage",
        "electrical_outlets": "Prises Électriques",
        "communication_security": "Communication & Sécurité",
        "medical_equipment": "Équipements Médicaux",
        "functionality": "Fonctionnalité",
        "arch_requirements": "Exigences Architecturales",
        "struct_requirements": "Exigences Structurales",
        "risk_elements": "Éléments à Risque",
        "ventilation_cvac": "Ventilation CVAC",
        "electricity": "Électricité"
    };

    return defaultTitles[category] ||
        category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Initialize event handlers for the table
function initializeTableActions(container, category) {
    // Add event listeners for table sorting
    container.querySelectorAll('th.sortable').forEach(header => {
        header.addEventListener('click', function() {
            const table = container.querySelector('table');
            if (!table) return;

            const column = this.getAttribute('data-column');
            const currentOrder = this.getAttribute('data-order') || 'none';
            let newOrder = 'asc';

            if (currentOrder === 'asc') {
                newOrder = 'desc';
            }

            // Update all sort icons
            container.querySelectorAll('th.sortable').forEach(th => {
                th.setAttribute('data-order', 'none');
                const icon = th.querySelector('.sort-icon');
                if (icon) icon.textContent = '↕️';
            });

            // Update this header's sort icon
            this.setAttribute('data-order', newOrder);
            const icon = this.querySelector('.sort-icon');
            if (icon) icon.textContent = newOrder === 'asc' ? '↑' : '↓';

            // Sort the table
            sortTable(table, column, newOrder);
        });
    });

    // Add event listeners for edit/delete buttons
    container.querySelectorAll('.edit-icon').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = this.closest('tr');
            if (!row) return;

            // Enable contentEditable on all data cells
            row.querySelectorAll('td[data-key]').forEach(cell => {
                cell.setAttribute('contenteditable', 'true');
                cell.classList.add('editing');
            });

            // Change this button to a save button
            this.textContent = '✓';
            this.title = 'Enregistrer';
            this.classList.add('save-icon');
            this.classList.remove('edit-icon');
        });
    });

    // Add delegation for dynamically created save buttons
    container.addEventListener('click', function(e) {
        if (e.target.classList.contains('save-icon')) {
            e.preventDefault();

            const row = e.target.closest('tr');
            if (!row) return;

            const rowId = row.getAttribute('data-id');
            const category = row.getAttribute('data-category');

            // Collect updated data
            const updatedData = {};
            row.querySelectorAll('td[data-key]').forEach(cell => {
                const key = cell.getAttribute('data-key');
                updatedData[key] = cell.textContent.trim();
            });

            // Save the data
            saveRowData(rowId, category, updatedData, function(success) {
                if (success) {
                    // Disable contentEditable
                    row.querySelectorAll('td[data-key]').forEach(cell => {
                        cell.removeAttribute('contenteditable');
                        cell.classList.remove('editing');
                    });

                    // Change back to edit button
                    e.target.textContent = '✎';
                    e.target.title = 'Modifier';
                    e.target.classList.remove('save-icon');
                    e.target.classList.add('edit-icon');
                }
            });
        }
    });

    // Add event listeners for delete buttons
    container.querySelectorAll('.delete-icon').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = this.closest('tr');
            if (!row) return;

            const rowId = row.getAttribute('data-id');
            const category = row.getAttribute('data-category');

            if (confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
                deleteRowData(rowId, category, function(success) {
                    if (success) {
                        row.remove();
                    }
                });
            }
        });
    });

    // Add event listener for the dropdown toggle
    container.querySelectorAll('.dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const dropdown = this.closest('.project-actions-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('active');

                // Add a click outside listener to close the dropdown
                const closeDropdownListener = function(event) {
                    if (!dropdown.contains(event.target)) {
                        dropdown.classList.remove('active');
                        document.removeEventListener('click', closeDropdownListener);
                    }
                };

                // Start listening for clicks outside
                document.addEventListener('click', closeDropdownListener);
            }
        });
    });

    // Add event listener for add button
    container.querySelectorAll('.add-item-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const selectedRoomId = window.ProjectApp.data.selectedRoomId ||
                                  sessionStorage.getItem('selectedRoom');

            if (!selectedRoomId) {
                alert('Veuillez sélectionner une pièce avant d\'ajouter un élément.');
                return;
            }

            // Close dropdown
            const dropdown = this.closest('.dropdown-menu');
            if (dropdown) {
                dropdown.classList.remove('active');
            }

            // Get the columns for this category
            const columns = window.columnsToDisplay?.[category] || [];

            if (columns.length === 0) {
                alert('Impossible de créer un nouvel élément: configuration des colonnes manquante.');
                return;
            }

            // Create a new input row at the top of the table
            const tbody = container.querySelector('table tbody');
            if (!tbody) return;

            const newRow = document.createElement('tr');
            newRow.classList.add('input-row');
            newRow.setAttribute('data-category', category);

            let rowHtml = '';

            // Create input cells
            columns.forEach(column => {
                rowHtml += `
                    <td>
                        <input type="text" data-column="${column}" placeholder="${column}">
                    </td>
                `;
            });

            // Add action buttons
            rowHtml += `
                <td class="actions-cell">
                    <button class="confirm-add" title="Confirmer">✓</button>
                    <button class="cancel-add" title="Annuler">✗</button>
                </td>
            `;

            newRow.innerHTML = rowHtml;

            // Add to the top of the table
            if (tbody.firstChild) {
                tbody.insertBefore(newRow, tbody.firstChild);
            } else {
                tbody.appendChild(newRow);
            }

            // Focus the first input
            const firstInput = newRow.querySelector('input');
            if (firstInput) firstInput.focus();

            // Add event listeners for confirmation/cancellation
            newRow.querySelector('.confirm-add').addEventListener('click', function() {
                const newItemData = {};

                // Get values from all inputs
                newRow.querySelectorAll('input').forEach(input => {
                    const column = input.getAttribute('data-column');
                    newItemData[column] = input.value;
                });

                // Ensure room_id is set
                if (selectedRoomId) {
                    // Add the item
                    addNewItem(category, selectedRoomId, newItemData, function(success, newId) {
                        if (success) {
                            // Remove the input row
                            newRow.remove();

                            // Refresh the tab to show the new item
                            window.ProjectApp.functions.fetchTabData(category, container);
                        }
                    });
                }
            });

            newRow.querySelector('.cancel-add').addEventListener('click', function() {
                newRow.remove();
            });
        });
    });

    // Add history button handlers
    container.querySelectorAll('.entity-history-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const selectedRoomId = window.ProjectApp.data.selectedRoomId ||
                                  sessionStorage.getItem('selectedRoom');

            if (!selectedRoomId) {
                alert('Veuillez sélectionner une pièce pour voir l\'historique.');
                return;
            }

            // Get the category
            const categoryAttr = this.getAttribute('data-category');
            const category = categoryAttr || this.closest('[data-category]')?.getAttribute('data-category');

            if (!category) {
                console.error('Cannot determine category for history');
                return;
            }

            // Open entity history modal if available
            const entityHistoryModal = document.getElementById('entity-history-modal');
            if (entityHistoryModal) {
                // Update title
                const titleSpan = entityHistoryModal.querySelector('.entity-type-title');
                if (titleSpan) {
                    titleSpan.textContent = getTabTitle(category);
                }

                const roomNameSpan = entityHistoryModal.querySelector('.entity-history-title');
                if (roomNameSpan) {
                    roomNameSpan.textContent = sessionStorage.getItem('selectedRoomName') || 'Pièce';
                }

                // Show loading state
                entityHistoryModal.style.display = 'flex';
                const loadingElement = entityHistoryModal.querySelector('.loading-history');
                const tableElement = entityHistoryModal.querySelector('.history-table');
                const noHistoryElement = entityHistoryModal.querySelector('.no-history');

                if (loadingElement) loadingElement.style.display = 'block';
                if (tableElement) tableElement.style.display = 'none';
                if (noHistoryElement) noHistoryElement.style.display = 'none';

                // Close dropdown
                const dropdown = this.closest('.dropdown-menu');
                if (dropdown) {
                    dropdown.classList.remove('active');
                }

                // Fetch history data
                const projectId = getProjectIdFromUrl();

                if (projectId) {
                    fetch(`/workspace/projects/${projectId}/entity_history/${category}?room_id=${selectedRoomId}`)
                        .then(response => response.json())
                        .then(data => {
                            if (loadingElement) loadingElement.style.display = 'none';

                            if (data.success && data.history && data.history.length > 0) {
                                // Populate table
                                const tbody = tableElement.querySelector('tbody');
                                if (tbody) {
                                    tbody.innerHTML = '';

                                    data.history.forEach(item => {
                                        const row = document.createElement('tr');

                                        // Format date
                                        const date = new Date(item.timestamp);
                                        const formattedDate = date.toLocaleString();

                                        row.innerHTML = `
                                            <td>${formattedDate}</td>
                                            <td>${item.user_name || 'Système'}</td>
                                            <td>${item.action_type || 'Modification'}</td>
                                            <td><pre>${item.details || '-'}</pre></td>
                                        `;

                                        tbody.appendChild(row);
                                    });

                                    if (tableElement) tableElement.style.display = 'table';
                                }
                            } else {
                                // Show no history message
                                if (noHistoryElement) noHistoryElement.style.display = 'block';
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching history:', error);
                            if (loadingElement) loadingElement.style.display = 'none';
                            if (noHistoryElement) {
                                noHistoryElement.innerHTML = `
                                    <h3>Erreur</h3>
                                    <p>Impossible de charger l'historique: ${error.message}</p>
                                `;
                                noHistoryElement.style.display = 'block';
                            }
                        });
                }
            }
        });
    });
}

// Initialize events for special tabs
function initializeSpecialTabEvents(container, category) {
    // Delegate clicking on edit buttons
    container.querySelectorAll('.edit-icon').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            // Find the form for this tab
            const formSelector = `.${category}-form[style*="block"]`;
            const form = container.querySelector(formSelector) ||
                       container.querySelector('form');

            if (!form) {
                console.error(`Form not found for ${category}`);
                return;
            }

            // Enable all input fields
            form.querySelectorAll('input, textarea, select').forEach(field => {
                field.removeAttribute('disabled');
            });

            // Add a save button if not already present
            if (!form.querySelector('.save-button')) {
                const saveBtn = document.createElement('button');
                saveBtn.className = 'save-button';
                saveBtn.textContent = 'Enregistrer';
                saveBtn.style.marginTop = '10px';
                form.appendChild(saveBtn);

                // Add save handler
                saveBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    saveSpecialTabForm(form, category);
                });
            }
        });
    });

    // Delegate history button clicks
    container.querySelectorAll('.functionality-history-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const selectedRoomId = window.ProjectApp.data.selectedRoomId ||
                                  sessionStorage.getItem('selectedRoom');

            if (!selectedRoomId) {
                alert('Veuillez sélectionner une pièce pour voir l\'historique.');
                return;
            }

            // Open entity history modal
            const entityHistoryModal = document.getElementById('entity-history-modal');
            if (entityHistoryModal) {
                // Update title
                const titleSpan = entityHistoryModal.querySelector('.entity-type-title');
                if (titleSpan) {
                    titleSpan.textContent = getTabTitle(category);
                }

                const roomNameSpan = entityHistoryModal.querySelector('.entity-history-title');
                if (roomNameSpan) {
                    roomNameSpan.textContent = sessionStorage.getItem('selectedRoomName') || 'Pièce';
                }

                // Show modal
                entityHistoryModal.style.display = 'flex';

                // Show loading state
                const loadingElement = entityHistoryModal.querySelector('.loading-history');
                const tableElement = entityHistoryModal.querySelector('.history-table');
                const noHistoryElement = entityHistoryModal.querySelector('.no-history');

                if (loadingElement) loadingElement.style.display = 'block';
                if (tableElement) tableElement.style.display = 'none';
                if (noHistoryElement) noHistoryElement.style.display = 'none';

                // Fetch history data
                const projectId = getProjectIdFromUrl();

                if (projectId) {
                    fetch(`/workspace/projects/${projectId}/entity_history/${category}?room_id=${selectedRoomId}`)
                        .then(response => response.json())
                        .then(data => {
                            if (loadingElement) loadingElement.style.display = 'none';

                            if (data.success && data.history && data.history.length > 0) {
                                // Populate table
                                const tbody = tableElement.querySelector('tbody');
                                if (tbody) {
                                    tbody.innerHTML = '';

                                    data.history.forEach(item => {
                                        const row = document.createElement('tr');

                                        // Format date
                                        const date = new Date(item.timestamp);
                                        const formattedDate = date.toLocaleString();

                                        row.innerHTML = `
                                            <td>${formattedDate}</td>
                                            <td>${item.user_name || 'Système'}</td>
                                            <td>${item.action_type || 'Modification'}</td>
                                            <td><pre>${item.details || '-'}</pre></td>
                                        `;

                                        tbody.appendChild(row);
                                    });

                                    if (tableElement) tableElement.style.display = 'table';
                                }
                            } else {
                                // Show no history message
                                if (noHistoryElement) noHistoryElement.style.display = 'block';
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching history:', error);
                            if (loadingElement) loadingElement.style.display = 'none';
                            if (noHistoryElement) {
                                noHistoryElement.innerHTML = `
                                    <h3>Erreur</h3>
                                    <p>Impossible de charger l'historique: ${error.message}</p>
                                `;
                                noHistoryElement.style.display = 'block';
                            }
                        });
                }
            }
        });
    });

    // Initialize dropdown toggles
    container.querySelectorAll('.dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const dropdown = this.closest('.project-actions-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('active');

                // Close when clicking outside
                document.addEventListener('click', function closeDropdown(e) {
                    if (!dropdown.contains(e.target)) {
                        dropdown.classList.remove('active');
                        document.removeEventListener('click', closeDropdown);
                    }
                });
            }
        });
    });
}

// Function to save special tab form data
function saveSpecialTabForm(form, category) {
    const projectId = getProjectIdFromUrl();
    if (!projectId) {
        alert('Erreur: ID du projet non trouvé');
        return;
    }

    const roomId = form.getAttribute('data-room-id');
    if (!roomId) {
        alert('Erreur: ID de la pièce non trouvé');
        return;
    }

    // Collect form data based on the category
    const formData = collectFormData(form, category);

    // Show loading state
    const saveButton = form.querySelector('.save-button');
    if (saveButton) {
        saveButton.disabled = true;
        saveButton.textContent = 'Enregistrement...';
    }

    // Send data to server
    fetch(`/workspace/projects/${projectId}/edit_${category}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Modifications enregistrées !');

            // Disable form fields
            form.querySelectorAll('input, textarea, select').forEach(field => {
                field.setAttribute('disabled', 'disabled');
            });

            // Remove save button
            if (saveButton) {
                saveButton.remove();
            }
        } else {
            alert(`Erreur: ${data.message || 'Erreur inconnue'}`);
        }
    })
    .catch(error => {
        console.error('Error saving form:', error);
        alert(`Une erreur est survenue: ${error.message}`);
    })
    .finally(() => {
        // Reset button state
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.textContent = 'Enregistrer';
        }
    });
}

// Helper to collect form data based on the tab category
function collectFormData(form, category) {
    const formData = {
        room_id: form.getAttribute('data-room-id')
    };

    // Collect all checkboxes with the same name
    const checkboxGroups = new Map();

    // Process all form fields
    form.querySelectorAll('input, textarea, select').forEach(field => {
        // Handle checkbox groups
        if (field.type === 'checkbox') {
            const name = field.getAttribute('name');
            if (name) {
                if (!checkboxGroups.has(name)) {
                    checkboxGroups.set(name, []);
                }

                if (field.checked) {
                    checkboxGroups.get(name).push(field.value);
                }
            }
        }
        // Handle regular fields
        else if (field.id) {
            formData[field.id] = field.value;
        }
    });

    // Add checkbox groups to form data
    checkboxGroups.forEach((values, name) => {
        formData[name] = values;
    });

    return formData;
}

// Function to save a row after editing
function saveRowData(rowId, category, updatedData, callback) {
    const projectId = getProjectIdFromUrl();
    if (!projectId) {
        alert('Erreur: ID du projet non trouvé');
        if (callback) callback(false);
        return;
    }

    fetch(`/workspace/projects/${projectId}/edit_item`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: rowId,
            category: category,
            updatedData: updatedData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (callback) callback(true);
        } else {
            alert(`Erreur: ${data.message || 'Erreur inconnue'}`);
            if (callback) callback(false);
        }
    })
    .catch(error => {
        console.error('Error saving row:', error);
        alert(`Une erreur est survenue: ${error.message}`);
        if (callback) callback(false);
    });
}

// Function to delete a row
function deleteRowData(rowId, category, callback) {
    const projectId = getProjectIdFromUrl();
    if (!projectId) {
        alert('Erreur: ID du projet non trouvé');
        if (callback) callback(false);
        return;
    }

    fetch(`/workspace/projects/${projectId}/delete_item`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: rowId,
            category: category
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (callback) callback(true);
        } else {
            alert(`Erreur: ${data.message || 'Erreur inconnue'}`);
            if (callback) callback(false);
        }
    })
    .catch(error => {
        console.error('Error deleting row:', error);
        alert(`Une erreur est survenue: ${error.message}`);
        if (callback) callback(false);
    });
}

// Function to add a new item
function addNewItem(category, roomId, newData, callback) {
    const projectId = getProjectIdFromUrl();
    if (!projectId) {
        alert('Erreur: ID du projet non trouvé');
        if (callback) callback(false);
        return;
    }

    fetch(`/workspace/projects/${projectId}/add_item`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            category: category,
            room_id: roomId,
            new_data: newData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (callback) callback(true, data.id);
        } else {
            alert(`Erreur: ${data.message || 'Erreur inconnue'}`);
            if (callback) callback(false);
        }
    })
    .catch(error => {
        console.error('Error adding new item:', error);
        alert(`Une erreur est survenue: ${error.message}`);
        if (callback) callback(false);
    });
}

// Function to sort table rows
function sortTable(table, column, order) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    // Handle case of no rows or input row
    if (rows.length === 0) return;

    // Filter out input rows (they should stay at the top)
    const inputRows = rows.filter(row => row.classList.contains('input-row'));
    const dataRows = rows.filter(row => !row.classList.contains('input-row'));

    // Sort the data rows
    dataRows.sort((a, b) => {
        const cellA = a.querySelector(`td[data-key="${column}"]`);
        const cellB = b.querySelector(`td[data-key="${column}"]`);

        if (!cellA || !cellB) return 0;

        const valA = cellA.textContent.trim();
        const valB = cellB.textContent.trim();

        // Try numeric sort first
        const numA = parseFloat(valA);
        const numB = parseFloat(valB);

        if (!isNaN(numA) && !isNaN(numB)) {
            return order === 'asc' ? numA - numB : numB - numA;
        }

        // Fall back to string comparison
        return order === 'asc' ?
            valA.localeCompare(valB) :
            valB.localeCompare(valA);
    });

    // Clear the table
    tbody.innerHTML = '';

    // Add input rows first
    inputRows.forEach(row => tbody.appendChild(row));

    // Add sorted data rows
    dataRows.forEach(row => tbody.appendChild(row));
}