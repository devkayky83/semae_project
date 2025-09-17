from django.contrib import admin
from .models import TipoProduto, Lote

@admin.register(TipoProduto)
class TipoProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nome',)
    ordering = ('nome',)

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('tipo_produto', 'quantidade', 'data_fabricacao', 'data_validade')
    list_filter = ('tipo_produto',)
    search_fields = ('tipo_produto__nome',)
    ordering = ('data_validade',)