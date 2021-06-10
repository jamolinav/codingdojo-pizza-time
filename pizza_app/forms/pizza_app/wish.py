from django.forms import ModelForm, PasswordInput, TextInput
from django import forms
from ...models import Wish

class WishForm(forms.ModelForm):
    class Meta:
        model = Wish
        fields = ['wish', 'description']
        widgets = {
            'wish' : TextInput(attrs={'placeholder': '<wish>'}),
            'description' : TextInput(attrs={'placeholder': '<description>'}),
        }
        labels = {
            'wish'  : 'I wish for',
            'description'  : 'Description',
        }

        