// JavaScript customization goes here

// Aviso de "respuesta en generación" para formularios que llaman a la IA.
// Uso: <form method="post" data-ai-loading="Mensaje a mostrar">
(function () {
    const overlay = document.getElementById("ai-loading-overlay");
    const messageEl = document.getElementById("ai-loading-message");
    if (!overlay) {
        return;
    }

    function hideOverlay() {
        overlay.classList.add("d-none");
        document.querySelectorAll("form[data-ai-loading] [type='submit']").forEach(function (button) {
            button.disabled = false;
        });
    }

    document.addEventListener("submit", function (event) {
        const form = event.target;
        if (!form.matches("form[data-ai-loading]") || event.defaultPrevented) {
            return;
        }

        const message = form.getAttribute("data-ai-loading");
        if (message && messageEl) {
            messageEl.textContent = message;
        }
        overlay.classList.remove("d-none");

        // Evita envíos duplicados mientras la IA responde.
        form.querySelectorAll("[type='submit']").forEach(function (button) {
            button.disabled = true;
        });
    });

    // Si el usuario vuelve con el botón "atrás", la página puede restaurarse desde caché.
    window.addEventListener("pageshow", hideOverlay);
})();
