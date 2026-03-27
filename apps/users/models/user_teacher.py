from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
import uuid


# ------------------- MANAGER -------------------
class TeacherUserManager(BaseUserManager):
    """
    Manager que define cómo se crean los docentes (usuarios normales)
    y superusuarios usando el gmail como identificador.
    """

    def create_user(self, gmail, password=None, **extra_fields):
        if not gmail:
            raise ValueError("El usuario debe tener un gmail")

        gmail = self.normalize_email(gmail)
        user = self.model(gmail=gmail, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, gmail, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(gmail, password, **extra_fields)


# ------------------- MODELO -------------------
class TeacherUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado para Docentes.
    Usa 'gmail' como identificador único de inicio de sesión.
    """

    # ID único automático (UUID)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Campos personales
    first_name = models.CharField(max_length=100, verbose_name="Primer Nombre")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Segundo Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Primer Apellido")
    second_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Segundo Apellido")
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="Apodo")
    birth_date = models.DateField(verbose_name="Fecha de Nacimiento")

    # Correo electrónico (único)
    gmail = models.EmailField(unique=True, verbose_name="Correo Electrónico (Gmail)")

    # Campos de estado y permisos
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Manager personalizado
    objects = TeacherUserManager()

    # Configuración de Login
    USERNAME_FIELD = "gmail"

    # Campos obligatorios al crear por consola (createsuperuser)
    REQUIRED_FIELDS = ["first_name", "last_name", "birth_date"]

    class Meta:
        verbose_name = "Usuario Docente"
        verbose_name_plural = "Usuarios Docentes"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.gmail})"