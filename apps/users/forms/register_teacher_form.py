from django import forms
from ..models import TeacherUser

class TeacherRegisterForm(forms.ModelForm):
    # Campos que no están en el modelo pero necesitamos para la validación
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'})
    )
    confirm_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'})
    )

    class Meta:
        model = TeacherUser
        fields = [
            'gmail', 'first_name', 'middle_name', 'last_name', 
            'second_last_name', 'birth_date', 'nickname'
        ]
        
        # Etiquetas en ESPAÑOL para el usuario
        labels = {
            'gmail': 'Correo Electrónico (Gmail)',
            'first_name': 'Primer Nombre',
            'middle_name': 'Segundo Nombre',
            'last_name': 'Primer Apellido',
            'second_last_name': 'Segundo Apellido',
            'birth_date': 'Fecha de Nacimiento',
            'nickname': 'Apodo o Alias',
        }

        # Widgets para el diseño y control de entrada
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gmail': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@gmail.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'second_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data