from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto
from .forms import ProdutoForm

# Create your views here.

def listar_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos/listar.html', {'produtos': produtos}) 

def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm()
    
    return render(request, 'produtos/cadastrar.html', {'form': form})

def editar_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')
    else:
        form = ProdutoForm(instance=produto)
        
    return render(request, 'produtos/cadastrar.html', {
        'form': form,
        'editar': True, 
        'produto': produto,
    })
    
        
