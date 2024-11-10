// app/static/js/download_file.js

document.addEventListener('DOMContentLoaded', function() {
    const downloadFileLinks = document.querySelectorAll('#downloadFileLink'); // Select all download links within options modal
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    downloadFileLinks.forEach(function(downloadLink) {
        downloadLink.addEventListener('click', function(event) {
            event.preventDefault();
            const token = downloadLink.getAttribute('href').split('/download/')[1];

            fetch(`/download/${token}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.status === 200) {
                    return response.blob();
                } else {
                    return response.json().then(data => {
                        throw new Error(data.message || 'Error downloading file.');
                    });
                }
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = downloadLink.getAttribute('data-file-name') || 'download';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error downloading file:', error);
                alert(error.message || 'Error downloading file.');
            });
        });
    });
});
