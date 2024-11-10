/* style for video */

document.addEventListener('DOMContentLoaded', function() {
    // Select all media elements
    const mediaElements = document.querySelectorAll('img, video, audio');

    // Apply styles and attributes dynamically
    mediaElements.forEach(el => {
        // Check if it's a video or audio and wants to take full height
        if (el.tagName === 'VIDEO' || el.tagName === 'AUDIO') {
            el.classList.add('full-height');
            el.style.objectFit = 'cover'; // Ensuring cover behavior

            // Adding controls if not already present (for example)
            if (!el.hasAttribute('controls')) {
                el.setAttribute('controls', true);
            }
        }

        // Universal max width for responsiveness
        el.style.maxWidth = '100%';
        el.style.height = 'auto'; // Maintain aspect ratio
        el.style.display = 'block';
        el.style.margin = '0 auto'; // Centering if needed

       
    });
});



