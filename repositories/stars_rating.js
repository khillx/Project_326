let stars = document.getElementsByClassName("star");
let output = document.getElementById("output");

function starClick(numStars) {
    let j = 0;
    while (j < 5) {
        stars[j].className = "star";
        j++;
    }

    for (let i=0; i<numStars; i++) {
        switch (numStars) {
            case 1:
                stringNum = "one";
                break;
            case 2:
                stringNum = "two";
                break;
            case 3:
                stringNum = "three";
                break;
            case 4:
                stringNum = "four";
                break;
            case 5:
                stringNum = "five";
                break;
            default:
                stringNum = "";
                break;
        }
        stars[i].className = "star " + stringNum;
    }
}