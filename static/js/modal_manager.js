// Function to open a modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "block";
    } else {
        console.error("Modal not found:", modalId);
    }
}

// Function to close a modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "none";
    }
}

// JavaScript to handle deletion with confirmation
function confirmDelete(token) {
    if (confirm("Are you sure you want to delete this file?")) {
        // Assuming you have a route set up to handle the deletion
        fetch(`/delete/${token}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("File deleted successfully.");
                    // Optionally close the modal and update the UI accordingly
                    closeModal('editModal');
                    // Update the UI or redirect as needed
                } else {
                    alert("Failed to delete file.");
                }
            })
            .catch(error => console.error('Error deleting file:', error));
    }
}


// Adding event listeners to upload buttons
document.querySelectorAll("#uploadBtn").forEach(btn => {
    btn.addEventListener('click', () => openModal('uploadModal'));
});

document.getElementById("editBtn").addEventListener('click', function() {
    openModal('editModal');
});


// Adding event listeners to close buttons within modals
document.querySelectorAll(".close").forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
        const modal = closeBtn.closest('.modal');
        if (modal) {
            closeModal(modal.id);
        }
    });
});

// Handling click outside of any modal content to close it
window.addEventListener('click', event => {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
});
