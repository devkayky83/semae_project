from django.shortcuts import render, redirect
from .models import Produto

# Create your views here.

def listar_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos/listar.html', {'produtos': produtos}) 

def cadastrar_produto(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        tipo = request.POST['tipo']
        quantidade = int(request.POST['quantidade'])
        data_fabricacao = request.POST['data_fabricacao']
        data_validade = request.POST['data_validade']
        observacoes = request.POST.get('observacoes', '')
        
        Produto.objects.create(
            nome=nome,
            tipo=tipo,
            quantidade=quantidade,
            data_fabricacao=data_fabricacao,
            data_validade=data_validade,
            observacoes=observacoes
        )
        
        return redirect('listar_produtos')
    
    return render(request, 'produtos/cadastrar.html')
