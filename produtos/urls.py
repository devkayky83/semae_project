from django.urls import path
from . import views

urlpatterns = [
    # URLs para Tipos de Produto
    path('', views.listar_tipos_produto, name='listar_tipos_produto'),
    path('novo/', views.cadastrar_tipo_produto, name='cadastrar_tipo_produto'),
    path('editar/<int:tipo_produto_id>/', views.editar_tipo_produto, name='editar_tipo_produto'),
    path('excluir/<int:tipo_produto_id>/', views.excluir_tipo_produto, name='excluir_tipo_produto'),

    # URLs para Lotes
    path('lotes/<int:tipo_produto_id>/', views.listar_lotes, name='listar_lotes'),
    path('lotes/<int:tipo_produto_id>/novo/', views.cadastrar_lote, name='cadastrar_lote'),
    path('lotes/editar/<int:lote_id>/', views.editar_lote, name='editar_lote'),
    path('lotes/baixar/<int:lote_id>/', views.baixar_estoque, name='baixar_estoque'),
    path('lotes/excluir/<int:lote_id>/', views.excluir_lote, name='excluir_lote'),
    
    #URLs para relatórios
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
]