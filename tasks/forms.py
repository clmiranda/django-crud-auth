from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "important"]
        labels = {
            "title": "Título de la Tarea",
            "description": "Descripción de la Tarea",
            "important": "Importante",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ingresa el Titulo"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingresa la Descripción",
                    "rows": "5",
                }
            ),
            "important": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
