document.addEventListener('DOMContentLoaded', function () {
    // Formulaire d'ajout
    const form = document.getElementById('add-person-form');
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const age = document.getElementById('age').value;

        fetch('/sample-web/api/people', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: name, age: parseInt(age) })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Recharger la page pour voir la nouvelle personne
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Une erreur s\'est produite');
            });
    });

    // Boutons de suppression
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function () {
            const personId = this.getAttribute('data-id');

            if (confirm('Êtes-vous sûr de vouloir supprimer cette personne ?')) {
                fetch(`/sample-web/api/people/${personId}`, {
                    method: 'DELETE'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.result) {
                            // Recharger la page
                            window.location.reload();
                        }
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                        alert('Une erreur s\'est produite');
                    });
            }
        });
    });
});