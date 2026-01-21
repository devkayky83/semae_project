from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.conf import settings
from django.db import transaction

from .models import Usuario, PerfilEscola
from .forms import UsuarioCadastroForm, UsuarioEditForm, UsuarioLoginForm


#Apenas secretário pode acessar seu próprio menu
@login_required
@user_passes_test(lambda u: u.is_secretario())
def menu_secretario(request):
    return render(request, 'usuarios/menu_secretario.html')



#Apenas diretor pode acessar seu próprio menu
@login_required
@user_passes_test(lambda u: u.is_diretor())
def menu_diretor(request):
    return render(request, 'usuarios/menu_diretor.html')



#Aénas nutricionista pode acessar seu próprio menu
@login_required
@user_passes_test(lambda u: u.is_nutricionista())
def menu_nutricionista(request):
    return render(request, 'usuarios/menu_nutricionista.html')

def is_secretario(user):
    return user.is_secretario() and user.cargo == "SECRETARIO"

def is_nutricionista(user):
    return user.is_nutricionista() and user.cargo == "NUTRICIONISTA"

def is_secretario_or_nutricionista(user):
    return user.is_authenticated and (user.cargo == 'SECRETARIO' or user.cargo == 'NUTRICIONISTA')



# Apenas secretário pode ver a lista de usuários
@login_required
@user_passes_test(is_secretario)
def lista_usuarios(request: HttpRequest) -> HttpResponse: #Lista de usuários
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})



# Apenas secretário pode criar novos usuários
@login_required
@user_passes_test(is_secretario)
def criar_usuario(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)
        
        if form.is_valid():
            with transaction.atomic():            
                novo_usuario = form.save()
                cargo_selecionado = novo_usuario.cargo 
                
                if cargo_selecionado == 'SECRETARIO':
                    grupo, _ = Group.objects.get_or_create(name='Secretário')
                    novo_usuario.groups.add(grupo)
                    
                elif cargo_selecionado == 'NUTRICIONISTA':
                    grupo, _ = Group.objects.get_or_create(name='Nutricionista')
                    novo_usuario.groups.add(grupo)
                    
                elif cargo_selecionado == 'DIRETOR':
                    grupo, _ = Group.objects.get_or_create(name='Diretor')
                    novo_usuario.groups.add(grupo)
                    
                    nome_da_escola = request.POST.get('nome_escola')
                    if nome_da_escola:
                        PerfilEscola.objects.create(
                            usuario=novo_usuario,
                            nome_escola=nome_da_escola
                        )
                
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
    else: 
        form = UsuarioLoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})
    


#Logout de usuário
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL) 
 


#Permite que cada usuário acesse seu respectivo painel
class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = UsuarioLoginForm

    def get_success_url(self):
        user = self.request.user

        if user.is_secretario():
            return reverse_lazy('menu_secretario')
        
        elif user.is_diretor():
            return reverse_lazy('menu_diretor')

        elif user.is_nutricionista():
            return reverse_lazy('menu_nutricionista')
        
        else:
            return reverse_lazy('login')



#Apenas secretário pode editar os usuários do sistema
@login_required
@user_passes_test(is_secretario)
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)
            
            nova_senha = form.cleaned_data.get('nova_senha')
            if nova_senha:
                user.set_password(nova_senha)
            
            user.save()

            if user.cargo == 'DIRETOR':
                nome_escola = form.cleaned_data.get('nome_escola')
                PerfilEscola.objects.update_or_create(
                    usuario=user, 
                    defaults={'nome_escola': nome_escola}
                )
            else:
                # Se mudou de diretor para outro cargo, removemos o vínculo da escola
                PerfilEscola.objects.filter(usuario=user).delete()

            return redirect('lista_usuarios')
    else:
        form = UsuarioEditForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {'form': form, 'usuario': usuario})



#Apenas secretário pode excluir usuários do sistema
@login_required
@user_passes_test(is_secretario)
def excluir_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        
        return redirect('lista_usuarios')

    return render(request, 'usuarios/excluir.html', {'usuario': usuario})



#Direcionador de menu
@login_required
def menu_principal(request: HttpRequest) -> HttpResponse:
    if request.user.cargo == 'SECRETARIO':
        return render(request, 'usuarios/menu_secretario.html')
    elif request.user.cargo == 'NUTRICIONISTA':
        return render(request, 'usuarios/menu_nutricionista.html')
    elif request.user.cargo == 'DIRETOR':
        return render(request, 'usuarios/menu_diretor.html')
    else:
        return redirect('logout_usuario')
