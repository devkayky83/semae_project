from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TipoProduto, Lote
from .forms import TipoProdutoForm, Loteform
from xhtml2pdf import pisa
from usuarios.views import is_nutricionista, is_secretario_or_nutricionista

import openpyxl

# Apenas nutricionista ou secretário pode ver a lista de produtos do estoque
@login_required
@user_passes_test(is_secretario_or_nutricionista) 
def listar_tipos_produto(request):
    tipos_produto = TipoProduto.objects.all()
    
    busca = request.GET.get('buscar')
    if busca:
        tipos_produto = tipos_produto.filter(nome__icontains=busca)
        
    tipo = request.GET.get('tipo')
    if tipo and tipo != 'TODOS':
        tipos_produto = tipos_produto.filter(tipo=tipo)
        
    ordem = request.GET.get('ordem')
    if ordem == 'nome':
        tipos_produto = tipos_produto.order_by('nome')
    
    return render(request, 'produtos/listar_tipos.html', {
        'tipos_produto': tipos_produto,
        'tipos': TipoProduto.PRODUTO_TIPO,
        'busca': busca or '',
        'tipo_selecionado': tipo or 'TODOS',
        'ordem': ordem or '',
    }) 



# Apenas nutricionista pode cadastrar produtos no estoque
@login_required
@user_passes_test(is_nutricionista)
def cadastrar_tipo_produto(request):
    if request.method == 'POST':
        form = TipoProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_tipos_produto')
    else:
        form = TipoProdutoForm()
    
    return render(request, 'produtos/cadastrar_tipo.html', {'form': form})


# Apenas nutricionista ou secretário pode listar lotes de produtos no estoque
@login_required
@user_passes_test(is_secretario_or_nutricionista)
def listar_lotes(request, tipo_produto_id):
    tipo_produto = get_object_or_404(TipoProduto, pk=tipo_produto_id)
    lotes = tipo_produto.lote_set.all()
    
    return render(request, 'produtos/listar_lotes.html', {
        'tipo_produto': tipo_produto,
        'lotes': lotes,
    })
    


# Apenas nutricionista pode cadastrar lotes de produtos no estoque
@login_required
@user_passes_test(is_nutricionista)
def cadastrar_lote(request, tipo_produto_id):
    tipo_produto = get_object_or_404(TipoProduto, pk=tipo_produto_id)
    if request.method == 'POST':
        form = Loteform(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.tipo_produto = tipo_produto
            lote.save()
            return redirect('listar_lotes', tipo_produto_id=tipo_produto_id)
    else:
        form = Loteform()
        
    return render(request, 'produtos/cadastrar_lote.html', {'form': form, 'tipo_produto': tipo_produto})



# Apenas nutricionista pode editar tipos de produtos no estoque
@login_required
@user_passes_test(is_nutricionista)
def editar_tipo_produto(request, tipo_produto_id):
    tipo_produto = get_object_or_404(TipoProduto, pk=tipo_produto_id)
    
    if request.method == 'POST':
        form = TipoProdutoForm(request.POST, instance=tipo_produto)
        if form.is_valid():
            form.save()
            return redirect('listar_tipos_produto')
    else:
        form = TipoProdutoForm(instance=tipo_produto)
        
    return render(request, 'produtos/cadastrar_tipo.html', {
        'form': form, 
        'editar': True
    })
    
    

# Apenas nutricionista pode excluir tipos de produtos no estoque
@login_required
@user_passes_test(is_nutricionista)
def excluir_tipo_produto(request, tipo_produto_id):
    tipo_produto = get_object_or_404(TipoProduto, pk=tipo_produto_id)
    
    if request.method == 'POST':
        tipo_produto.delete()
        return redirect('listar_tipos_produto')

    return render(request, 'produtos/excluir_tipo.html', {'tipo_produto': tipo_produto}) 



# Apenas nutricionista pode baixar produtos do estoque
@login_required
@user_passes_test(is_nutricionista)
def baixar_estoque(request, lote_id):
    lote = get_object_or_404(Lote, pk=lote_id)
    
    if request.method == 'POST':
        quantidade_remover = int(request.POST.get('quantidade', 0))
        
        if quantidade_remover <= 0:
            error = "Informe um valor positivo."
        elif quantidade_remover > lote.quantidade:
            error = "Não há unidades suficientes no estoque."
        else:
            lote.quantidade -= quantidade_remover
            lote.save()
            return redirect('listar_lotes', tipo_produto_id=lote.tipo_produto.id)
        
        return render(request, 'produtos/baixar_estoque.html', {
            'lote': lote,
            'error': error
        })
    
    return render(request, 'produtos/baixar_estoque.html', {'lote': lote})



# Apenas nutricionista pode editar lotes do estoque
@login_required
@user_passes_test(is_nutricionista)
def editar_lote(request, lote_id):
    lote = get_object_or_404(Lote, pk=lote_id)
    
    if request.method == 'POST':
        form = Loteform(request.POST, instance=Lote)
        if form.is_valid():
            form.save()
            return redirect('listar_lotes', tipo_produto_id=lote.tipo_produto.id)
    else:
        form = Loteform(instance=lote)
        
    return render(request, 'produtos/cadastrar_lote.html', {
        'form': form, 
        'editar': True,
        'lote': lote,
        'tipo_produto': lote.tipo_produto,
    })



# Apenas nutricionista pode excluir lotes do estoque
@login_required
@user_passes_test(is_nutricionista)
def excluir_lote(request, lote_id):
    lote = get_object_or_404(Lote, pk=lote_id)
    
    if request.method == 'POST':
        lote.delete()
        return redirect('listar_lotes', tipo_produto_id=lote.tipo_produto.id)
    
    return render(request, 'produtos/excluir_lote.html', {'lote': lote})



# Apenas nutricionista ou secretário pode exportar relatórios
@login_required
@user_passes_test(is_secretario_or_nutricionista)
def exportar_excel(request):
    book = openpyxl.Workbook()
    activation = book.active
    activation.title = 'Produtos'
    
    activation.append(['Nome', 'Tipo', 'Quantidade', 'Fabricação', 'Validade', 'observações'])
    
    for produto in TipoProduto.objects.all():
        activation.append([
            produto.nome,
            produto.tipo, 
            produto.quantidade,
            produto.data_fabricacao.strftime('%d/%m/%Y'),
            produto.data_validade.strftime('%d/%m/%Y'),
            produto.observacoes or ''
        ])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=produtos.xlsx'
    book.save(response)
    return response


@login_required
@user_passes_test(is_secretario_or_nutricionista)
def exportar_pdf(request):
    produtos = TipoProduto.objects.all()
    template = get_template('produtos/relatorio_pdf.html')
    html = template.render({'produtos': produtos})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=relatorio_produtos.pdf'
    
    pisa.CreatePDF(html, dest=response)
    return response