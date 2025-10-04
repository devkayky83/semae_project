from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TipoProduto, Lote
from .forms import TipoProdutoForm, Loteform
from xhtml2pdf import pisa
from usuarios.views import is_nutricionista, is_secretario_or_nutricionista
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Pedido, ItemPedido, TipoProduto
from .forms import ItemPedidoForm
from django.db import transaction
from django.db.models import Q

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
@user_passes_test(is_secretario_or_nutricionista)
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
@user_passes_test(is_secretario_or_nutricionista)
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
@user_passes_test(is_secretario_or_nutricionista)
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
@user_passes_test(is_secretario_or_nutricionista)
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

@login_required
@user_passes_test(lambda u: u.is_diretor())
def criar_pedido(request):

    novo_pedido = Pedido.objects.create(solicitante=request.user)
    return redirect('detalhe_pedido', pedido_id=novo_pedido.id)

@login_required
@user_passes_test(lambda u: u.is_diretor())
def detalhe_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, solicitante=request.user)
    
    if request.method == 'POST':
        form = ItemPedidoForm(request.POST)
        if form.is_valid():
            produto_selecionado = form.cleaned_data['produto']
            quantidade_adicionar = form.cleaned_data['quantidade']
            estoque_disponivel = produto_selecionado.estoque_total

            item_existente = ItemPedido.objects.filter(pedido=pedido, produto=produto_selecionado).first()

            quantidade_existente = item_existente.quantidade if item_existente else 0
            quantidade_final_desejada = quantidade_existente + quantidade_adicionar

            if quantidade_final_desejada > estoque_disponivel:
                messages.error(request, f"Estoque insuficiente para '{produto_selecionado.nome}'. "
                                        f"Disponível: {estoque_disponivel}, "
                                        f"Solicitado: {quantidade_final_desejada}.")
            else:
                if item_existente:
                    item_existente.quantidade += quantidade_adicionar
                    item_existente.save()
                    messages.success(request, f"Quantidade de '{produto_selecionado.nome}' atualizada.")
                else:
                    item = form.save(commit=False)
                    item.pedido = pedido
                    item.save()
                    messages.success(request, f"'{produto_selecionado.nome}' adicionado ao pedido.")
            
            return redirect('detalhe_pedido', pedido_id=pedido.id)
    
    form = ItemPedidoForm()
    itens_do_pedido = pedido.itens.all()
    
    context = {
        'pedido': pedido,
        'itens': itens_do_pedido,
        'form': form,
    }
    return render(request, 'pedidos/detalhe_pedido.html', context)

@login_required
@user_passes_test(lambda u: u.is_diretor())
def remover_item_pedido(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id)

    pedido_id = item.pedido.id

    if item.pedido.solicitante == request.user:
        item.delete()

        return redirect('detalhe_pedido', pedido_id=pedido_id)
    else:
        return HttpResponseForbidden("Você não tem permissão para remover este item.")

@login_required
@user_passes_test(lambda u: u.is_diretor())
def meus_pedidos(request):
    pedidos_do_diretor = Pedido.objects.filter(solicitante=request.user).order_by('-data_pedido')
    
    context = {
        'pedidos': pedidos_do_diretor
    }
    
    return render(request, 'pedidos/meus_pedidos.html', context)

from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.is_diretor())
def finalizar_pedido(request, pedido_id):

    pedido = get_object_or_404(Pedido, id=pedido_id, solicitante=request.user)

    messages.success(request, f"Pedido #{pedido.id} foi finalizado e enviado para análise!")
    return redirect('menu_diretor')

from django.db.models import Sum

@login_required
@user_passes_test(lambda u: u.is_diretor())
def listar_estoque_disponivel(request):

    produtos = TipoProduto.objects.order_by('nome')
    
    context = {
        'produtos': produtos
    }
    
    return render(request, 'produtos/estoque_disponivel.html', context)
@login_required
@user_passes_test(lambda u: u.is_diretor())
def excluir_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, solicitante=request.user)

    if request.method == 'POST':
        if pedido.status == 'PENDENTE':
            numero_pedido = pedido.id
            pedido.delete()
            messages.success(request, f"Pedido #{numero_pedido} foi excluído com sucesso.")
        else:
            messages.error(request, f"Este pedido não pode ser excluído pois seu status é '{pedido.get_status_display()}'.")

    return redirect('meus_pedidos')

@login_required
@user_passes_test(lambda u: u.is_nutricionista())
def listar_pedidos_pendentes(request):
    pedidos = Pedido.objects.filter(status='PENDENTE').order_by('data_pedido')
    context = {
        'pedidos': pedidos
    }
    return render(request, 'pedidos/listar_pedidos_pendentes.html', context)

@login_required
@user_passes_test(lambda u: u.is_nutricionista())
def detalhe_pedido_nutricionista(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    context = {
        'pedido': pedido
    }
    return render(request, 'pedidos/detalhe_pedido_nutricionista.html', context)

@login_required
@user_passes_test(lambda u: u.is_nutricionista())
def aprovar_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        try:
            with transaction.atomic():
                for item in pedido.itens.all():
                    if item.quantidade > item.produto.estoque_total:
                        raise Exception(f"Estoque insuficiente para o produto '{item.produto.nome}'.")

                for item in pedido.itens.all():
                    quantidade_a_baixar = item.quantidade
                    lotes_disponiveis = Lote.objects.filter(tipo_produto=item.produto, quantidade__gt=0).order_by('data_validade')
                    
                    for lote in lotes_disponiveis:
                        if quantidade_a_baixar == 0:
                            break
                        
                        if lote.quantidade >= quantidade_a_baixar:
                            lote.quantidade -= quantidade_a_baixar
                            quantidade_a_baixar = 0
                        else:
                            quantidade_a_baixar -= lote.quantidade
                            lote.quantidade = 0
                        lote.save()
                pedido.status = 'APROVADO'
                pedido.save()
                messages.success(request, f"Pedido #{pedido.id} aprovado e estoque atualizado!")

        except Exception as e:
            messages.error(request, f"Erro ao aprovar o pedido #{pedido.id}: {e}")

    return redirect('listar_pedidos_pendentes')


@login_required
@user_passes_test(lambda u: u.is_nutricionista())
def rejeitar_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.status = 'REJEITADO'
        pedido.save()
        messages.success(request, f"Pedido #{pedido.id} foi rejeitado.")
    return redirect('listar_pedidos_pendentes')

@login_required
@user_passes_test(lambda u: u.is_nutricionista())
def historico_pedidos(request):
    pedidos_recentes = Pedido.objects.filter(
        Q(status='APROVADO') | Q(status='REJEITADO')
    ).order_by('-data_pedido')[:20]  

    context = {
        'pedidos': pedidos_recentes
    }
    
    return render(request, 'pedidos/historico_pedidos.html', context)

