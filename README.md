**SEMAE - Sistema de Controle de Estoque para as Escolas Municipais**  
Desenvolvido em **Python** com o framework **Django**

---

## 📚 Sobre o Projeto

O **Projeto SEMAE** (Sistema de Estoque Municipal para Ambientes Escolares) tem como objetivo fornecer uma solução simples, eficiente e web-based para o controle de estoque de materiais em escolas municipais.

A ferramenta permite que as unidades escolares possam registrar entradas e saídas de produtos, manter o estoque atualizado, acompanhar o consumo de materiais e gerar relatórios de forma rápida e intuitiva.

---

## ⚙️ Funcionalidades

- ✅ Cadastro de produtos com categorias e unidades de medida  
- ✅ Controle de entrada e saída de estoque  
- ✅ Relatórios de movimentação e inventário  
- ✅ Autenticação e níveis de acesso (usuários administrativos e comuns)  
- ✅ Interface web amigável (Django Admin e/ou templates personalizados)  
- ✅ Almoxarifado central (Secretária ou demais)

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Django 4.x**
- **SQLite/MySQL** (em desenvolvimento)
- **Bootstrap 5**
- **HTML, CSS**

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos

- Python 3.10 ou superior
- Pip (gerenciador de pacotes)
- Git (opcional, para clonar o repositório)

### Passo a passo

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
python manage.py runserver
