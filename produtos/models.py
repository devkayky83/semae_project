from django.db import models

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
        
