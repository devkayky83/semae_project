from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    FUNCOES = (
        ('SECRETARIO', 'Secretario'),
        ('DIRETOR', 'Diretor'),
        ('NUTRICIONISTA', 'Nutricionista'),
    )
    
    cargo = models.CharField(max_length=20, choices=FUNCOES)
    
    def is_secretario(self):
        return self.cargo == 'SECRETARIO'
    
    def is_diretor(self):
        return self.cargo == 'DIRETOR'
    
    def is_nutricionista(self):
        return self.cargo == 'NUTRICIONISTA'
    
    