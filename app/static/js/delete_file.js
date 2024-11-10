// app/static/js/delete_file.js

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button'); // Select all delete buttons within options modal
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    deleteButtons.forEach(function(deleteBtn) {
        deleteBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const token = deleteBtn.getAttribute('data-token');

            if (confirm('Are you sure you want to delete this file?')) {
                fetch(`/delete/${token}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    const contentType = response.headers.get('Content-Type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json();
                    } else {
                        return response.text().then(text => {
                            throw new Error(`Server returned non-JSON response: ${text}`);
                        });
                    }
                })
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        // Optionally, remove the file entry from the DOM
                        // Example:
                        // deleteBtn.closest('.file-entry').remove();
                        window.location.reload(); // Or redirect to refresh the page
                    }
                })
                .catch(error => {
                    console.error('Error deleting file:', error);
                    alert(error.message || 'Error deleting file.');
                });
            }
        });
    });
});
