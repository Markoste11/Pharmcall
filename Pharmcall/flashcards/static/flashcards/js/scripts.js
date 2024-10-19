// scripts.js

// Define the getCookie function at the top of the file
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    let currentCardIndex = 0;
    let totalCards = userCards.length;
    let progressIndicator = document.getElementById('progress-indicator');
    let cardContainer = document.getElementById('card-container');

    function showCard(index) {
        if (index < totalCards) {
            let card = userCards[index];
    
            cardContainer.innerHTML = `
                <div class="flashcard">
                    <div class="card-inner">
                        <div class="card-front">
                            <p>${card.card.question}</p>
                        </div>
                        <div class="card-back">
                            <p>${card.card.answer}</p>
                            <p>How well did you recall this information?</p>
                            <div class="slider-container">
                                <input type="range" min="1" max="5" value="3" class="slider" id="recall-slider">
                                <div class="slider-labels">
                                    <span>1</span>
                                    <span>2</span>
                                    <span>3</span>
                                    <span>4</span>
                                    <span>5</span>
                                </div>
                            </div>
                            <button class="submit-btn btn btn-primary mt-3">Submit</button>
                        </div>
                    </div>
                </div>
            `;
    
            let flashcard = document.querySelector('.flashcard');
            flashcard.addEventListener('click', function(event) {
                if (!event.target.classList.contains('submit-btn') && !event.target.classList.contains('slider')) {
                    flashcard.classList.toggle('is-flipped');
                }
            });
    
            document.querySelector('.submit-btn').addEventListener('click', function(event) {
                event.stopPropagation(); // Prevent the flip when clicking the button
                let quality = document.getElementById('recall-slider').value;
                submitReview(card.uuid, quality);
            });
    
            updateProgress();
        } else {
            // User has completed all cards
            cardContainer.innerHTML = `
                <div class="congratulations-message">
                    <h1>Congratulations!</h1>
                    <p>You have completed today's cards! See Ya tomorrow </p>
                    <button class="continue-btn" onclick="window.location.href='/'">Continue</button>
                </div>
            `;
            progressIndicator.textContent = '';

            // Start the confetti animation
            startConfetti();
        }
    }
    
    function submitReview(cardUUID, quality) {
        fetch('/update_review/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                'card_uuid': cardUUID,
                'quality': parseInt(quality)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentCardIndex += 1;
                showCard(currentCardIndex);
            } else {
                alert('Error submitting review: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while submitting your review.');
        });
    }

    function updateProgress() {
        progressIndicator.textContent = `Card ${currentCardIndex + 1} of ${totalCards}`;
    }

    // Start by showing the first card
    showCard(currentCardIndex);
});

// Confetti Animation Functions
function startConfetti() {
    confetti({
        particleCount: 1000,
        spread: 1000,
        origin: { y: 0.5 }
    });
}

// Include the Confetti.js library
(function() {
    var confettiScript = document.createElement('script');
    confettiScript.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.4.0/dist/confetti.browser.min.js';
    confettiScript.async = true;
    document.head.appendChild(confettiScript);
})();
