// app/static/js/modal_manager.js

document.addEventListener('DOMContentLoaded', function() {
    // Function to open a modal
    function openModal(modalId, additionalData = {}) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';

            // Handle additional data for specific modals (if any)
            if (modalId === 'optionsModal') {
                const fileName = additionalData.fileName || 'Unknown File';
                const fileToken = additionalData.fileToken || '';

                const optionFileNameSpan = modal.querySelector('#optionFileName');
                const downloadFileLink = modal.querySelector('#downloadFileLink');
                const deleteFileBtn = modal.querySelector('#deleteFileBtn');

                if (optionFileNameSpan) {
                    optionFileNameSpan.textContent = fileName;
                }

                if (downloadFileLink) {
                    // Corrected Download URL
                    downloadFileLink.href = `/download/${fileToken}`;
                }

                if (deleteFileBtn) {
                    // Set the data-token attribute for deletion
                    deleteFileBtn.setAttribute('data-token', fileToken);
                }
            } else if (modalId === 'uploadModal') {
                // If there's any specific setup for the upload modal, handle it here.
                const messageContainer = modal.querySelector('#messageContainer');
                if (messageContainer) {
                    messageContainer.textContent = ''; // Clear any previous messages when opening the modal.
                }
            }
        }
    }

    // Function to close a modal
    function closeModal(modal) {
        modal.style.display = 'none';
    }

    // Attach event listeners to all open-modal buttons
    const openModalButtons = document.querySelectorAll('.open-modal-btn');
    openModalButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const modalTarget = button.getAttribute('data-modal-target');
            const modal = document.getElementById(modalTarget);

            if (modalTarget === 'optionsModal') {
                const fileName = button.getAttribute('data-file-name') || 'Unknown File';
                const fileToken = button.getAttribute('data-file-token') || '';
                openModal(modalTarget, { fileName: fileName, fileToken: fileToken });
            } else if (modalTarget === 'uploadModal') {
                openModal(modalTarget); // Open the upload modal without additional data.
            }
        });
    });

    // Attach event listeners to all close-modal buttons
    const closeModalButtons = document.querySelectorAll('.close-modal-btn');
    closeModalButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const modal = button.closest('.modal');
            if (modal) {
                closeModal(modal);
            }
        });
    });

    // Close modals when clicking outside of them
    window.addEventListener('click', function(event) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(function(modal) {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    // Optional: Close modals with the Esc key
    window.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal[style*="display: block"]');
            openModals.forEach(function(modal) {
                closeModal(modal);
            });
        }
    });
});
