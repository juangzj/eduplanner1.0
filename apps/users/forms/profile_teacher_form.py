from django import forms

from ..models import TeacherUser


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherUser
        fields = [
            "gmail",
            "first_name",
            "middle_name",
            "last_name",
            "second_last_name",
            "nickname",
        ]
        labels = {
            "gmail": "Correo Electrónico (Gmail)",
            "first_name": "Primer Nombre",
            "middle_name": "Segundo Nombre",
            "last_name": "Primer Apellido",
            "second_last_name": "Segundo Apellido",
            "nickname": "Apodo o Alias",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

        if self.is_bound:
            for name, field in self.fields.items():
                if self.errors.get(name):
                    current_class = field.widget.attrs.get("class", "")
                    field.widget.attrs.update({"class": f"{current_class} is-invalid"})
