from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto
from .forms import ProdutoForm

# Create your views here.

def listar_produtos(request):
    produtos = Produto.objects.all()
    
    busca = request.GET.get('buscar')
    if busca:
        produtos = produtos.filter(nome__icontains=busca)
        
    tipo = request.GET.get('tipo')
    if tipo:
        produtos = produtos.filter(tipo=tipo)
        
    ordem = request.GET.get('ordem')
    if ordem == 'nome':
        produtos = produtos.order_by('nome')
    elif ordem == 'quantidade':
        produtos = produtos.order_by('-quantidade')
    
    return render(request, 'produtos/listar.html', {
        'produtos': produtos,
        'tipos': Produto.PRODUTO_TIPO,
        'busca': busca or '',
        'tipo_selecionado': tipo or 'TODOS',
        'ordem': ordem or '',
    }) 

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
    
def excluir_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    
    if request.method == 'POST':
        produto.delete()
        return redirect('listar_produtos')
    
    return render(request, 'produtos/excluir.html', {'produto': produto})

def baixar_estoque(request, id):
    produto = get_object_or_404(Produto, pk=id)
    
    if request.method == 'POST':
        quantidade_remover = int(request.POST.get('quantidade', 0))
        
        if quantidade_remover <= 0:
            error = "Informe um valor positivo."
        elif quantidade_remover > produto.quantidade:
            error = "Não há unidades suficientes no estoque."
        else:
            produto.quantidade -= quantidade_remover
            produto.save()
            return redirect('listar_produtos')
        
        return render(request, 'produtos/baixar_estoque.html', {
            'produto': produto,
            'error': error
        })
    
    return render(request, 'produtos/baixar_estoque.html', {'produto': produto})
    
        
