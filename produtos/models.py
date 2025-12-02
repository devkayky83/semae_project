from django.db import models
from usuarios.models import Usuario

from django.db import models
from django.db.models import Sum 


class TipoProduto(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True)
    PRODUTO_TIPO = (
        ('ALIMENTO', 'Alimento'),
        ('LIMPEZA', 'Limpeza'),
        ('ESCOLAR', 'Escolar'),
        ('OUTROS', 'Outros'),
    )
    tipo = models.CharField(max_length=50, choices=PRODUTO_TIPO, default='OUTROS')
    
    ORIGEM_COMPRA_CHOICES = (
        ('COMUM', 'Compra Comum'),
        ('AGRICULTURA', 'Agricultura Familiar'),
    )
    
    origem_compra = models.CharField(
        max_length=15,
        choices=ORIGEM_COMPRA_CHOICES,
        default='COMUM',
        verbose_name='Origem da Compra'
    )
    
    UNIDADE_CHOICES = (
        ('KG', 'Quilogramas (KG)'),
        ('G', 'Gramas (g)'),
        ('L', 'Litros (L)'),
        ('ML', 'Mililitros (mL)'),
        ('UN', 'Unidades (Un)'),
        ('CX', 'Caixas (Cx)'),
        ('NA', 'Não Aplicável (N/A)')
    )
    
    unidade_medida = models.CharField(
        max_length=5,
        choices=UNIDADE_CHOICES,
        default='NA',
        verbose_name='Unidade de Medida'
    )
    
    possui_data_fabricacao = models.BooleanField(
        default=True,
        verbose_name='Possui Data de Fabricação?',
    )
    
    possui_data_validade = models.BooleanField(
        default=True,
        verbose_name='Possui Data de Validade?'
    )

    def __str__(self):
        return f"{self.nome} - {self.tipo}"
    
    def __str__(self):
        return f"{self.nome} ({self.get_unidade_medida_display()})"

    class Meta:
        ordering = ['nome']
        verbose_name = 'Tipo de Produto'
        verbose_name_plural = 'Tipos de Produtos'
        db_table = 'tb_tipo_produto'
        
        
class Lote(models.Model):
    tipo_produto = models.ForeignKey(
        TipoProduto, 
        on_delete=models.CASCADE,
        related_name='lotes'
    )
    
    quantidade_pacotes = models.IntegerField(
        verbose_name='Nº de Pacotes/Itens',
        default=0,
        help_text='Quantidade física de pacotes ou unidades.'
    )
    
    quantidade_por_pacote = models.DecimalField(
        max_digits=10,
        default=1,
        decimal_places=2,
        verbose_name='Peso/Volume por Pacote',
        help_text='Peso ou volume de cada pacote/item.',
        null=True,
        blank=True
    )
    
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço Unitário (R$)"
    )
    
    data_fabricacao = models.DateField(blank=True, null=True, verbose_name='Data de Fabricação')
    data_validade = models.DateField(blank=True, null=True, verbose_name='Data de Validade')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    
    @property
    def quantidade_total_unidade(self):
        quantidade_por_pacote = self.quantidade_por_pacote if self.quantidade_por_pacote is not None else 1
        return self.quantidade_pacotes * self.quantidade_por_pacote
    
    def __str__(self):
            return f"Lote de {self.tipo_produto.nome} - Validade: {self.data_validade}"
    
    class Meta:
        ordering = ['data_validade']
        verbose_name = 'Lote de Produto'
        verbose_name_plural = 'Lotes de Produtos'
        db_table = 'tb_lote'
        get_latest_by = 'data_validade'
        
class Pedido(models.Model):
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('ENTREGUE', 'Entregue'),
    )

    solicitante = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='pedidos_feitos')
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']

    def __str__(self):
        return f"Pedido #{self.id} por {self.solicitante.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(TipoProduto, on_delete=models.PROTECT, verbose_name="Produto")
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome}"