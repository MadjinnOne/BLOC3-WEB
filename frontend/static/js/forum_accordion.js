document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.accordion-toggle').forEach(function(btn) {
        btn.addEventListener('click', function() {
            // Accordéon strict : ferme les autres catégories ouvertes
            document.querySelectorAll('.accordion-content').forEach(function(content) {
                if (content !== btn.nextElementSibling) {
                    content.classList.remove('active');
                    content.previousElementSibling.classList.remove('opened');
                }
            });
            // Toggle l'ouverture sur le bouton cliqué
            btn.classList.toggle('opened');
            btn.nextElementSibling.classList.toggle('active');
        });
    });
});
