from django.contrib import admin
from .models import Produto

@admin.register(Produto)

# Register your models here.

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'quantidade', 'data_validade')
    list_filter = ('tipo',)
    search_fields = ('nome',)
    ordering = ('nome',)
