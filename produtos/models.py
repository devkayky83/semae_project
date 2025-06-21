from django.db import models

class Produto(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=50)
    data_fabricacao = models.DateField()
    data_validade = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    
    def resumo_para_admin(self):
        return f"{self.nome} ({self.tipo}) - {self.quantidade} unidades"
    
    def __str__(self):
        return self.resumo_para_admin()
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Produto do Estoque'
        verbose_name_plural = 'Produtos do Estoque'
        db_table = 'tb_produto'
        get_latest_by = 'data_validade'
        
        
