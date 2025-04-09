document.addEventListener('DOMContentLoaded', function() {
    const entityHistoryModal = document.getElementById('entity-history-modal');
    const historyButtons = document.querySelectorAll('.functionality-history-btn');
    const closeButton = entityHistoryModal ? entityHistoryModal.querySelector('.close-modal-btn') : null;

    // Function to extract project ID from URL
    function getProjectIdFromUrl() {
        const urlParts = window.location.pathname.split('/');
        const projectsIndex = urlParts.indexOf('projects');
        if (projectsIndex !== -1 && urlParts.length > projectsIndex + 1) {
            return urlParts[projectsIndex + 1];
        }
        return null;
    }

    // Dictionary of entity type display names for fallback
    const entityTypeDisplayNames = {
        'functionality': 'Fonctionnalité',
        'arch_requirements': 'Exigences Architecturales',
        'struct_requirements': 'Exigences Structurelles',
        'risk_elements': 'Éléments à Risque',
        'ventilation_cvac': 'Ventilation CVAC',
        'electricity': 'Électricité',
        'interior_fenestration': 'Fenestration Intérieure',
        'exterior_fenestration': 'Fenestration Extérieure',
        'doors': 'Portes',
        'built_in_furniture': 'Mobilier Intégré',
        'accessories': 'Accessoires',
        'plumbings': 'Plomberie',
        'fire_protection': 'Protection Incendie',
        'lighting': 'Éclairage',
        'electrical_outlets': 'Prises Électriques',
        'communication_security': 'Communication & Sécurité',
        'medical_equipment': 'Équipements Médicaux'
    };

    // Function to open the history modal for a specific entity type
    function openEntityHistoryModal(entityType, roomId, roomName) {
        if (!entityHistoryModal) {
            console.error('Entity history modal not found in the DOM');
            return;
        }

        // Get the tab title from the active tab
        let tabTitle = '';

        // First try to get the title from the tab header of the currently active tab
        const activeTab = document.querySelector(`.tab-content.active`);
        if (activeTab) {
            const tabHeader = activeTab.querySelector('.tab-header h1, .tab-header h2');
            if (tabHeader) {
                tabTitle = tabHeader.textContent.trim();
            } else {
                // If no header in tab header, try to find the active tab button and get its text
                const activeTabId = activeTab.id;
                const activeTabButton = document.querySelector(`.tab-button[data-tab="${activeTabId}"]`);
                if (activeTabButton) {
                    tabTitle = activeTabButton.textContent.trim();
                }
            }
        }

        // If we still don't have a title, try another approach
        if (!tabTitle) {
            // Try getting title from the corresponding tab button
            const tabButton = document.querySelector(`.tab-button[data-tab="tab-${entityType}"]`);
            if (tabButton) {
                tabTitle = tabButton.textContent.trim();
            } else {
                // Use the fallback names from our dictionary
                tabTitle = entityTypeDisplayNames[entityType] || entityType;
            }
        }

        console.log("Using tab title:", tabTitle);

        // Update modal title with entity type and room name
        const typeElement = entityHistoryModal.querySelector('.entity-type-title');
        const titleElement = entityHistoryModal.querySelector('.entity-history-title');

        if (typeElement) {
            typeElement.textContent = tabTitle;
        }

        if (titleElement) {
            titleElement.textContent = roomName;
        }

        // Show the modal
        entityHistoryModal.style.display = 'flex';
        document.body.classList.add('modal-open');

        // Show loading indicator
        const loadingEl = entityHistoryModal.querySelector('.loading-history');
        const tableEl = entityHistoryModal.querySelector('.history-table');
        const noHistoryEl = entityHistoryModal.querySelector('.no-history');

        if (loadingEl) loadingEl.style.display = 'block';
        if (tableEl) tableEl.style.display = 'none';
        if (noHistoryEl) noHistoryEl.style.display = 'none';

        // Get the project ID
        const projectId = getProjectIdFromUrl();

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

        // Construct URL for fetching entity history
        // We pass the actual entity type as a query param
        const url = `/workspace/projects/${projectId}/entity_history/${entityType}?room_id=${roomId}&actual_entity_type=${entityType}`;

        console.log(`Fetching history from: ${url}`);

        // Fetch entity history from the server
        fetch(url)
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
                            <p>Aucune modification n'a été enregistrée pour cet élément de type ${tabTitle}.</p>
                        `;
                        noHistoryEl.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching entity history:', error);
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

    // Add click event listeners to all history buttons
    historyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent event from bubbling up

            // Close the dropdown
            const dropdown = this.closest('.project-actions-dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }

            // Get the entity type from the button's data attribute
            const entityType = this.getAttribute('data-entity-type') || 'functionality';

            // Get the current selected room info
            const roomId = sessionStorage.getItem('selectedRoom');
            const roomName = sessionStorage.getItem('selectedRoomName');

            if (!roomId || !roomName) {
                alert('Veuillez sélectionner une pièce d\'abord');
                return;
            }

            openEntityHistoryModal(entityType, roomId, roomName);
        });
    });

    // Close modal when close button is clicked
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            entityHistoryModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        });
    }

    // Close modal when clicking outside the modal content
    if (entityHistoryModal) {
        window.addEventListener('click', function(event) {
            if (event.target === entityHistoryModal) {
                entityHistoryModal.style.display = 'none';
                document.body.classList.remove('modal-open');
            }
        });
    }
});