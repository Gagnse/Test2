// Function to initialize the delete confirmation modal
function initDeleteConfirmationModal() {
    console.log("Initializing delete confirmation modal");

    // Get modal elements
    const modal = document.getElementById('delete-confirmation-modal');
    const closeButton = modal.querySelector('.close-modal-btn');
    const cancelButton = modal.querySelector('.cancel-delete-btn');
    const confirmButton = modal.querySelector('.confirm-delete-btn');
    const userIdInput = document.getElementById('delete-user-id');
    const orgIdInput = document.getElementById('delete-org-id');

    // Close modal when close button is clicked
    closeButton.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    // Close modal when cancel button is clicked
    cancelButton.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    // Close modal when clicking outside the modal content
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });

    // Handle confirmation button click
    confirmButton.addEventListener('click', () => {
        const userId = userIdInput.value;
        const orgId = orgIdInput.value;

        if (!userId || !orgId) {
            console.error("Missing userId or orgId for delete operation");
            if (window.toast) {
                window.toast.error("Erreur: Informations manquantes pour la suppression");
            }
            return;
        }

        // Show loading state
        const buttonText = confirmButton.querySelector('.btn-text');
        const buttonSpinner = confirmButton.querySelector('.btn-spinner');
        confirmButton.disabled = true;
        buttonText.style.display = 'none';
        buttonSpinner.style.display = 'inline-block';

        // Call the delete API
        performDeleteUser(userId, orgId)
            .then(() => {
                // Success already handled in the function
                // Just close the modal
                modal.classList.remove('active');
            })
            .catch(error => {
                // Error already handled in the function
                // Reset button state
                confirmButton.disabled = false;
                buttonText.style.display = 'inline';
                buttonSpinner.style.display = 'none';
            });
    });

    // Set up delete buttons
    setupDeleteButtons();

    console.log("Delete confirmation modal initialized");
}

// Function to set up delete buttons
function setupDeleteButtons() {
    // Get organization ID
    const orgContainer = document.querySelector('.organisation-container');
    if (!orgContainer) {
        console.error("Organisation container not found!");
        return;
    }

    const organizationId = orgContainer.getAttribute('data-org-id');
    if (!organizationId) {
        console.error('Organization ID not found! Make sure to add data-org-id attribute to the container.');
        return;
    }

    // Get all delete buttons
    const deleteButtons = document.querySelectorAll('.delete-btn');
    console.log(`Found ${deleteButtons.length} delete buttons`);

    // Set up click event for each delete button
    deleteButtons.forEach((btn, index) => {
        const userId = btn.getAttribute('data-id');
        console.log(`Setting up delete button ${index + 1}: userId = ${userId}`);

        // Remove any existing event listeners
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);

        // Add our new event listener
        newBtn.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();

            if (!userId) {
                console.error("No user ID found on button");
                if (window.toast) {
                    window.toast.error("Erreur: ID utilisateur manquant");
                }
                return;
            }

            // Show the confirmation modal
            showDeleteConfirmationModal(userId, organizationId);
        });
    });
}

// Function to show the delete confirmation modal
function showDeleteConfirmationModal(userId, orgId) {
    console.log(`Showing delete confirmation modal for user ${userId} in org ${orgId}`);

    // Set the user ID and org ID in the hidden fields
    document.getElementById('delete-user-id').value = userId;
    document.getElementById('delete-org-id').value = orgId;

    // Get user name if available
    let userName = "ce membre";
    const row = document.querySelector(`.delete-btn[data-id="${userId}"]`)?.closest('tr');
    if (row) {
        const firstNameCell = row.cells[1]; // Adjust based on your table structure
        const lastNameCell = row.cells[0];  // Adjust based on your table structure

        if (firstNameCell && lastNameCell) {
            userName = `${firstNameCell.textContent.trim()} ${lastNameCell.textContent.trim()}`;
        }
    }

    // Set message with user name
    document.getElementById('delete-confirmation-message').textContent =
        `Êtes-vous sûr de vouloir supprimer ${userName} de l'organisation ?`;

    // Show the modal
    const modal = document.getElementById('delete-confirmation-modal');
    modal.classList.add('active');
}

// Function to perform the actual delete operation
async function performDeleteUser(userId, orgId) {
    console.log(`Performing delete for user ${userId} from organization ${orgId}`);

    // Show loading toast if available
    if (window.toast) {
        window.toast.info('Suppression en cours...');
    }

    try {
        // Make the API request
        const response = await fetch(`/api/organisations/${orgId}/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });

        // Parse the response
        const data = await response.json();
        console.log("API response:", data);

        // Check if the request was successful
        if (!response.ok) {
            throw new Error(data.message || `Erreur HTTP ${response.status}`);
        }

        // Show success message
        if (window.toast) {
            window.toast.success(data.message || 'Membre supprimé avec succès');
        }

        // Reload the page after a short delay
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error("Error performing delete:", error);

        // Show error message
        if (window.toast) {
            window.toast.error(error.message || 'Une erreur est survenue lors de la suppression');
        }

        // Re-throw to be handled by caller
        throw error;
    }
}

// Initialize the modal when the DOM is loaded
document.addEventListener('DOMContentLoaded', initDeleteConfirmationModal);

// Or initialize immediately if the DOM is already loaded
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    initDeleteConfirmationModal();
}