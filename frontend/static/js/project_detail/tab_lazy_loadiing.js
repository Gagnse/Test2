// tab_lazy_loading.js - Place this file in your static/js/project_detail/ directory

document.addEventListener('DOMContentLoaded', function() {
    // Get the current project ID from the URL
    const pathParts = window.location.pathname.split('/');
    const projectId = pathParts[pathParts.indexOf('projects') + 1];

    // Track which tabs have already been loaded
    const loadedTabs = new Set();

    // Select all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');

    // Initialize tab click handlers
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
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

            // If this tab hasn't been loaded yet
            if (!loadedTabs.has(tabId) && tabContent) {
                // Add loading indicator
                tabContent.innerHTML = `
                    <div class="loading-indicator">
                        <div class="spinner"></div>
                        <p>Chargement des données...</p>
                    </div>
                `;

                // Make tab visible while loading
                tabContent.classList.add('active');

                // Fetch tab data from server
                fetchTabData(tabCategory, projectId, tabContent);

                // Mark this tab as loaded
                loadedTabs.add(tabId);
            } else if (tabContent) {
                // If already loaded, just show it
                tabContent.classList.add('active');
            }
        });
    });

    // Activate the first tab by default or the one from URL hash
    const hashTab = window.location.hash.substring(1);
    const tabToActivate = hashTab ?
        document.querySelector(`.tab-button[data-tab="tab-${hashTab}"]`) :
        document.querySelector('.tab-button');

    if (tabToActivate) {
        tabToActivate.click();
    }
});

function fetchTabData(category, projectId, tabContentElement) {
    const selectedRoomId = window.ProjectApp.data.selectedRoomId;

    // Construct the API URL
    let url = `/api/projects/${projectId}/tabs/${category}`;
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
            console.log(`Response status: ${response.status}`);

            // First check if response is OK
            if (!response.ok) {
                return response.text().then(text => {
                    console.error(`Error response text: ${text}`);
                    throw new Error(`Server error: ${response.status} ${response.statusText}`);
                });
            }

            // Then try to parse as JSON
            return response.text().then(text => {
                console.log("Response text:", text.substring(0, 200) + "..."); // Log first 200 chars
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.error("JSON parse error:", e);
                    console.error("Response was not valid JSON:", text);
                    throw new Error("Invalid JSON response from server");
                }
            });
        })
        .then(data => {
            console.log(`Tab data received for ${category}:`, data);

            if (!data) {
                throw new Error("Empty response data");
            }

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
                    <div>
                        <button class="retry-button" onclick="retryLoadTab('${category}', '${projectId}', this.parentElement.parentElement.parentElement)">Réessayer</button>
                    </div>
                    <p class="error-details">Details: ${error.stack || ''}</p>
                </div>
            `;
        });
}

// Function to render a regular table-based tab
function renderRegularTab(category, items, tabContentElement) {
    // Get column display configuration
    const columnsToDisplay = window.columnsToDisplay[category] || [];

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
                    <a href="#" class="functionality-history-btn" data-category="${category}">
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

    if (items && items.length > 0) {
        tabHtml += `<table>
            <thead>
                <tr>`;

        // Add header cells
        columnsToDisplay.forEach(key => {
            if (items[0][key] !== undefined) {
                const columnTitle = window.columnTitles ? window.columnTitles[key] : key;
                tabHtml += `
                    <th class="sortable" data-column="${key}" data-order="none">
                        ${columnTitle || key.replace('_', ' ')}
                        <span class="sort-icon">↕️</span>
                    </th>`;
            }
        });

        tabHtml += `<th>Actions</th></tr></thead><tbody>`;

        // Add table rows
        items.forEach(item => {
            const itemId = item[`${category}_id`];
            const roomId = item['room_id'] || '';
            const roomName = item['room_name'] || '';

            tabHtml += `
                <tr data-id="${itemId}" data-category="${category}" data-room-id="${roomId}" data-room-name="${roomName}">
                    <td style="display: none;">${roomId}</td>
                    <td style="display: none;">${roomName}</td>`;

            // Add data cells
            columnsToDisplay.forEach(key => {
                if (item[key] !== undefined) {
                    tabHtml += `<td contenteditable="false" data-key="${key}">${item[key]}</td>`;
                }
            });

            tabHtml += `
                <td>
                    <span class="edit-icon" title="Modifier">&#9998;</span>
                    <span class="delete-icon" title="Supprimer">&#128465;</span>
                </td>
                </tr>`;
        });

        tabHtml += `</tbody></table>`;
    } else {
        tabHtml += `<p>Aucune donnée disponible pour cet onglet.</p>`;
    }

    // Update the tab content
    tabContentElement.innerHTML = tabHtml;

    // Reinitialize event handlers for table actions
    initializeTableEvents(tabContentElement);
}

// Function to render special tabs (functionality, arch_requirements, etc.)
function renderSpecialTab(category, items, tabContentElement) {
    // For special tabs, we'll need to load their HTML templates
    fetch(`/api/templates/tabs/${category}?items=${encodeURIComponent(JSON.stringify(items))}`)
        .then(response => response.text())
        .then(html => {
            tabContentElement.innerHTML = html;

            // Initialize event handlers for special tabs
            initializeSpecialTabEvents(category, tabContentElement);
        })
        .catch(error => {
            console.error('Error loading special tab template:', error);
            tabContentElement.innerHTML = `
                <div class="error-message">
                    <p>Erreur lors du chargement du template: ${error.message}</p>
                </div>
            `;
        });
}

// Helper function to get tab title
function getTabTitle(category) {
    if (window.tabTitles && window.tabTitles[category]) {
        return window.tabTitles[category];
    }

    const tabTitles = {
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

    return tabTitles[category] || category.replace('_', ' ').charAt(0).toUpperCase() + category.replace('_', ' ').slice(1);
}

// Function to retry loading a tab
function retryLoadTab(category, projectId, tabContentElement) {
    fetchTabData(category, projectId, tabContentElement);
}

// Function to initialize table event handlers
function initializeTableEvents(container) {
    // Add click handlers for edit and delete icons
    container.querySelectorAll('.edit-icon').forEach(icon => {
        icon.addEventListener('click', function() {
            const row = this.closest('tr');
            if (window.ProjectApp.functions.startEditing) {
                window.ProjectApp.functions.startEditing(row);
            } else {
                console.warn("startEditing function not found in ProjectApp.functions");
            }
        });
    });

    container.querySelectorAll('.delete-icon').forEach(icon => {
        icon.addEventListener('click', function() {
            const row = this.closest('tr');
            if (window.ProjectApp.functions.deleteRow) {
                window.ProjectApp.functions.deleteRow(row);
            } else {
                console.warn("deleteRow function not found in ProjectApp.functions");
            }
        });
    });

    // Add click handler for add item button
    container.querySelectorAll('.add-item-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.getAttribute('data-category');
            if (window.ProjectApp.functions.addNewItem) {
                window.ProjectApp.functions.addNewItem(category);
            } else {
                console.warn("addNewItem function not found in ProjectApp.functions");
            }
        });
    });

    // Add handlers for table sorting
    container.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', function() {
            const column = this.getAttribute('data-column');
            const currentOrder = this.getAttribute('data-order');
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';

            // Update all headers
            container.querySelectorAll('th.sortable').forEach(header => {
                header.setAttribute('data-order', 'none');
            });

            // Set the new order on this header
            this.setAttribute('data-order', newOrder);

            // Sort the table
            sortTable(container.querySelector('table'), column, newOrder);
        });
    });
}

// Function to initialize special tab event handlers
function initializeSpecialTabEvents(category, container) {
    // Initialize dropdown toggles
    container.querySelectorAll('.dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const dropdown = this.nextElementSibling;
            dropdown.classList.toggle('active');

            // Close other open dropdowns
            container.querySelectorAll('.dropdown-menu.active').forEach(menu => {
                if (menu !== dropdown) {
                    menu.classList.remove('active');
                }
            });

            // Close when clicking outside
            document.addEventListener('click', function closeDropdown(e) {
                if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.classList.remove('active');
                    document.removeEventListener('click', closeDropdown);
                }
            });
        });
    });

    // Initialize edit button
    container.querySelectorAll('.edit-icon').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const roomId = container.querySelector(`form[data-room-id]`).getAttribute('data-room-id');

            if (window.ProjectApp.functions.editSpecialTab) {
                window.ProjectApp.functions.editSpecialTab(category, roomId);
            } else {
                console.warn(`editSpecialTab function not found for ${category}`);
            }
        });
    });

    // Initialize history button
    container.querySelectorAll('.functionality-history-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const roomId = container.querySelector(`form[data-room-id]`).getAttribute('data-room-id');

            if (window.ProjectApp.functions.openEntityHistory) {
                window.ProjectApp.functions.openEntityHistory(category, roomId);
            } else {
                console.warn(`openEntityHistory function not found for ${category}`);
            }
        });
    });
}

// Function to sort a table by column
function sortTable(table, column, order) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const tbody = table.querySelector('tbody');

    // Sort the rows
    rows.sort((a, b) => {
        const cellA = a.querySelector(`td[data-key="${column}"]`);
        const cellB = b.querySelector(`td[data-key="${column}"]`);

        if (!cellA || !cellB) return 0;

        const valueA = cellA.textContent.trim();
        const valueB = cellB.textContent.trim();

        // Try to convert to numbers for numeric sorting
        const numA = parseFloat(valueA);
        const numB = parseFloat(valueB);

        if (!isNaN(numA) && !isNaN(numB)) {
            return order === 'asc' ? numA - numB : numB - numA;
        }

        // Fall back to string comparison
        return order === 'asc'
            ? valueA.localeCompare(valueB)
            : valueB.localeCompare(valueA);
    });

    // Clear and repopulate the table
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    rows.forEach(row => tbody.appendChild(row));
}