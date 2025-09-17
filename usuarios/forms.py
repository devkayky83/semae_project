from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

class UsuarioCadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cargo', 'password1', 'password2']
        
class UsuarioLoginForm(AuthenticationForm):
        pass

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        # CORREÇÃO: Usando os nomes de campo REAIS do modelo Django ('first_name', 'last_name')
        fields = ['username', 'email', 'cargo']

        labels = {
            'username': 'Nome de Usuário',
            'email': 'E-mail',
            'cargo': 'Cargo',
        }