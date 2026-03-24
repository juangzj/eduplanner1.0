from django import forms
from django.contrib.auth import authenticate

class TeacherLoginForm(forms.Form):
    gmail = forms.EmailField(
        label="Correo Electrónico (Gmail)",
        error_messages={
            'required': 'Debe ingresar su correo electrónico.',
            'invalid': 'Ingrese un correo electrónico válido.'
        },
        widget=forms.EmailInput(attrs={
            'placeholder': 'ejemplo@gmail.com',
            'class': 'form-control'
        })
    )
    
    password = forms.CharField(
        label="Contraseña",
        error_messages={
            'required': 'Debe ingresar su contraseña.'
        },
        widget=forms.PasswordInput(attrs={
            'placeholder': '********',
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        gmail = cleaned_data.get("gmail")
        password = cleaned_data.get("password")

        if gmail and password:
            user = authenticate(username=gmail, password=password)

            if user is None:
                raise forms.ValidationError("Correo o contraseña incorrectos.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})