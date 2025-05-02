document.addEventListener("DOMContentLoaded", function() {
    fetch('https://api.marketstack.com/v2/eod?access_key=4ece27fbd41ca25cb97f22cbf8713369&symbols=AAPL')
    .then(response => response.json())
    .then(data => {
        const imageUrl = data.imageUrl; // Assuming the API returns an image URL
        document.querySelector('.login-image').style.backgroundImage = `url(${imageUrl})`;
    })
    .catch(error => console.error('Failed to load image:', error));
});
