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
        fetch(`/delete/${token}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("File deleted successfully.");
                    window.location.href = '/'; // Redirect to the home route after deletion
                } else {
                    alert(data.message); // Show the error message from the server
                }
            })
            .catch(error => {
                console.error('Error deleting file:', error);
                alert("Error occurred while deleting file.");
            });
    }
}


// Attach event listeners
document.addEventListener('DOMContentLoaded', function () {
    const uploadBtns = document.querySelectorAll("#uploadBtn");
    uploadBtns.forEach(btn => {
        btn.addEventListener('click', () => openModal('uploadModal'));
    });

    const editBtns = document.querySelectorAll("#editBtn");
    editBtns.forEach(btn => {
        btn.addEventListener('click', () => openModal('editModal'));
    });

    const closeButtons = document.querySelectorAll(".close");
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            closeModal(this.closest('.modal').id);
        });
    });

    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
    });
});
