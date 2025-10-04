from django import forms
from .models import TipoProduto, Lote
from .models import ItemPedido

class TipoProdutoForm(forms.ModelForm):
    class Meta:
        model = TipoProduto
        fields = '__all__'
        
class Loteform(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['quantidade', 'data_fabricacao', 'data_validade', 'observacoes']
        
class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade']
