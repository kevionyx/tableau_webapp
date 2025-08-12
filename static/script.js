document.getElementById("uploadForm").addEventListener("submit", function() {
    document.getElementById("loader").style.display = "flex"; // era "block", ora flex per il centraggio
});

/* document.getElementById("uploadForm").addEventListener("submit", function(e) {
    e.preventDefault(); // Evita il refresh
    document.getElementById("loader").style.display = "flex";

    let formData = new FormData(this);
    fetch("/", { method: "POST", body: formData })
        .then(response => {
            if (response.ok) {
                document.getElementById("loader").style.display = "none";
                alert("PDF generato!");
            }
        })
        .catch(err => {
            document.getElementById("loader").style.display = "none";
            alert("Errore durante la generazione del PDF");
        });
}); */

