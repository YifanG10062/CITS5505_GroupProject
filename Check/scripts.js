document.addEventListener("DOMContentLoaded", function() {
    const imageElement = document.querySelector('.login-image');
    if (imageElement) {
        const imageUrl = imageElement.getAttribute('data-image');
        if (imageUrl) {
            imageElement.style.backgroundImage = `url('${imageUrl}')`;
        } else {
            console.warn("data-image attribute missing.");
        }
    } else {
        console.warn("No .login-image element found.");
    }
});
