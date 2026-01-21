# SEMAE - Sistema de Estoque e Materiais da Educação Escolar

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-5.0%2B-092e20)](https://www.djangoproject.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

O **SEMAE** é uma plataforma simples e robusta desenvolvida para otimizar a logística e o controle dos produtos escolares em redes municipais. O sistema integra desde o pedido realizado na ponta (Diretores) até a análise técnica (Nutricionistas) e a compra/entrega (Secretaria), garantindo transparência e eficiência no uso dos recursos públicos.

## Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Estrutura](#estrutura-do-projeto)
- [Roadmap](#roadmap)
- [Tecnologias](#tecnologias-utilizadas)
- [Instalação](#instalação)

---

## Visão Geral

O SEMAE resolve o desafio de gerenciar o fluxo de suprimentos alimentares para múltiplas unidades escolares. Ele substitui planilhas manuais por um fluxo de trabalho automatizado e auditável.

### Problema de Negócio
Secretarias de Educação enfrentam dificuldades em:
- Controlar o estoque centralizado e o consumo real por escola.
- Validar pedidos de itens perecíveis (carnes/proteínas) que exigem compra imediata.
- Gerar relatórios de prestação de contas precisos para órgãos fiscalizadores e análise própria.

### Solução
- **Gestão de Perfis Dinâmicos**: Acesso restrito para Secretários, Nutricionistas e Diretores.
- **Ciclo de Pedidos Inteligente**: Separação automática entre produtos registraveis (estoque) e pedidos de proteína (compra direta).
- **Vínculo Institucional**: Cada Diretor é vinculado à sua respectiva Unidade Escolar via Perfil de Escola.

---

## Funcionalidades

### Gestão de Usuários
- **Níveis de Acesso (RBAC)**: Controle total via Grupos do Django.
- **Edição Administrativa**: Interface para redefinir senhas e atualizar vínculos de escolas.

### Fluxo de Pedidos
- **Solicitação**: Diretores realizam pedidos baseados no estoque disponível no almoxarifado.
- **Análise Nutricional**: Nutricionistas podem aprovar, editar quantidades ou negar itens por motivos técnicos.
- **Logística de Proteínas**: Identificação automática de pedidos de carne para encaminhamento ao setor de compras.

### Relatórios e BI
- **Dashboard de Consumo**: Gráficos interativos mostrando a distribuição de recursos por escola.
- **Relatórios Oficiais**: Listagem detalhada de solicitações de proteínas com observações específicas para fornecedores.

---

## Arquitetura

O sistema utiliza o padrão **MVT (Model-View-Template)** do Django:

```text
┌─────────────────────────────────────────────────────┐
│                  CAMADA DE FRONTEND                 │
│   (Django Templates - HTML5/CSS3/JavaScript)        │
└─────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────┐
│             CAMADA DE NEGÓCIO (Django Views)        │
│  • Lógica de Aprovação e Gestão de Estoque          │
│  • Processamento de Relatórios e Gráficos           │
└─────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────┐
│          CAMADA DE DADOS (Django Models/ORM)        │
│  • Usuario Customizado (AbstractUser)               │
│  • Estoque, Pedidos e Lotes                         │
│  • PerfilEscola (Relacionamento OneToOne)           │
└─────────────────────────────────────────────────────┘

```

---

## Estrutura do Projeto

semae_project/
├── usuarios/       # Custom User, Perfis de Escola e Autenticação
├── produtos/       # Gestão de itens, Lotes e Estoque Central
├── pedidos/        # Fluxo de solicitação e aprovação de merenda
├── core/           # Configurações do projeto e URLs principais
└── templates/      # Arquivos HTML do sistema

---

## Roadmap

- [x] Cadastro de Usuários com Perfis Dinâmicos
- [x] Vínculo Diretor -> Unidade Escolar
- [x] Controle de pedidos por Diretor
- [x] Cadastro por tipos de produtos e seus respectivos lotes ao estoque
- [x] Controle de pedidos das escolas pela Nutricionista
- [x] Controle por pedidos diretos de perecíveis (Proteínas e carne) pela secretaria
- [x] Dashboard de Consumo por Unidade
- [x] Geração de Relatórios em PDF com cabeçalho oficial

--

## Tecnologias Utilizadas

- **Python 3.12+**
- **Django 5.0**
- **SQLite/PostgreSQL**
- **Chart.js**
- **HTML, CSS**

---


# Instalação

```bash
# Clone o repositório
git clone [https://github.com/devkayky83/semae_project.git](https://github.com/devkayky83/semae_project.git)
cd semae_project

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

## Execute as migrações
python manage.py migrate

# Inicie o servidor
python manage.py runserver