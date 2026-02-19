// https://us.glock.com/en/products/commercial-firearms/pistols/g19-gen6
// VISIT URL, RUN THIS SCRIPT, SPIN THE GUN TO CAPTURE ALL URLS.

// Create a Set to store unique src values
const uniqueSrcSet = new Set();

// Select all images with the specific class
const images = document.querySelectorAll('.TurntablePistolViewer_viewer__Bl1_D');

// Function to add src to the Set and log it
function updateSrcSet(img) {
    if (img.src) {
        uniqueSrcSet.add(img.src);
        console.log(uniqueSrcSet);
    }
}

// Observe changes to the src attribute
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'src') {
            updateSrcSet(mutation.target);
        }
    });
});

// Attach observer and collect initial src values
images.forEach((img) => {
    updateSrcSet(img); // Add initial src
    observer.observe(img, { attributes: true });
});

// THEN EXTRACT THE SET USING:
// const sortedSrcSet = Array.from(uniqueSrcSet).sort((a, b) => {
//     const aFileName = parseInt(a.split('/').pop().split('.')[0], 10);
//     const bFileName = parseInt(b.split('/').pop().split('.')[0], 10);
//     return aFileName - bFileName;
// });
// JSON.stringify(sortedSrcSet, null, 4)
