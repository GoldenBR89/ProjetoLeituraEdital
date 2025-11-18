# 🚀 Sistema de Extração de Editais para Google Sheets

Sistema completo para extrair informações de editais de licitações em PDF e preencher automaticamente uma planilha do Google Sheets.

## 📋 Campos Extraídos
- **Orgão** - Nome do órgão licitante
- **CNPJ Órgão** - CNPJ do órgão
- **Cidade e Estado** - Localização do órgão
- **Nº Pregão e Processo** - Números de identificação
- **Telefones** - Contatos do órgão
- **E-mail** - E-mail para contato
- **Prazo de pagamento** - Condições de pagamento
- **Plataforma** - Sistema onde ocorre a licitação
- **UASG** - Unidade de gestão
- **Modalidade de compra** - Tipo de licitação
- **Prazo de entrega** - Prazo para entrega dos produtos/serviços
- **Local de entrega** - Endereço de entrega
- **Validade da proposta** - Prazo de validade das propostas
- **Catálogo técnico** - Referência a catálogos técnicos
- **Modo de Disputa** - Tipo de disputa do pregão

## ⚙️ Configuração Inicial

### 1. Dependências do Sistema
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Tesseract OCR** (opcional, para PDFs escaneados):
  - Windows: [Baixar instalador](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt install tesseract-ocr libtesseract-dev poppler-utils`
  - Mac: `brew install tesseract poppler`

### 2. Configuração do Google Cloud
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Habilite a API do Google Sheets
4. Em "Credenciais", crie uma ID de cliente OAuth 2.0:
   - Tipo de aplicativo: Aplicativo para desktop
   - Nome: Sistema de Editais
5. Baixe o arquivo `credentials.json` e coloque na pasta do projeto

### 3. Instalação do Projeto
```bash
# Clone o repositório ou crie a estrutura de pastas
git clone https://github.com/seuusuario/licitacoes-extractor.git
cd licitacoes-extractor

# Crie ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações