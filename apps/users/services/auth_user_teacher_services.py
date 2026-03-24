from django.contrib.auth import authenticate, login

def login_teacher_service(request, gmail, password):
    """Autentica al docente y maneja la sesión."""
    user = authenticate(request, gmail=gmail, password=password)

    if user is not None:
        login(request, user)
        return user

    return None