from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

class UsuarioCadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ['username', 'email', 'cargo']
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Digite o usuário'}),
            'email': forms.EmailInput(attrs={'class': 'custom-input'}),
            'cargo': forms.Select(attrs={
                'class': 'custom-select', 
                'id': 'id_cargo',
                'onchange': 'toggleEscolaField()'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'custom-input', 'placeholder': 'Digite a senha'})
        self.fields['password2'].widget.attrs.update({'class': 'custom-input', 'placeholder': 'Confirme a senha'})
        
        

class UsuarioEditForm(forms.ModelForm):
    nome_escola = forms.CharField(
        label="Nome Oficial da Escola",
        required=False,
        widget=forms.TextInput(attrs={'class': 'custom-input', 'id': 'id_nome_escola'})
    )
    
    nova_senha = forms.CharField(
        label="Redefinir Senha", 
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'custom-input', 'placeholder': 'Deixe em branco para manter a atual'})
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cargo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'custom-input'}),
            'email': forms.EmailInput(attrs={'class': 'custom-input'}),
            'cargo': forms.Select(attrs={'class': 'custom-select', 'id': 'id_cargo', 'onchange': 'toggleEscolaField()'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.cargo == 'DIRETOR':
            perfil = getattr(self.instance, 'escola', None)
            if perfil:
                self.fields['nome_escola'].initial = perfil.nome_escola

        
class UsuarioLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome de usuário'})
    )
    password = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Sua senha'})
    )
        

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