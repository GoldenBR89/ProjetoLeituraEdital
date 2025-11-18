import streamlit as st
import os
import json
import threading
import time
import bcrypt
from pathlib import Path
from database.init_db import DatabaseManager
from config.user_settings import UserSettings
from core.pdf_processor import PDFProcessor
from core.sheets_uploader import SheetsUploader
from utils.file_manager import FileManager
from datetime import datetime

# Configuração inicial
st.set_page_config(
    page_title="Extrator de Editais - Multi-Usuário",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o banco de dados
db_manager = DatabaseManager()

# Funções auxiliares
def hash_password(password):
    """Cria um hash seguro da senha"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password, hashed_password):
    """Verifica se a senha corresponde ao hash armazenado"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def init_session_state():
    """Inicializa variáveis de estado da sessão"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None
    if 'new_user' not in st.session_state:
        st.session_state.new_user = False
    if 'needs_credentials' not in st.session_state:
        st.session_state.needs_credentials = False
    if 'needs_spreadsheet_config' not in st.session_state:
        st.session_state.needs_spreadsheet_config = False
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = None
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = []
    if 'spreadsheet_id' not in st.session_state:
        st.session_state.spreadsheet_id = ""
    if 'spreadsheet_name' not in st.session_state:
        st.session_state.spreadsheet_name = ""
    if 'google_credentials' not in st.session_state:
        st.session_state.google_credentials = None

def login_user(username, password):
    """Realiza o login do usuário"""
    user = db_manager.get_user_by_username(username)
    if user and verify_password(password, user[3]):
        st.session_state.user_id = user[0]
        st.session_state.username = username
        st.session_state.user_name = user[1]
        st.session_state.user_email = user[2]
        st.session_state.authentication_status = True
        
        # Verifica se o usuário tem configurações de planilha
        sheet_config = db_manager.get_spreadsheet_config(user[0])
        if not sheet_config:
            st.session_state.needs_spreadsheet_config = True
        else:
            st.session_state.needs_spreadsheet_config = False
        
        # Verifica se o usuário tem credenciais do Google
        google_creds = db_manager.get_google_credentials(user[0])
        if not google_creds:
            st.session_state.needs_credentials = True
        else:
            st.session_state.needs_credentials = False
        
        return True
    return False

def create_user(username, name, email, password):
    """Cria um novo usuário"""
    hashed_password = hash_password(password)
    user_id = db_manager.create_user(username, name, email, hashed_password)
    if user_id:
        # Configura o estado da sessão
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.user_name = name
        st.session_state.user_email = email
        st.session_state.authentication_status = True
        st.session_state.needs_spreadsheet_config = True
        st.session_state.needs_credentials = True
        return True
    return False

def process_pdf_thread(pdf_path, user_id, username, log_placeholder):
    """Processa um PDF em uma thread separada"""
    try:
        processor = PDFProcessor(pdf_path)
        extracted_data = processor.extract_all_fields()
        
        uploader = SheetsUploader(user_id, username)
        success = uploader.update_sheet(extracted_data)
        
        file_manager = FileManager()
        if success:
            edital_number = processor.get_edital_number()
            file_manager.move_to_processed(pdf_path, edital_number)
            return True, f"✅ Processado: {os.path.basename(pdf_path)}"
        else:
            return False, f"❌ Erro ao enviar para planilha: {os.path.basename(pdf_path)}"
    except Exception as e:
        return False, f"❌ Erro ao processar {os.path.basename(pdf_path)}: {str(e)}"

def process_pdfs(uploaded_files):
    """Função principal para processar múltiplos PDFs"""
    if not st.session_state.user_id:
        st.error("Nenhum usuário logado. Faça login primeiro.")
        return
    
    if not uploaded_files:
        st.warning("Nenhum arquivo PDF selecionado.")
        return
    
    file_manager = FileManager()
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Atualiza progresso
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Processando {i+1}/{len(uploaded_files)}: {uploaded_file.name}...")
        
        # Salva o arquivo temporariamente
        temp_path = os.path.join(file_manager.settings.PDF_TO_PROCESS, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Processa o PDF
        success, message = process_pdf_thread(
            temp_path, 
            st.session_state.user_id, 
            st.session_state.username,
            status_text
        )
        results.append(message)
    
    # Atualiza o estado da sessão com os resultados
    st.session_state.processing_status = "completed"
    st.session_state.processing_results = results
    progress_bar.empty()
    status_text.empty()

# Página principal
def main_app():
    init_session_state()
    
    # Cabeçalho
    st.title("📄 Extrator de Editais - Multi-Usuário")
    st.markdown(f"Bem-vindo, **{st.session_state.user_name}**! Versão: 2.0")
    
    # Barra lateral
    with st.sidebar:
        st.header("⚙️ Menu")
        
        if st.session_state.authentication_status:
            st.subheader(f"Olá, {st.session_state.user_name}!")
            
            # Configurações do usuário
            if st.button("📝 Configurar Planilha"):
                st.session_state.needs_spreadsheet_config = True
            
            if st.button("🔑 Configurar Credenciais Google"):
                st.session_state.needs_credentials = True
            
            if st.button("🚪 Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()
        
        else:
            st.subheader("Autenticação")
            auth_choice = st.radio("Escolha uma opção:", ["Login", "Criar Conta"])
            
            if auth_choice == "Login":
                with st.form("login_form"):
                    username = st.text_input("Nome de usuário")
                    password = st.text_input("Senha", type="password")
                    submitted = st.form_submit_button("Entrar")
                    
                    if submitted:
                        if login_user(username, password):
                            st.success(f"Bem-vindo de volta, {st.session_state.user_name}!")
                            st.experimental_rerun()
                        else:
                            st.error("Credenciais inválidas. Tente novamente.")
            
            else:  # Criar Conta
                with st.form("signup_form"):
                    new_username = st.text_input("Novo nome de usuário (único)")
                    new_name = st.text_input("Seu nome completo")
                    new_email = st.text_input("Seu e-mail")
                    new_password = st.text_input("Senha", type="password")
                    confirm_password = st.text_input("Confirmar senha", type="password")
                    submitted = st.form_submit_button("Criar Conta")
                    
                    if submitted:
                        if new_password != confirm_password:
                            st.error("As senhas não coincidem.")
                        elif len(new_password) < 6:
                            st.error("A senha deve ter pelo menos 6 caracteres.")
                        else:
                            if create_user(new_username, new_name, new_email, new_password):
                                st.success(f"Conta criada com sucesso! Bem-vindo, {new_name}!")
                                st.experimental_rerun()
                            else:
                                st.error("Nome de usuário já existe. Escolha outro.")
    
    # Verifica se precisa de configuração inicial
    if st.session_state.needs_spreadsheet_config:
        st.subheader("📊 Configurar Planilha do Google Sheets")
        st.info("Configure sua planilha do Google Sheets para enviar os dados extraídos.")
        
        col1, col2 = st.columns(2)
        with col1:
            spreadsheet_id = st.text_input(
                "ID da Planilha (obrigatório)",
                help="Encontre na URL: https://docs.google.com/spreadsheets/d/[ID_DA_PLANILHA]/edit"
            )
        with col2:
            spreadsheet_name = st.text_input("Nome da Planilha (opcional)")
        
        if st.button("💾 Salvar Configuração da Planilha"):
            if not spreadsheet_id.strip():
                st.error("O ID da planilha é obrigatório.")
            else:
                user_settings = UserSettings(st.session_state.user_id, st.session_state.username)
                user_settings.save_spreadsheet_config(spreadsheet_id.strip(), spreadsheet_name.strip() or None)
                st.session_state.needs_spreadsheet_config = False
                st.success("Configuração da planilha salva com sucesso!")
                st.experimental_rerun()
        
        st.markdown("---")
    
    if st.session_state.needs_credentials:
        st.subheader("🔑 Configurar Credenciais do Google")
        st.info("Faça upload do seu arquivo credentials.json do Google Cloud Console")
        
        uploaded_credentials = st.file_uploader("Carregar credentials.json", type="json")
        
        if uploaded_credentials:
            credentials_content = uploaded_credentials.read().decode()
            try:
                json.loads(credentials_content)  # Valida se é JSON válido
                st.success("Arquivo JSON válido carregado!")
                
                if st.button("💾 Salvar Credenciais do Google"):
                    user_settings = UserSettings(st.session_state.user_id, st.session_state.username)
                    user_settings.save_google_credentials(credentials_content)
                    st.session_state.needs_credentials = False
                    st.success("Credenciais do Google salvas com sucesso!")
                    st.experimental_rerun()
            except json.JSONDecodeError:
                st.error("Arquivo não é um JSON válido. Verifique o arquivo carregado.")
        
        st.markdown("---")
    
    # Área principal - processamento de PDFs
    if st.session_state.authentication_status and not (st.session_state.needs_spreadsheet_config or st.session_state.needs_credentials):
        st.subheader("📤 Processar Editais (PDFs)")
        st.info(f"Planilha configurada: {st.session_state.spreadsheet_name or 'Minha Planilha'}")
        
        uploaded_files = st.file_uploader(
            "Selecione os arquivos PDF do edital",
            type="pdf",
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} arquivo(s) PDF selecionado(s).")
            
            if st.button("⚡ Processar Todos os PDFs", key="process_btn"):
                # Inicia o processamento em uma thread separada
                processing_thread = threading.Thread(
                    target=process_pdfs,
                    args=(uploaded_files,),
                    daemon=True
                )
                processing_thread.start()
                st.session_state.processing_status = "processing"
                st.info("🔄 Processamento iniciado em segundo plano...")
        
        # Mostra resultados do processamento
        if st.session_state.processing_status == "completed":
            st.success("🎉 Processamento concluído!")
            
            if st.session_state.processing_results:
                st.subheader("📋 Resultados:")
                for result in st.session_state.processing_results:
                    if "✅" in result:
                        st.success(result)
                    elif "❌" in result:
                        st.error(result)
                    else:
                        st.info(result)
                
                # Botão para limpar resultados
                if st.button("🔄 Limpar Resultados"):
                    st.session_state.processing_status = None
                    st.session_state.processing_results = []
                    st.experimental_rerun()
        
        elif st.session_state.processing_status == "processing":
            st.info("🔄 Processamento em andamento...")
            st.spinner("Aguarde enquanto processamos seus PDFs...")
    
    else:
        if not st.session_state.authentication_status:
            st.info("🔐 Faça login ou crie uma conta para começar a usar o sistema.")
        else:
            st.warning("⚠️ Configure sua planilha do Google Sheets e credenciais primeiro!")
    
    # Rodapé
    st.markdown("---")
    st.markdown("*Sistema de Extração de Editais - Versão Multi-Usuário*")
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Inicializa o aplicativo
if __name__ == "__main__":
    main_app()