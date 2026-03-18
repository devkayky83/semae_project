"""
usuarios/tests/test_models.py

Testa os modelos Usuario e PerfilEscola.
"""
import pytest
from django.db import IntegrityError

from usuarios.models import Usuario, PerfilEscola


@pytest.mark.django_db
class TestUsuarioModel:
    """Testes para o modelo customizado de usuário."""

    def test_is_secretario_retorna_true_para_cargo_correto(self, secretario):
        assert secretario.is_secretario() is True

    def test_is_secretario_retorna_false_para_outros_cargos(self, diretor, nutricionista):
        assert diretor.is_secretario() is False
        assert nutricionista.is_secretario() is False

    def test_is_diretor_retorna_true_para_cargo_correto(self, diretor):
        assert diretor.is_diretor() is True

    def test_is_diretor_retorna_false_para_outros_cargos(self, secretario, nutricionista):
        assert secretario.is_diretor() is False
        assert nutricionista.is_diretor() is False

    def test_is_nutricionista_retorna_true_para_cargo_correto(self, nutricionista):
        assert nutricionista.is_nutricionista() is True

    def test_is_nutricionista_retorna_false_para_outros_cargos(self, secretario, diretor):
        assert secretario.is_nutricionista() is False
        assert diretor.is_nutricionista() is False

    def test_username_deve_ser_unico(self, secretario):
        with pytest.raises(Exception):  # IntegrityError ou ValidationError
            Usuario.objects.create_user(
                username="secretario_test",  # mesmo username da fixture
                password="outra_senha",
                cargo="SECRETARIO",
            )

    def test_usuario_criado_com_cargo_correto(self, diretor):
        assert diretor.cargo == "DIRETOR"

    def test_usuario_pode_fazer_login_com_senha_correta(self, client, secretario):
        logado = client.login(username="secretario_test", password="senha_forte_123")
        assert logado is True

    def test_usuario_nao_faz_login_com_senha_errada(self, client, secretario):
        logado = client.login(username="secretario_test", password="senha_errada")
        assert logado is False


@pytest.mark.django_db
class TestPerfilEscolaModel:
    """Testes para o perfil vinculado ao diretor."""

    def test_str_retorna_nome_da_escola(self, diretor):
        assert str(diretor.escola) == "E.M. Teste"

    def test_relacionamento_one_to_one_com_usuario(self, diretor):
        assert diretor.escola.usuario == diretor

    def test_diretor_sem_escola_nao_tem_atributo_escola(self, db):
        diretor_sem_escola = Usuario.objects.create_user(
            username="dir_sem_escola",
            password="senha",
            cargo="DIRETOR",
        )
        assert not hasattr(diretor_sem_escola, "escola") or \
               not PerfilEscola.objects.filter(usuario=diretor_sem_escola).exists()

    def test_deletar_usuario_deleta_perfil_escola(self, diretor):
        perfil_id = diretor.escola.id
        diretor.delete()
        assert not PerfilEscola.objects.filter(id=perfil_id).exists()