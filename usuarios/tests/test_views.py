"""
usuarios/tests/test_views.py

Testa controle de acesso (RBAC) e comportamento das views de usuário.
"""
import pytest
from django.urls import reverse

from usuarios.models import Usuario, PerfilEscola


# ─────────────────────────────────────────────
#  ACESSO SEM LOGIN
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRedirectSemLogin:
    """Rotas protegidas devem redirecionar para login quando não autenticado."""

    def test_lista_usuarios_redireciona_sem_login(self, client):
        response = client.get(reverse("lista_usuarios"))
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_criar_usuario_redireciona_sem_login(self, client):
        response = client.get(reverse("criar_usuario"))
        assert response.status_code == 302

    def test_menu_secretario_redireciona_sem_login(self, client):
        response = client.get(reverse("menu_secretario"))
        assert response.status_code == 302

    def test_menu_diretor_redireciona_sem_login(self, client):
        response = client.get(reverse("menu_diretor"))
        assert response.status_code == 302

    def test_menu_nutricionista_redireciona_sem_login(self, client):
        response = client.get(reverse("menu_nutricionista"))
        assert response.status_code == 302


# ─────────────────────────────────────────────
#  CONTROLE DE ACESSO POR CARGO
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestAcessoSecretario:
    """Secretário deve ter acesso às suas rotas e ser bloqueado nas dos outros."""

    def test_secretario_acessa_lista_usuarios(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("lista_usuarios"))
        assert response.status_code == 200

    def test_secretario_acessa_menu_secretario(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("menu_secretario"))
        assert response.status_code == 200

    def test_secretario_nao_acessa_menu_diretor(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("menu_diretor"))
        assert response.status_code == 302  # Bloqueado e redirecionado

    def test_secretario_nao_acessa_menu_nutricionista(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("menu_nutricionista"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestAcessoDiretor:
    """Diretor deve acessar apenas suas rotas."""

    def test_diretor_acessa_menu_diretor(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("menu_diretor"))
        assert response.status_code == 200

    def test_diretor_nao_acessa_lista_usuarios(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("lista_usuarios"))
        assert response.status_code == 302

    def test_diretor_nao_acessa_menu_secretario(self, client, diretor):
        client.login(username="diretor_test", password="senha_forte_123")
        response = client.get(reverse("menu_secretario"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestAcessoNutricionista:
    """Nutricionista deve acessar apenas suas rotas."""

    def test_nutricionista_acessa_menu_nutricionista(self, client, nutricionista):
        client.login(username="nutri_test", password="senha_forte_123")
        response = client.get(reverse("menu_nutricionista"))
        assert response.status_code == 200

    def test_nutricionista_nao_acessa_lista_usuarios(self, client, nutricionista):
        client.login(username="nutri_test", password="senha_forte_123")
        response = client.get(reverse("lista_usuarios"))
        assert response.status_code == 302


# ─────────────────────────────────────────────
#  CRUD DE USUÁRIOS (apenas secretário)
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestCriarUsuario:
    """Testa criação de usuários pelo secretário."""

    def test_secretario_cria_nutricionista(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.post(
            reverse("criar_usuario"),
            {
                "username": "nova_nutri",
                "email": "nutri@escola.com",
                "cargo": "NUTRICIONISTA",
                "password1": "Djang0Pass!",
                "password2": "Djang0Pass!",
            },
        )
        assert response.status_code == 302  # Redireciona após sucesso
        assert Usuario.objects.filter(username="nova_nutri").exists()

    def test_secretario_cria_diretor_com_escola(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        client.post(
            reverse("criar_usuario"),
            {
                "username": "novo_dir",
                "email": "dir@escola.com",
                "cargo": "DIRETOR",
                "nome_escola": "E.M. São José",
                "password1": "Djang0Pass!",
                "password2": "Djang0Pass!",
            },
        )
        usuario = Usuario.objects.get(username="novo_dir")
        assert PerfilEscola.objects.filter(usuario=usuario, nome_escola="E.M. São José").exists()

    def test_username_duplicado_retorna_formulario_com_erro(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.post(
            reverse("criar_usuario"),
            {
                "username": "secretario_test",  # Já existe
                "email": "outro@email.com",
                "cargo": "NUTRICIONISTA",
                "password1": "Djang0Pass!",
                "password2": "Djang0Pass!",
            },
        )
        # Deve voltar ao formulário (status 200), não redirecionar
        assert response.status_code == 200


@pytest.mark.django_db
class TestExcluirUsuario:
    """Testa exclusão de usuários."""

    def test_secretario_exclui_usuario(self, client, secretario, nutricionista):
        client.login(username="secretario_test", password="senha_forte_123")
        client.post(reverse("excluir_usuario", args=[nutricionista.pk]))
        assert not Usuario.objects.filter(pk=nutricionista.pk).exists()

    def test_diretor_nao_pode_excluir_usuario(self, client, diretor, nutricionista):
        client.login(username="diretor_test", password="senha_forte_123")
        client.post(reverse("excluir_usuario", args=[nutricionista.pk]))
        # nutricionista deve continuar existindo
        assert Usuario.objects.filter(pk=nutricionista.pk).exists()


# ─────────────────────────────────────────────
#  LOGIN / LOGOUT
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestLoginRedirect:
    """Login deve redirecionar para o menu correto de cada cargo."""

    def test_secretario_redireciona_para_menu_secretario(self, client, secretario):
        response = client.post(
            reverse("login"),
            {"username": "secretario_test", "password": "senha_forte_123"},
        )
        assert response.status_code == 302
        assert "secretario" in response["Location"]

    def test_diretor_redireciona_para_menu_diretor(self, client, diretor):
        response = client.post(
            reverse("login"),
            {"username": "diretor_test", "password": "senha_forte_123"},
        )
        assert response.status_code == 302
        assert "diretor" in response["Location"]

    def test_nutricionista_redireciona_para_menu_nutricionista(self, client, nutricionista):
        response = client.post(
            reverse("login"),
            {"username": "nutri_test", "password": "senha_forte_123"},
        )
        assert response.status_code == 302
        assert "nutricionista" in response["Location"]

    def test_logout_redireciona_para_login(self, client, secretario):
        client.login(username="secretario_test", password="senha_forte_123")
        response = client.get(reverse("logout_usuario"))
        assert response.status_code == 302