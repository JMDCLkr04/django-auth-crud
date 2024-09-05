from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Write a title"}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder':"Write a description"}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input text-center'}),
        } #se puede reemplazar el text-center con m-auto o visceversa en caso de que uno no funcione