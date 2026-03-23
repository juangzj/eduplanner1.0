from django.db import IntegrityError, DatabaseError
from ..models import TeacherUser

def register_teacher_service(data):
    """Lógica de negocio para registrar un docente con manejo de errores."""
    
    # Hacemos una copia para no alterar el diccionario original del formulario
    user_data = data.copy()
    
    try:
        # Extraemos la contraseña de forma segura
        password = user_data.pop('password')
        user_data.pop('confirm_password', None) # Eliminamos si existe
        
        # El método create_user del manager se encarga del hashing y el save()
        user = TeacherUser.objects.create_user(
            password=password,
            **user_data
        )
        return user

    except IntegrityError as e:
        # Este error ocurre si el Gmail ya existe (Violación de unicidad)
        # O si un campo obligatorio llega vacío a la BD
        if 'gmail' in str(e).lower():
            raise ValueError("Este correo electrónico ya se encuentra registrado.")
        raise ValueError("Error de integridad: Verifique que los datos sean únicos.")

    except TypeError as e:
        # Este error ocurre si envías un campo que NO existe en el modelo TeacherUser
        raise ValueError(f"Error en los campos enviados: {str(e)}")

    except DatabaseError as e:
        # Error de conexión o problema físico con la base de datos
        raise Exception("Error de conexión con la base de datos. Intente más tarde.")

    except Exception as e:
        # Cualquier otro error inesperado lo relanzamos para que la vista lo vea
        raise e