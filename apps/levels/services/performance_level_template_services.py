from ..models import PerformanceLevelTemplate


def create_performance_level_service(form, user):
    """
    Encapsula la creación de un nuevo nivel de desempeño.
    """

    performance_level = form.save(commit=False)

    # Asignar el usuario antes de guardar
    performance_level.user = user

    performance_level.save()

    return performance_level