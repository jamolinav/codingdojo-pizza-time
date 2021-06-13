from django.forms import ModelForm, PasswordInput, TextInput
from django import forms
from ...models import Pizza

class PizzaForm(forms.ModelForm):

    class Meta:
        model = Pizza
        fields = '__all__'
        #fields = ['first_name','last_name','email','password']
        widgets = {
            'name' : TextInput(attrs={'placeholder': '<nombre>'}),
        }
        labels = {
            'name'  : 'Nombre',
        }

