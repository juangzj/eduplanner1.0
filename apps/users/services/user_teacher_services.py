
from ..models import TeacherUser

def register_teacher_service(data):
    """Lógica de negocio para registrar un docente."""
    password = data.pop('password')
    data.pop('confirm_password', None)
    
    # El método create_user del manager se encarga del hashing
    user = TeacherUser.objects.create_user(
        password=password,
        **data
    )
    return user