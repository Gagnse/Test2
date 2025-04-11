/**
 * Handles the entity history modal functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    const historyModal = document.getElementById('entity-history-modal');

    // If the modal doesn't exist, exit early
    if (!historyModal) {
        console.error('Entity history modal not found in the DOM');
        return;
    }

    const closeButton = historyModal.querySelector('.close-modal-btn');

    // Function to open the history modal for a specific entity type
    function openEntityHistoryModal(entityType, roomId, roomName) {
        // Map tab IDs to proper entity types for the database
        const entityTypeMap = {
            'interior_fenestration': 'interior_fenestration',
            'exterior_fenestration': 'exterior_fenestration',
            'doors': 'doors',
            'built_in_furniture': 'built_in_furniture',
            'accessories': 'accessories',
            'plumbings': 'plumbings',
            'fire_protection': 'fire_protection',
            'lighting': 'lighting',
            'electrical_outlets': 'electrical_outlets',
            'communication_security': 'communication_security',
            'medical_equipment': 'medical_equipment',
            'functionality': 'functionality',
            'arch_requirements': 'arch_requirements',
            'struct_requirements': 'struct_requirements',
            'risk_elements': 'risk_elements',
            'ventilation_cvac': 'ventilation_cvac',
            'electricity': 'electricity'
        };

        // Map database entity types to display names
        const entityDisplayNames = {
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
            'medical_equipment': 'Équipements Médicaux',
            'functionality': 'Fonctionnalité',
            'arch_requirements': 'Exigences Architecturales',
            'struct_requirements': 'Exigences Structurales',
            'risk_elements': 'Éléments à Risque',
            'ventilation_cvac': 'Ventilation CVAC',
            'electricity': 'Électricité'
        };

        // Get the actual entity type for the database query
        const actualEntityType = entityTypeMap[entityType] || entityType;

        // Get the display name for the entity type
        const entityDisplayName = entityDisplayNames[actualEntityType] || entityType;

        // Update modal title with entity type and room name
        const entityTitleElement = historyModal.querySelector('.entity-type-title');
        const roomTitleElement = historyModal.querySelector('.entity-history-title');

        if (entityTitleElement) {
            entityTitleElement.textContent = entityDisplayName;
        }

        if (roomTitleElement) {
            roomTitleElement.textContent = roomName;
        }

        // Show the modal
        historyModal.style.display = 'flex';
        document.body.classList.add('modal-open');

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

        // Fetch entity history from the server
        // Add the entity_type as a query parameter
        fetch(`/workspace/projects/${projectId}/entity_history/${actualEntityType}?room_id=${roomId}`)
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
                            <p>Aucune modification n'a été enregistrée pour cet élément de type ${entityDisplayName}.</p>
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
    document.querySelectorAll('.functionality-history-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent event from bubbling up

            // Close the dropdown
            const dropdown = this.closest('.project-actions-dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }

            // Get the current selected room info
            const roomId = sessionStorage.getItem('selectedRoom');
            const roomName = sessionStorage.getItem('selectedRoomName');

            if (!roomId || !roomName) {
                alert('Veuillez sélectionner une pièce d\'abord');
                return;
            }

            // Determine which entity type to show history for
            let entityType;

            // First try to get it from the data-entity-type attribute if it exists
            if (this.hasAttribute('data-entity-type')) {
                entityType = this.getAttribute('data-entity-type');
            }
            // Otherwise, try to get it from data-category
            else if (this.hasAttribute('data-category')) {
                entityType = this.getAttribute('data-category');
            }
            // If still not found, look at the tab ID from the parent
            else {
                const tabContent = this.closest('.tab-content');
                if (tabContent && tabContent.id) {
                    entityType = tabContent.id.replace('tab-', '');
                } else {
                    // Last resort: get the active tab
                    const activeTab = document.querySelector('.tab-content.active');
                    if (activeTab && activeTab.id) {
                        entityType = activeTab.id.replace('tab-', '');
                    } else {
                        entityType = 'functionality'; // Default fallback
                    }
                }
            }

            console.log(`Opening history modal for entity type: ${entityType}`);
            openEntityHistoryModal(entityType, roomId, roomName);
        });
    });

    // Close modal when close button is clicked
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            historyModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        });
    }

    // Close modal when clicking outside the modal content
    window.addEventListener('click', function(event) {
        if (event.target === historyModal) {
            historyModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    });
});