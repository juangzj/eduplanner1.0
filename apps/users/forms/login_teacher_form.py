from django import forms
from django.contrib.auth.forms import AuthenticationForm

class TeacherLoginForm(forms.Form):
    # Usamos EmailField porque tu USERNAME_FIELD es 'gmail'
    gmail = forms.EmailField(
        label="Correo Electrónico (Gmail)",
        widget=forms.EmailInput(attrs={
            'placeholder': 'ejemplo@gmail.com',
            'class': 'form-control'
        })
    )
    
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': '********',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aseguramos que todos tengan la clase de Bootstrap
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})