from django import forms
from .models import Movimentacao

class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['produto', 'tipo', 'quantidade', 'observacao']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
