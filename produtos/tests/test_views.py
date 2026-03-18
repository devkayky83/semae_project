"""
produtos/tests/test_views.py

Testa controle de acesso e lógica de negócio das views de produtos/pedidos.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.urls import reverse

from produtos.models import TipoProduto, Lote, Pedido, ItemPedido


# ─────────────────────────────────────────────
#  CONTROLE DE ACESSO — ESTOQUE
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestAcessoEstoque:
    """Estoque é visível para secretário e nutricionista, não para diretor."""

    def test_nutricionista_acessa_lista_tipos(self, client, nutricionista):
        client.login(username="nutri_test", password="senha_forte_123")
        response = client.get(reverse("listar_tipos_produto"))
        assert response.status_code == 200

    def test_secretario_acessa_lista_tipos(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("listar_tipos_produto"))
        assert response.status_code == 200

    def test_diretor_nao_acessa_lista_tipos(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("listar_tipos_produto"))
        assert response.status_code == 302

    def test_diretor_acessa_estoque_disponivel(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("estoque_disponivel"))
        assert response.status_code == 200

    def test_nutricionista_pode_cadastrar_tipo_produto(self, client, nutricionista):
        client.login(username="nutri_test", password="senha_forte_123")
        response = client.post(
            reverse("cadastrar_tipo_produto"),
            {
                "nome": "Macarrão",
                "tipo": "ALIMENTO",
                "unidade_medida": "KG",
                "origem_compra": "COMUM",
                "possui_data_fabricacao": True,
                "possui_data_validade": True,
            },
        )
        assert response.status_code == 302
        assert TipoProduto.objects.filter(nome="Macarrão").exists()

    def test_secretario_nao_pode_cadastrar_tipo_produto(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.post(
            reverse("cadastrar_tipo_produto"),
            {"nome": "Produto Bloqueado", "tipo": "ALIMENTO"},
        )
        assert response.status_code == 302
        assert not TipoProduto.objects.filter(nome="Produto Bloqueado").exists()


# ─────────────────────────────────────────────
#  CONTROLE DE ACESSO — PEDIDOS
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestAcessoPedidos:

    def test_diretor_cria_pedido_e_redireciona(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("criar_pedido"))
        # View cria o pedido e redireciona para detalhe
        assert response.status_code == 302
        assert Pedido.objects.filter(solicitante=diretor).exists()

    def test_nutricionista_nao_pode_criar_pedido(self, client, nutricionista):
        client.login(username="nutri_test", password="senha_forte_123")
        response = client.get(reverse("criar_pedido"))
        assert response.status_code == 302
        assert not Pedido.objects.filter(solicitante=nutricionista).exists()

    def test_secretario_nao_pode_criar_pedido(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("criar_pedido"))
        assert response.status_code == 302

    def test_nutricionista_acessa_pedidos_pendentes(self, client, nutricionista):
        client.login(username="nutri_test", password="senha_forte_123")
        response = client.get(reverse("listar_pedidos_pendentes"))
        assert response.status_code == 200

    def test_diretor_nao_acessa_pedidos_pendentes(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("listar_pedidos_pendentes"))
        assert response.status_code == 302

    def test_diretor_acessa_seus_proprios_pedidos(self, client, diretor, pedido_pendente):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("meus_pedidos"))
        assert response.status_code == 200

    def test_diretor_nao_acessa_pedido_de_outro_diretor(self, client, db, pedido_pendente):
        outro_diretor = __import__("usuarios.models", fromlist=["Usuario"]).Usuario.objects.create_user(
            username="outro_dir", password="senha", cargo="DIRETOR"
        )
        client.login(username="outro_dir", password="senha")
        response = client.get(reverse("detalhe_pedido", args=[pedido_pendente.id]))
        assert response.status_code == 404


# ─────────────────────────────────────────────
#  LÓGICA DE NEGÓCIO — APROVAR PEDIDO
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestAprovarPedido:
    """
    O fluxo mais crítico do sistema:
    aprovar um pedido deve debitar o estoque dos lotes (FIFO por validade).
    """

    def test_aprovacao_desconta_estoque_do_lote(
        self, client, nutricionista, pedido_pendente, lote_arroz
    ):
        client.login(username="nutri_test", password="senha_forte_123")
        client.post(reverse("aprovar_pedido", args=[pedido_pendente.id]))

        lote_arroz.refresh_from_db()
        assert lote_arroz.quantidade_pacotes == 15  # 20 - 5

    def test_aprovacao_muda_status_para_aprovado(
        self, client, nutricionista, pedido_pendente
    ):
        client.login(username="nutri_test", password="senha_forte_123")
        client.post(reverse("aprovar_pedido", args=[pedido_pendente.id]))

        pedido_pendente.refresh_from_db()
        assert pedido_pendente.status == "APROVADO"

    def test_aprovacao_com_estoque_insuficiente_nao_altera_nada(
        self, client, nutricionista, diretor, tipo_arroz, lote_arroz
    ):
        """Pedido maior que o estoque: status permanece PENDENTE, lote intacto."""
        pedido = Pedido.objects.create(solicitante=diretor)
        ItemPedido.objects.create(pedido=pedido, produto=tipo_arroz, quantidade=999)

        client.login(username="nutri_test", password="senha_forte_123")
        client.post(reverse("aprovar_pedido", args=[pedido.id]))

        pedido.refresh_from_db()
        lote_arroz.refresh_from_db()
        assert pedido.status == "PENDENTE"
        assert lote_arroz.quantidade_pacotes == 20

    def test_aprovacao_consome_multiplos_lotes_em_ordem_de_validade(
        self, client, nutricionista, diretor, tipo_arroz
    ):
        """
        Com dois lotes, o mais próximo do vencimento deve ser consumido primeiro (FIFO).
        """
        lote_proximo = Lote.objects.create(
            tipo_produto=tipo_arroz,
            quantidade_pacotes=3,
            data_validade=date.today() + timedelta(days=10),
        )
        lote_distante = Lote.objects.create(
            tipo_produto=tipo_arroz,
            quantidade_pacotes=10,
            data_validade=date.today() + timedelta(days=180),
        )
        pedido = Pedido.objects.create(solicitante=diretor)
        ItemPedido.objects.create(pedido=pedido, produto=tipo_arroz, quantidade=5)

        client.login(username="nutri_test", password="senha_forte_123")
        client.post(reverse("aprovar_pedido", args=[pedido.id]))

        lote_proximo.refresh_from_db()
        lote_distante.refresh_from_db()

        # Lote próximo foi zerado (tinha 3), lote distante perdeu 2 (5 - 3)
        assert lote_proximo.quantidade_pacotes == 0
        assert lote_distante.quantidade_pacotes == 8

    def test_pedido_ja_aprovado_nao_pode_ser_aprovado_novamente(
        self, client, nutricionista, diretor, tipo_arroz, lote_arroz
    ):
        pedido = Pedido.objects.create(solicitante=diretor, status="APROVADO")
        ItemPedido.objects.create(pedido=pedido, produto=tipo_arroz, quantidade=1)

        client.login(username="nutri_test", password="senha_forte_123")
        client.post(reverse("aprovar_pedido", args=[pedido.id]))

        lote_arroz.refresh_from_db()
        assert lote_arroz.quantidade_pacotes == 20  # Não foi descontado


# ─────────────────────────────────────────────
#  LÓGICA DE NEGÓCIO — REJEITAR PEDIDO
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRejeitarPedido:

    def test_rejeitar_muda_status_para_rejeitado(
        self, client, nutricionista, pedido_pendente
    ):
        client.login(username="nutri_test", password="senha_forte_123")
        client.post(
            reverse("rejeitar_pedido", args=[pedido_pendente.id]),
            {"justificativa": "Produto em falta nesta semana."},
        )
        pedido_pendente.refresh_from_db()
        assert pedido_pendente.status == "REJEITADO"

    def test_rejeitar_salva_justificativa(
        self, client, nutricionista, pedido_pendente
    ):
        client.login(username="nutri_test", password="senha_forte_123")
        client.post(
            reverse("rejeitar_pedido", args=[pedido_pendente.id]),
            {"justificativa": "Estoque insuficiente de arroz."},
        )
        pedido_pendente.refresh_from_db()
        assert "Estoque insuficiente" in pedido_pendente.justificativa_rejeicao

    def test_rejeitar_nao_altera_estoque(
        self, client, nutricionista, pedido_pendente, lote_arroz
    ):
        client.login(username="nutri_test", password="senha_forte_123")
        client.post(
            reverse("rejeitar_pedido", args=[pedido_pendente.id]),
            {"justificativa": "Motivo qualquer."},
        )
        lote_arroz.refresh_from_db()
        assert lote_arroz.quantidade_pacotes == 20  # Intacto


# ─────────────────────────────────────────────
#  LÓGICA DE NEGÓCIO — EXCLUIR PEDIDO
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestExcluirPedido:

    def test_diretor_exclui_pedido_pendente(self, client, diretor, pedido_pendente):
        pedido_id = pedido_pendente.id
        client.login(username="diretor_test", password="senha_forte_123")
        client.post(reverse("excluir_pedido", args=[pedido_id]))
        assert not Pedido.objects.filter(id=pedido_id).exists()

    def test_diretor_nao_exclui_pedido_aprovado(self, client, diretor, pedido_pendente):
        pedido_pendente.status = "APROVADO"
        pedido_pendente.save()

        client.login(username="diretor_test", password="senha_forte_123")
        client.post(reverse("excluir_pedido", args=[pedido_pendente.id]))
        assert Pedido.objects.filter(id=pedido_pendente.id).exists()

    def test_diretor_nao_exclui_pedido_de_outro(self, client, db, pedido_pendente):
        from usuarios.models import Usuario
        outro = Usuario.objects.create_user(
            username="dir_outro", password="senha", cargo="DIRETOR"
        )
        client.login(username="dir_outro", password="senha")
        client.post(reverse("excluir_pedido", args=[pedido_pendente.id]))
        # Pedido não é dele; deve retornar 404 e o pedido permanecer
        assert Pedido.objects.filter(id=pedido_pendente.id).exists()


# ─────────────────────────────────────────────
#  COMPRAS DIRETAS (Secretário)
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestComprasDiretas:

    def test_secretario_acessa_lista_compras(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("lista_compras_secretario"))
        assert response.status_code == 200

    def test_diretor_nao_acessa_lista_compras(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("lista_compras_secretario"))
        assert response.status_code == 302

    def test_marcar_carne_comprada(self, client, secretario, diretor):
        pedido = Pedido.objects.create(
            solicitante=diretor, observacao_carne="20kg Acém"
        )
        client.login(username="secretario_test", password="senha_forte_123")
        client.get(reverse("marcar_carne_comprada", args=[pedido.id]))
        pedido.refresh_from_db()
        assert pedido.carne_comprada is True

    def test_negar_compra_direta_salva_justificativa(self, client, secretario, diretor):
        pedido = Pedido.objects.create(
            solicitante=diretor, observacao_carne="10kg Frango"
        )
        client.login(username="secretario_test", password="senha_forte_123")
        client.post(
            reverse("negar_compra_direta", args=[pedido.id]),
            {"justificativa_secretario": "Verba insuficiente no mês."},
        )
        pedido.refresh_from_db()
        assert "Verba insuficiente" in pedido.justificativa_secretario
        assert pedido.carne_comprada is True  # Marcado como processado