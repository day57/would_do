// app/static/js/create_user.js

document.addEventListener('DOMContentLoaded', () => {
    const createUserForm = document.querySelector('form');

    createUserForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent the default form submission

        // Retrieve the CSRF token from the hidden input
        const csrfToken = createUserForm.querySelector('input[name="csrf_token"]').value;

        // Create a FormData object from the form
        const formData = new FormData(createUserForm);

        // Send the AJAX request using Fetch API
        fetch(createUserForm.action, {
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
            if (data.success) {
                // Redirect to the index page upon successful user creation
                window.location.href = '/';
            } else {
                // Handle errors (display a message to the user)
                alert(data.message || 'An error occurred.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message || 'An error occurred while creating the user.');
        });
    });
});
