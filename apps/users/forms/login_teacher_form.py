from django import forms
from ..models import TeacherUser

class TeacherLoginForm(forms.Form):
    gmail = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu-correo@gmail.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'})
    )