# app.py
import streamlit as st
import os
import threading
from main import batch_process_mode, FileManager # Certifique-se de que essas funções estão prontas para serem chamadas
from config.settings import Settings # Para carregar/configurar o ID da planilha

# --- Configuração da Página ---
st.set_page_config(page_title="Extrator de Editais", page_icon="📄")

# --- Função para processar (executada em thread) ---
def processar_pdf_thread():
    try:
        batch_process_mode() # Chama a função do seu main.py
        st.session_state.processamento_status = "Concluído com sucesso!"
        st.session_state.processamento_ok = True
    except Exception as e:
        st.session_state.processamento_status = f"Erro: {str(e)}"
        st.session_state.processamento_ok = False

# --- Interface Streamlit ---
st.title("📄 Extrator de Editais para Google Sheets")

# --- Configuração (opcional, pode ser um campo no início) ---
st.sidebar.header("Configurações")
novo_spreadsheet_id = st.sidebar.text_input("ID da Planilha do Google Sheets", value=Settings.SPREADSHEET_ID)
if st.sidebar.button("Salvar ID da Planilha"):
    # Atualiza o .env (semelhante ao que fizemos na GUI Tkinter)
    env_path = ".env"
    if not os.path.exists(env_path):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", env_path)
        else:
            st.sidebar.error("Arquivo .env não encontrado e .env.example também não.")
            st.stop()

    with open(env_path, "r", encoding="utf-8") as f:
        env_content = f.read()

    import re
    if re.search(r'^SPREADSHEET_ID=.*$', env_content, re.MULTILINE):
        env_content = re.sub(r'^SPREADSHEET_ID=.*$', f'SPREADSHEET_ID={novo_spreadsheet_id}', env_content, flags=re.MULTILINE)
    else:
        env_content += f"\nSPREADSHEET_ID={novo_spreadsheet_id}\n"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)

    st.sidebar.success("ID da planilha salvo no .env!")

# --- Seleção de PDFs ---
uploaded_files = st.file_uploader("Selecione os arquivos PDF do edital", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} arquivo(s) PDF selecionado(s).")

    # Botão para processar
    if st.button("Processar PDFs"):
        if not novo_spreadsheet_id.strip():
            st.error("Por favor, configure o ID da planilha antes de processar.")
        else:
            # Copia os arquivos para a pasta de processamento
            file_manager = FileManager()
            for uploaded_file in uploaded_files:
                file_path = os.path.join(file_manager.settings.PDF_TO_PROCESS, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.info(f"PDF '{uploaded_file.name}' copiado para processamento.")

            # Inicia o processamento em uma thread
            st.session_state.processamento_status = "Iniciando processamento..."
            st.session_state.processamento_ok = None
            thread = threading.Thread(target=processar_pdf_thread)
            thread.start()

    # Exibe status do processamento
    if 'processamento_status' in st.session_state:
        if st.session_state.processamento_ok is True:
            st.success(st.session_state.processamento_status)
        elif st.session_state.processamento_ok is False:
            st.error(st.session_state.processamento_status)
        else:
            st.info(st.session_state.processamento_status)

else:
    st.info("Por favor, selecione um ou mais arquivos PDF para processar.")

# --- Rodapé ---
st.markdown("---")
st.markdown("*Sistema de Extração de Editais - Desenvolvido por Rafael Cardoso Dourado com Python e Streamlit*")