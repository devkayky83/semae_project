from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from .forms import UsuarioCadastroForm, UsuarioLoginForm
from django.conf import settings
from .models import Usuario
from .forms import UsuarioForm

# Verifica se o usuário é secretário (para controle de acesso)
def is_secretario(user):
    return user.is_secretario()

# Apenas secretário pode ver a lista de usuários
@login_required
@user_passes_test(is_secretario)
def lista_usuarios(request: HttpRequest) -> HttpResponse: #Lista de usuários
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


# Apenas secretário pode criar novos usuários
@login_required
@user_passes_test(is_secretario)
def criar_usuario(request: HttpRequest) -> HttpResponse: #Cadastro de usuário
    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_usuarios') 
    else:
        form = UsuarioCadastroForm()
            
    return render(request, 'usuarios/criar.html', {'form': form})


#Login de usuário
def login_usuario(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UsuarioLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else: # Este 'else' lida com requisições GET
        form = UsuarioLoginForm()
    
    # Este 'return' é o que lida com requisições GET e com formulários inválidos
    return render(request, 'usuarios/login.html', {'form': form})
    

#Logout de usuário
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL) # Redireciona para a página de login após o logout


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'


@login_required
@user_passes_test(is_secretario)
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save() 
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {
        'form': form,
        'usuario': usuario,
    })

@login_required
@user_passes_test(is_secretario)
def excluir_usuario(request, id):
    # Busca o usuário pelo ID ou retorna um erro 404
    usuario = get_object_or_404(Usuario, pk=id)

    if request.method == 'POST':
        usuario.delete()
        # Redireciona para a lista de usuários
        return redirect('lista_usuarios')

    return render(request, 'usuarios/excluir.html', {'usuario': usuario})
