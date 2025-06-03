document.addEventListener('DOMContentLoaded', function () {
    let shouldRefresh = false;
    document.querySelectorAll('.vote-card').forEach(function(card) {
        const endDateStr = card.getAttribute('data-end');
        const countdownElt = card.querySelector('.countdown');
        if (!countdownElt || !endDateStr) return;

        function updateCountdown() {
            const endDate = new Date(endDateStr);
            const now = new Date();
            const diff = endDate - now;
            if (diff <= 0) {
                countdownElt.textContent = "Vote terminé";
                card.classList.add('vote-closed');
                shouldRefresh = true;
                return;
            }
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
            const minutes = Math.floor((diff / (1000 * 60)) % 60);
            const seconds = Math.floor((diff / 1000) % 60);

            let txt = "Temps restant : ";
            if (days > 0) txt += days + "j ";
            if (hours > 0 || days > 0) txt += hours + "h ";
            if (minutes > 0 || hours > 0 || days > 0) txt += minutes + "m ";
            txt += seconds + "s";
            countdownElt.textContent = txt;
        }

        updateCountdown();
        setInterval(updateCountdown, 1000);
    });

    // Vérifie toutes les secondes si on doit rafraîchir la page
    setInterval(function() {
        if (shouldRefresh) {
            window.location.reload();
        }
    }, 1000);
});
