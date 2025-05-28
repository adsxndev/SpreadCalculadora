from django import forms
from .models import SpreadRegistro

class SpreadForm(forms.ModelForm):
    class Meta:
        model = SpreadRegistro
        fields = ['spot_abertura', 'short_abertura', 'spot_fechamento', 'short_fechamento']
        widgets = {
            'spot_abertura': forms.NumberInput(attrs={'step': '0.01'}),
            'short_abertura': forms.NumberInput(attrs={'step': '0.01'}),
            'spot_fechamento': forms.NumberInput(attrs={'step': '0.01'}),
            'short_fechamento': forms.NumberInput(attrs={'step': '0.01'}),
        }