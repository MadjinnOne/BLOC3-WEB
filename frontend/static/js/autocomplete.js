function switchForm(cible) {
    const formConnexion = document.getElementById("form-connexion");
    const formInscription = document.getElementById("form-inscription");

    if (cible === "inscription") {
        formConnexion.style.display = "none";
        formInscription.style.display = "block";
    } else {
        formInscription.style.display = "none";
        formConnexion.style.display = "block";
    }
}

// 🔎 Autocomplete VILLE
const inputVille = document.getElementById("ville");
const datalistVille = document.getElementById("suggestions-ville");

let timeout = null;
let controller = null;

inputVille.addEventListener("input", () => {
    const query = inputVille.value.trim();
    if (query.length < 2) return;

    clearTimeout(timeout);
    timeout = setTimeout(() => {
        if (controller) controller.abort();
        controller = new AbortController();

        fetch(`https://webservices-pub.bpost.be/ws/ExternalMailingAddressProofingCSREST_v1/address/autocomplete/locality?q=${encodeURIComponent(query)}&maxNumberOfSuggestions=5`, {
            signal: controller.signal
        })
            .then(response => response.json())
            .then(data => {
                datalistVille.innerHTML = "";
                const suggestions = data.response?.topSuggestions || [];

                suggestions.forEach(s => {
                    const name = s.address?.localityName;
                    if (name) {
                        const option = document.createElement("option");
                        option.value = name;
                        datalistVille.appendChild(option);
                    }
                });
            })
            .catch(err => {
                if (err.name !== "AbortError") console.error("Erreur API Bpost :", err);
            });
    }, 300);
});

// 🔁 Auto-remplir CODE POSTAL quand on sélectionne une ville
inputVille.addEventListener("change", () => {
    const selectedVille = inputVille.value.trim();
    if (selectedVille.length < 2) return;

    fetch(`https://webservices-pub.bpost.be/ws/ExternalMailingAddressProofingCSREST_v1/address/autocomplete/locality?q=${encodeURIComponent(selectedVille)}&maxNumberOfSuggestions=1`)
        .then(response => response.json())
        .then(data => {
            const suggestion = data.response?.topSuggestions?.[0];
            const postalCode = suggestion?.address?.postalCode;

            if (postalCode) {
                document.getElementById("code_postal").value = postalCode;
            } else {
                console.warn("Code postal non trouvé.");
            }
        })
        .catch(err => console.error("Erreur code postal :", err));
});

// 🏠 Autocomplete RUE (avec datalist)
const inputRue = document.getElementById("rue");
const datalistRue = document.getElementById("suggestions-rue");

inputRue.addEventListener("input", async function () {
    const rue = inputRue.value.trim();
    const ville = document.getElementById("ville").value.trim();
    const cp = document.getElementById("code_postal").value.trim();

    if (rue.length < 2 || !ville || !cp) {
        datalistRue.innerHTML = "";
        return;
    }

    try {
        const url = `https://webservices-pub.bpost.be/ws/ExternalMailingAddressProofingCSREST_v1/address/autocomplete/street?q=${encodeURIComponent(rue)}&postalCode=${encodeURIComponent(cp)}&locality=${encodeURIComponent(ville)}&maxNumberOfSuggestions=5`;
        const response = await fetch(url);
        const data = await response.json();

        const suggestions = data.response?.topSuggestions || [];
        datalistRue.innerHTML = "";

        suggestions.forEach(street => {
            const name = street?.address?.streetName;
            if (name) {
                const option = document.createElement("option");
                option.value = name;
                datalistRue.appendChild(option);
            }
        });

    } catch (err) {
        console.error("Erreur API Bpost (rue) :", err);
    }
});

