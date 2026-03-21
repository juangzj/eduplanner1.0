def get_landing_data():
    """
    Centraliza los datos del landing
    """

    return {
        "titulo": "Eduplanner",
        "descripcion": "Plataforma educativa con inteligencia artificial",

        "modulos": [
            {
                "titulo": "Niveles de desempeño",
                "descripcion": "Generación automática basada en taxonomía de Bloom",
                "icono": "bi-graph-up",
                "color": "primary"
            },
            {
                "titulo": "Secuencias didácticas",
                "descripcion": "Creación de clases con metodologías activas",
                "icono": "bi-easel",
                "color": "success"
            },
            {
                "titulo": "Rúbricas",
                "descripcion": "Evaluación alineada con niveles de desempeño",
                "icono": "bi-check2-square",
                "color": "warning"
            },
            {
                "titulo": "Generación ética",
                "descripcion": "Validación pedagógica y ética del contenido",
                "icono": "bi-shield-check",
                "color": "danger"
            },
        ]
    }