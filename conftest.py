import pytest
from decimal import Decimal
from datetime import date, timedelta

from usuarios.models import Usuario, PerfilEscola
from produtos.models import TipoProduto, Lote, Pedido, ItemPedido


# ─────────────────────────────────────────────
#  Fixtures de Usuários
# ─────────────────────────────────────────────

@pytest.fixture
def secretario(db):
    return Usuario.objects.create_user(
        username="secretario_test",
        password="senha_forte_123",
        cargo="SECRETARIO",
    )


@pytest.fixture
def nutricionista(db):
    return Usuario.objects.create_user(
        username="nutri_test",
        password="senha_forte_123",
        cargo="NUTRICIONISTA",
    )


@pytest.fixture
def diretor(db):
    user = Usuario.objects.create_user(
        username="diretor_test",
        password="senha_forte_123",
        cargo="DIRETOR",
    )
    PerfilEscola.objects.create(usuario=user, nome_escola="E.M. Teste")
    return user


# ─────────────────────────────────────────────
#  Fixtures de Produtos / Estoque
# ─────────────────────────────────────────────

@pytest.fixture
def tipo_arroz(db):
    return TipoProduto.objects.create(
        nome="Arroz Branco",
        tipo="ALIMENTO",
        unidade_medida="KG",
        origem_compra="COMUM",
    )


@pytest.fixture
def tipo_feijao(db):
    return TipoProduto.objects.create(
        nome="Feijão Preto",
        tipo="ALIMENTO",
        unidade_medida="KG",
        origem_compra="AGRICULTURA",
    )


@pytest.fixture
def lote_arroz(db, tipo_arroz):
    return Lote.objects.create(
        tipo_produto=tipo_arroz,
        quantidade_pacotes=20,
        quantidade_por_pacote=Decimal("1.00"),
        preco_unitario=Decimal("5.00"),
        data_validade=date.today() + timedelta(days=90),
    )


# ─────────────────────────────────────────────
#  Fixtures de Pedidos
# ─────────────────────────────────────────────

@pytest.fixture
def pedido_pendente(db, diretor, tipo_arroz, lote_arroz):
    pedido = Pedido.objects.create(solicitante=diretor)
    ItemPedido.objects.create(pedido=pedido, produto=tipo_arroz, quantidade=5)
    return pedido