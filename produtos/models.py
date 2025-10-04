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

    def __str__(self):
        return f"{self.nome} - {self.tipo}"
    @property
    def estoque_total(self):
        """Soma a 'quantidade' de todos os lotes relacionados a este TipoProduto."""
        soma = self.lote_set.aggregate(Sum('quantidade'))['quantidade__sum']
        return soma or 0

    class Meta:
        ordering = ['nome']
        verbose_name = 'Tipo de Produto'
        verbose_name_plural = 'Tipos de Produtos'
        db_table = 'tb_tipo_produto'
        
        
class Lote(models.Model):
    tipo_produto = models.ForeignKey(TipoProduto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    data_fabricacao = models.DateField()
    data_validade = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    
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