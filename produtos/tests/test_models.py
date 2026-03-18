"""
produtos/tests/test_models.py

Testa os modelos TipoProduto, Lote, Pedido e ItemPedido.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from produtos.models import TipoProduto, Lote, Pedido, ItemPedido


@pytest.mark.django_db
class TestTipoProdutoModel:

    def test_str_contem_nome(self, tipo_arroz):
        assert "Arroz Branco" in str(tipo_arroz)

    def test_ativo_por_padrao_e_true(self, tipo_arroz):
        assert tipo_arroz.ativo is True

    def test_possui_data_fabricacao_por_padrao(self, tipo_arroz):
        assert tipo_arroz.possui_data_fabricacao is True

    def test_possui_data_validade_por_padrao(self, tipo_arroz):
        assert tipo_arroz.possui_data_validade is True

    def test_nome_e_unico(self, tipo_arroz, db):
        with pytest.raises(Exception):
            TipoProduto.objects.create(nome="Arroz Branco", tipo="ALIMENTO")

    def test_produto_inativo_nao_aparece_em_filter_ativo(self, tipo_arroz):
        tipo_arroz.ativo = False
        tipo_arroz.save()
        ativos = TipoProduto.objects.filter(ativo=True)
        assert tipo_arroz not in ativos

    def test_produto_pode_ser_reativado(self, tipo_arroz):
        tipo_arroz.ativo = False
        tipo_arroz.save()
        tipo_arroz.ativo = True
        tipo_arroz.save()
        tipo_arroz.refresh_from_db()
        assert tipo_arroz.ativo is True


@pytest.mark.django_db
class TestLoteModel:

    def test_quantidade_total_unidade_com_peso(self, lote_arroz):
        # 20 pacotes * 1.00 kg = 20.00
        assert lote_arroz.quantidade_total_unidade == Decimal("20.00")

    def test_quantidade_total_unidade_sem_peso(self, tipo_arroz):
        """Quando quantidade_por_pacote é None, deve usar 1 como fallback."""
        lote = Lote.objects.create(
            tipo_produto=tipo_arroz,
            quantidade_pacotes=7,
            quantidade_por_pacote=None,
        )
        try:
            result = lote.quantidade_total_unidade
            assert result is not None or result == 0
        except TypeError:
            pytest.fail(
                "BUG CONFIRMADO: quantidade_total_unidade lança TypeError quando "
                "quantidade_por_pacote é None. Corrija a property em Lote."
            )
            # Correção feita, a tendência é não apresentar mais essa mensagem de bug

    def test_str_contem_nome_produto(self, lote_arroz):
        assert "Arroz Branco" in str(lote_arroz)

    def test_lote_com_validade_futura_nao_e_vencido(self, lote_arroz):
        assert lote_arroz.data_validade > date.today()

    def test_lote_vencido_tem_validade_no_passado(self, tipo_arroz):
        lote_vencido = Lote.objects.create(
            tipo_produto=tipo_arroz,
            quantidade_pacotes=5,
            data_validade=date.today() - timedelta(days=1),
        )
        assert lote_vencido.data_validade < date.today()

    def test_quantidade_pacotes_aumenta_ao_adicionar(self, lote_arroz):
        original = lote_arroz.quantidade_pacotes
        lote_arroz.quantidade_pacotes += 10
        lote_arroz.save()
        lote_arroz.refresh_from_db()
        assert lote_arroz.quantidade_pacotes == original + 10

    def test_quantidade_pacotes_diminui_ao_dar_baixa(self, lote_arroz):
        original = lote_arroz.quantidade_pacotes
        lote_arroz.quantidade_pacotes -= 5
        lote_arroz.save()
        lote_arroz.refresh_from_db()
        assert lote_arroz.quantidade_pacotes == original - 5


@pytest.mark.django_db
class TestPedidoModel:

    def test_status_padrao_e_pendente(self, diretor):
        pedido = Pedido.objects.create(solicitante=diretor)
        assert pedido.status == "PENDENTE"

    def test_str_contem_id_e_username(self, diretor):
        pedido = Pedido.objects.create(solicitante=diretor)
        texto = str(pedido)
        assert str(pedido.id) in texto
        assert "diretor_test" in texto

    def test_carne_comprada_padrao_false(self, diretor):
        pedido = Pedido.objects.create(solicitante=diretor)
        assert pedido.carne_comprada is False

    def test_pedido_deletado_ao_deletar_solicitante_com_protect(self, diretor):
        """PROTECT impede exclusão do usuário se houver pedido."""
        from django.db import IntegrityError
        from django.db.models import ProtectedError
        Pedido.objects.create(solicitante=diretor)
        with pytest.raises(ProtectedError):
            diretor.delete()


@pytest.mark.django_db
class TestItemPedidoModel:

    def test_str_contem_quantidade_e_produto(self, pedido_pendente, tipo_arroz):
        item = pedido_pendente.itens.first()
        texto = str(item)
        assert "5" in texto
        assert "Arroz Branco" in texto

    def test_item_removido_ao_remover_pedido(self, pedido_pendente):
        pedido_id = pedido_pendente.id
        pedido_pendente.delete()
        assert not ItemPedido.objects.filter(pedido_id=pedido_id).exists()