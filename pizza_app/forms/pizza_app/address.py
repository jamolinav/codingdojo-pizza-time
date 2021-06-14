from django.forms import TextInput
from django import forms
from ...models import Address

class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        #fields = '__all__'
        fields = ['alias','street','number','appartment','floor','comuna','comments']
        widgets = {
            'alias' : TextInput(attrs={'placeholder': '<alias>'}),
            'street' : TextInput(attrs={'placeholder': '<calle>'}),
            'number' : TextInput(attrs={'placeholder': '<número>'}),
            'appartment' : TextInput(attrs={'placeholder': '<opcional>'}),
            'floor' : TextInput(attrs={'placeholder': '<opcional>'}),
            'comments' : TextInput(attrs={'placeholder': '<opcional>'}),
        }
        labels = {
            'alias'  : 'Alias',
            'street'  : 'Calle',
            'number'  : 'Número',
            'appartment'  : 'Departamento',
            'floor'  : 'Piso',
            'comments'  : 'Referencia',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['appartment'].required = False
        self.fields['floor'].required = False
