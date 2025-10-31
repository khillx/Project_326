// static/js/stars_ratings.js
let stars = document.getElementsByClassName("star");
let currentRating = 0;

function starClick(numStars) {
    currentRating = numStars;
    let j = 0;
    while (j < 5) {
        stars[j].className = "star";
        j++;
    }

    for (let i = 0; i < numStars; i++) {
        let ratingClass = "";
        switch (numStars) {
            case 1: ratingClass = "one"; break;
            case 2: ratingClass = "two"; break;
            case 3: ratingClass = "three"; break;
            case 4: ratingClass = "four"; break;
            case 5: ratingClass = "five"; break;
        }
        stars[i].className = "star " + ratingClass;
    }
}

// Export for use in main script
window.getCurrentRating = () => currentRating;