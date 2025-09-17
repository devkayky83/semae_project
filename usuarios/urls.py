from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('menu/', views.menu_principal, name='menu_principal'),
    path('criar/', views.criar_usuario, name='criar_usuario'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),
]