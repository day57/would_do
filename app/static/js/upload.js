// app/static/js/upload.js

document.addEventListener('DOMContentLoaded', function() {
    const uploadFileBtn = document.getElementById('uploadFileBtn'); // Upload button inside the modal
    const uploadForm = document.getElementById('fileUploadForm'); // Upload form
    const messageContainer = document.getElementById('messageContainer');

    if (uploadFileBtn && uploadForm) {
        uploadFileBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default button behavior

            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            let formData = new FormData(uploadForm);

            fetch(uploadForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken, // Include CSRF token in the headers
                    'Accept': 'application/json', // Expect JSON response
                },
                body: formData, // Send form data
                credentials: 'same-origin', // Include cookies in the request
            })
            .then(response => {
                if (response.ok) {
                    return response.json(); // Parse JSON response
                } else {
                    return response.json().then(data => {
                        throw new Error(data.message || 'An error occurred.');
                    });
                }
            })
            .then(data => {
                displayMessage(data.message, data.success);
                if (data.success) {
                    uploadForm.reset(); // Reset the form on successful upload
                    const uploadModal = document.getElementById('uploadModal');
                    if (uploadModal) {
                        uploadModal.style.display = 'none'; // Close the modal after uploading
                    }
                    // Optionally, reload the page to show the new file
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error uploading file:', error);
                displayMessage(error.message || 'Error uploading file.', false);
            });
        });
    }

    function displayMessage(message, isSuccess) {
        if (messageContainer) {
            messageContainer.textContent = message;
            messageContainer.style.color = isSuccess ? 'green' : 'red';
        }
    }
});
