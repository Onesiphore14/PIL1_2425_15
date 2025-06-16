
document.getElementById('registerForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const nom =
        document.getElementById('nom').value.trim();
    const email =
        document.getElementById('email').value.trim();

    const numero =
        document.getElementById('numero').value.trim();
    const password =
        document.getElementById('password').value;
    const confirmer =
        document.getElementById('confirmer').value;
    if (nom === '' || email === '' || numero === '' || password === '' || confirmer === '') {
        alert("Tous les champs sont obligatoires.");
        return;
    }
    if (password !== confirmer) {
        alert("Les moys de passe ne correspondent pas");
        return;
        window.location.href = "accueil.html"
    }
});

