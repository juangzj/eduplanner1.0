def get_landing_data():
    """
    Centraliza los datos del landing
    """

    return {
        "titulo": "Eduplanner",
        "descripcion": "Plataforma educativa con inteligencia artificial para docentes de educación media",
        "subtitulo": "Diseña, evalúa y organiza planeaciones, niveles de desempeño, rúbricas y prompts pedagógicos en un solo lugar.",
        "resumen": {
            "docentes": "Pensado para equipos académicos de instituciones educativas",
            "flujo": "Desde la idea inicial hasta el producto pedagógico final",
            "ia": "Con retroalimentación y refinamiento asistido por IA"
        },

        "modulos": [
            {
                "titulo": "Niveles de desempeño",
                "descripcion": "Generación automática basada en taxonomía de Bloom y la evidencia de aprendizaje.",
                "icono": "bi-graph-up",
                "color": "primary",
                "url": "/levels/"
            },
            {
                "titulo": "Planeaciones de clase",
                "descripcion": "Creación de clases con metodologías activas, objetivos, recursos y momentos didácticos.",
                "icono": "bi-easel",
                "color": "success",
                "url": "/levels/class-plans/"
            },
            {
                "titulo": "Prompt Lab",
                "descripcion": "Construcción, evaluación y refinamiento de prompts pedagógicos con retroalimentación por campo.",
                "icono": "bi-chat-square-text",
                "color": "info",
                "url": "/prompt/create/"
            },
            {
                "titulo": "Rúbricas",
                "descripcion": "Evaluación alineada con niveles de desempeño y criterios observables.",
                "icono": "bi-check2-square",
                "color": "warning",
                "url": "/levels/"
            },
            {
                "titulo": "Configuración docente",
                "descripcion": "Actualiza tus datos básicos y mantén tu perfil académico al día.",
                "icono": "bi-gear",
                "color": "danger",
                "url": "/users/settings/"
            },
        ]
        ,
        "beneficios": [
            {
                "titulo": "Ahorra tiempo de preparación",
                "descripcion": "Reduce trabajo repetitivo y organiza tus recursos en una sola plataforma.",
                "icono": "bi-clock-history"
            },
            {
                "titulo": "Mejora la calidad pedagógica",
                "descripcion": "La IA te ayuda a afinar contexto, tarea, formato y retroalimentación.",
                "icono": "bi-mortarboard"
            },
            {
                "titulo": "Refina por intentos",
                "descripcion": "Cada intento recibe retroalimentación para llevar el contenido a un nivel más sólido.",
                "icono": "bi-arrow-repeat"
            }
        ],
        "proceso": [
            {
                "paso": "01",
                "titulo": "Define el contexto",
                "descripcion": "Selecciona grado, área, competencia y evidencia de aprendizaje."
            },
            {
                "paso": "02",
                "titulo": "Construye con IA",
                "descripcion": "Genera niveles, rúbricas o prompts con una base pedagógica clara."
            },
            {
                "paso": "03",
                "titulo": "Refina y guarda",
                "descripcion": "Recibe sugerencias, mejora cada intento y conserva tu trabajo."
            }
        ],
        "metricas": [
            {"valor": "4", "etiqueta": "módulos principales"},
            {"valor": "100%", "etiqueta": "flujo orientado a docentes"},
            {"valor": "IA", "etiqueta": "con retroalimentación por campo"}
        ]
    }