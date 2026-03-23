from django import forms
from ..models import TeacherUser

class TeacherRegisterForm(forms.ModelForm):
    # Definimos campos extra que no están en el modelo
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '********'})
    )
    confirm_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '********'})
    )

    class Meta:
        model = TeacherUser
        fields = [
            'gmail', 'first_name', 'middle_name', 'last_name', 
            'second_last_name', 'birth_date', 'nickname'
        ]
        labels = {
            'gmail': 'Correo Electrónico (Gmail)',
            'first_name': 'Primer Nombre',
            'middle_name': 'Segundo Nombre',
            'last_name': 'Primer Apellido',
            'second_last_name': 'Segundo Apellido',
            'birth_date': 'Fecha de Nacimiento',
            'nickname': 'Apodo o Alias',
        }
        widgets = {
            # HTML5 date input para que aparezca el calendario nativo
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Si el formulario ya fue enviado y tiene errores, añadimos clases visuales
        if self.is_bound:
            for name, field in self.fields.items():
                if self.errors.get(name):
                    current_class = field.widget.attrs.get('class', '')
                    field.widget.attrs.update({'class': f'{current_class} is-invalid'})
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data