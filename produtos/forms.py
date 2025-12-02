from django import forms
from .models import TipoProduto, Lote
from .models import ItemPedido

class TipoProdutoForm(forms.ModelForm):
    class Meta:
        model = TipoProduto
        fields = [
            'nome', 
            'tipo', 
            'unidade_medida', 
            'possui_data_fabricacao', 
            'possui_data_validade'
        ]
        
class Loteform(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.tipo_produto = kwargs.pop('tipo_produto', None)
        super().__init__(*args, **kwargs)
        
        if self.tipo_produto and not self.tipo_produto.possui_data_fabricacao:
            self.fields['data_fabricacao'].required = False
            
        if self.tipo_produto and not self.tipo_produto.possui_data_validade:
            self.fields['data_validade'].required = False
        
    class Meta:
        model = Lote
        fields = [
            'quantidade_pacotes',
            'quantidade_por_pacote',
            'data_fabricacao',
            'data_validade',
            'preco_unitario',
            'observacoes'
        ]
        

class AdicionarEstoqueForm(forms.Form):
    quantidade_pacotes = forms.IntegerField(
        label='Quantidade a adicionar',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )   

class BaixaEstoqueForm(forms.Form):
    quantidade_pacotes = forms.IntegerField(
        label='Quantidade a dar baixa',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})    )
        
class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade']
