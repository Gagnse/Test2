/**
 * Handles modal interactions for the project detail page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Project Members Modal
    const membersModal = document.getElementById('project-members-modal');
    const manageMembersBtn = document.querySelector('.manage-members-btn');

    if (membersModal && manageMembersBtn) {
        manageMembersBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Close the dropdown menu if it's open
            const dropdown = document.querySelector('.project-actions-dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }

            // Open the members modal
            membersModal.classList.add('active');
            membersModal.style.display = 'block';
        });
    }

    // Set up the class for all buttons that should open the members modal
    document.querySelectorAll('.open-members-modal-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (membersModal) {
                membersModal.classList.add('active');
                membersModal.style.display = 'block';
            }
        });
    });

    // Project Parameters Modal
    const parametersButtons = document.querySelectorAll('.open-parameters-modal');

    parametersButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            // Close the dropdown menu if it's open
            const dropdown = document.querySelector('.project-actions-dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }

            // Open the parameters modal
            if (typeof window.openProjectParametersModal === 'function') {
                window.openProjectParametersModal();
            } else {
                console.error('openProjectParametersModal function not found');
                // Fallback to the old URL-based method
                window.location.href = `/workspace/projects/{{ project.id }}/project_parameters`;
            }
        });
    });

    // Check URL parameters to see if we should open the modal automatically
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('openModal') && urlParams.get('openModal') === 'parameters') {
        // Remove the parameter from the URL without refreshing the page
        const newUrl = window.location.pathname +
            window.location.search.replace(/[?&]openModal=parameters/, '').replace(/^&/, '?');
        window.history.replaceState({}, document.title, newUrl);

        // A small delay to ensure the modal is fully initialized
        setTimeout(() => {
            if (typeof window.openProjectParametersModal === 'function') {
                window.openProjectParametersModal();
            }
        }, 100);
    }

    // Room History Modal
    const historyModal = document.getElementById('room-history-modal');
    const historyButtons = document.querySelectorAll('.view-history-btn');
    const closeButton = historyModal ? historyModal.querySelector('.close-modal-btn') : null;

    // Function to open the history modal for a specific room
    function openHistoryModal(roomId, roomName) {
        if (!historyModal) return;

        // Update modal title with room name
        const titleElement = historyModal.querySelector('.room-history-title');
        if (titleElement) {
            titleElement.textContent = roomName;
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
                // Show no history message
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
    if (historyButtons) {
        historyButtons.forEach(button => {
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

                openHistoryModal(roomId, roomName);
            });
        });
    }

    // Close modal when close button is clicked
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            historyModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        });
    }

    // Close modal when clicking outside the modal content
    if (historyModal) {
        window.addEventListener('click', function(event) {
            if (event.target === historyModal) {
                historyModal.style.display = 'none';
                document.body.classList.remove('modal-open');
            }
        });
    }

    // Room Creation Modal
    const roomCreationModal = document.getElementById('create-room-modal');
    const addRoomBtn = document.getElementById('add-room-btn');
    const roomModalCloseButton = roomCreationModal ? roomCreationModal.querySelector('.close-modal-btn') : null;
    const roomModalCancelButton = roomCreationModal ? roomCreationModal.querySelector('.cancel-btn') : null;

    // Open modal when the add room button is clicked
    if (addRoomBtn && roomCreationModal) {
        addRoomBtn.addEventListener('click', function() {
            roomCreationModal.classList.add('active');
            roomCreationModal.style.display = 'flex';
        });
    }

    // Close modal when close button is clicked
    if (roomModalCloseButton) {
        roomModalCloseButton.addEventListener('click', function() {
            roomCreationModal.classList.remove('active');
            roomCreationModal.style.display = 'none';
        });
    }

    // Close modal when cancel button is clicked
    if (roomModalCancelButton) {
        roomModalCancelButton.addEventListener('click', function() {
            roomCreationModal.classList.remove('active');
            roomCreationModal.style.display = 'none';
        });
    }

    // Close modal when clicking outside the modal content
    if (roomCreationModal) {
        window.addEventListener('click', function(event) {
            if (event.target === roomCreationModal) {
                roomCreationModal.classList.remove('active');
                roomCreationModal.style.display = 'none';
            }
        });
    }
});