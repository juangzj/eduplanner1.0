from django.contrib.auth import authenticate, login, logout

def login_teacher_service(request, gmail, password):
    """Autentica al docente y maneja la sesión."""
    user = authenticate(request, gmail=gmail, password=password)

    if user is not None:
        login(request, user)
        return user

    return None

def process_logout(request):
        """Maneja la destrucción de la sesión del usuario"""
        logout(request)