from django.db import models
from django.conf import settings
import uuid


# ------------------- OPCIONES GRADO -------------------
GRADOS_OPCIONES = [
    ('1', 'Primero'),
    ('2', 'Segundo'),
    ('3', 'Tercero'),
    ('4', 'Cuarto'),
    ('5', 'Quinto'),
    ('6', 'Sexto'),
    ('7', 'Séptimo'),
    ('8', 'Octavo'),
    ('9', 'Noveno'),
    ('10', 'Décimo'),
    ('11', 'Once'),
]


# ------------------- OPCIONES ASIGNATURA -------------------
AREAS_OPCIONES = [
    ('Español / Castellano', 'Español / Castellano'),
    ('Matemáticas', 'Matemáticas'),
    ('Ingles', 'Ingles'),
    ('Sociales', 'Sociales'),
    ('Ciencias Naturales', 'Ciencias Naturales'),
    ('Educación Física', 'Educación Física'),
    ('Filosofía', 'Filosofía'),
    ('Artística', 'Artística'),
    ('Ética y Valores', 'Ética y Valores'),
    ('Informática', 'Informática'),
]


# ------------------- OPCIONES PERIODO ACADÉMICO -------------------
PERIODO_ACADEMICO_OPCIONES = [
    ('Primer periodo', 'Primer periodo'),
    ('Segundo periodo', 'Segundo periodo'),
    ('Tercer periodo', 'Tercer periodo'),
]


# ------------------- MODELO NIVELES DE DESEMPEÑO -------------------
class PerformanceLevelTemplate(models.Model):
    """
    Modelo que representa los niveles de desempeño académico.
    Un usuario docente puede tener muchos niveles de desempeño.
    """

    # ID único automático (UUID)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Relación con el usuario (1 usuario -> muchos niveles)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="performance_levels",
        verbose_name="Usuario Docente"
    )

    generated_level_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ID Niveles Generados"
    )

    # Campos de contenido
    area = models.CharField(
        max_length=255,
        choices=AREAS_OPCIONES,
        verbose_name="Área"
    )

    level_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Título de Niveles"
    )

    level_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción de Niveles"
    )

    # GRADO COMO CAMPO DESPLEGABLE
    grade = models.CharField(
        max_length=2,
        choices=GRADOS_OPCIONES,
        verbose_name="Grado"
    )

    # ASIGNATURA COMO CAMPO DESPLEGABLE
    subject = models.CharField(
        max_length=255,
        choices=AREAS_OPCIONES,
        verbose_name="Asignatura"
    )

    competency = models.CharField(max_length=255, verbose_name="Competencia")
    statement = models.TextField(verbose_name="Afirmación")
    learning_evidence = models.TextField(verbose_name="Evidencia de Aprendizaje")

    # PERIODO ACADÉMICO COMO CAMPO DE ELECCIÓN
    academic_period = models.CharField(
        max_length=20,
        choices=PERIODO_ACADEMICO_OPCIONES,
        verbose_name="Periodo Académico"
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Eliminación")

    class Meta:
        verbose_name = "Nivel de Desempeño"
        verbose_name_plural = "Niveles de Desempeño"
        db_table = "performance_levels"

    def __str__(self):
        return f"{self.level_title} - {self.subject} ({self.grade})"