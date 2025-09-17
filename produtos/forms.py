from django import forms
from .models import TipoProduto, Lote

class TipoProdutoForm(forms.ModelForm):
    class Meta:
        model = TipoProduto
        fields = '__all__'
        
class Loteform(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['quantidade', 'data_fabricacao', 'data_validade', 'observacoes']
        

