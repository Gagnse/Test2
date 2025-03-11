// Toast notification system
class ToastManager {
    constructor() {
        this.toastContainer = null;
        this.timeouts = [];
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!this.toastContainer) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.className = 'toast-container';
            document.body.appendChild(this.toastContainer);

            // Add styles to document
            const style = document.createElement('style');
            style.textContent = `
                .toast-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    max-width: 350px;
                }
                
                .toast {
                    padding: 12px 20px;
                    border-radius: 6px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    color: white;
                    font-size: 14px;
                    opacity: 0;
                    transform: translateY(-20px);
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    animation: toast-in 0.3s ease forwards;
                }
                
                .toast.removing {
                    animation: toast-out 0.3s ease forwards;
                }
                
                .toast-success {
                    background-color: #28a745;
                }
                
                .toast-error {
                    background-color: #dc3545;
                }
                
                .toast-info {
                    background-color: #17a2b8;
                }
                
                .toast-warning {
                    background-color: #ffc107;
                    color: #333;
                }
                
                .toast-close {
                    background: none;
                    border: none;
                    color: inherit;
                    font-size: 18px;
                    cursor: pointer;
                    opacity: 0.8;
                    margin-left: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                }
                
                .toast-close:hover {
                    opacity: 1;
                }
                
                .toast-message {
                    flex: 1;
                }
                
                @keyframes toast-in {
                    from {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                @keyframes toast-out {
                    from {
                        opacity: 1;
                        transform: translateY(0);
                    }
                    to {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Show a toast notification
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const messageSpan = document.createElement('span');
        messageSpan.className = 'toast-message';
        messageSpan.textContent = message;

        const closeButton = document.createElement('button');
        closeButton.className = 'toast-close';
        closeButton.innerHTML = '×';
        closeButton.onclick = () => this.remove(toast);

        toast.appendChild(messageSpan);
        toast.appendChild(closeButton);
        this.toastContainer.appendChild(toast);

        // Auto-remove after duration
        const timeout = setTimeout(() => {
            this.remove(toast);
        }, duration);

        this.timeouts.push(timeout);

        return toast;
    }

    // Remove a specific toast
    remove(toast) {
        if (!toast || !this.toastContainer.contains(toast)) return;

        toast.classList.add('removing');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    // Clear all toasts
    clear() {
        while (this.toastContainer.firstChild) {
            this.toastContainer.removeChild(this.toastContainer.firstChild);
        }

        // Clear all timeouts
        this.timeouts.forEach(timeout => clearTimeout(timeout));
        this.timeouts = [];
    }

    // Shorthand methods
    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }
}

// Create a global toast manager instance
const toastManager = new ToastManager();

// Make it available globally
window.toast = {
    show: (message, type, duration) => toastManager.show(message, type, duration),
    success: (message, duration) => toastManager.success(message, duration),
    error: (message, duration) => toastManager.error(message, duration),
    info: (message, duration) => toastManager.info(message, duration),
    warning: (message, duration) => toastManager.warning(message, duration),
    clear: () => toastManager.clear()
};