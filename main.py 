import time
import sys
from core.pdf_processor import PDFProcessor
from core.sheets_uploader import SheetsUploader
from utils.file_manager import FileManager
from config.settings import Settings

def process_single_pdf(pdf_path, uploader, clear_sheet=True):
    """Processa um único arquivo PDF"""
    print(f"\n{'='*60}")
    print(f"📄 PROCESSANDO: {os.path.basename(pdf_path)}")
    print(f"{'='*60}")
    
    try:
        # Limpa planilha para novo edital
        if clear_sheet:
            uploader.clear_sheet()
        
        # Processa PDF
        processor = PDFProcessor(pdf_path)
        extracted_data = processor.extract_all_fields()
        
        # Exibe dados extraídos
        print("\n🔍 DADOS EXTRAÍDOS:")
        print("-" * 40)
        for field, value in extracted_data.items():
            print(f"{field}: {value}")
        print("-" * 40)
        
        # Atualiza planilha
        print("\n☁️  ENVIANDO PARA GOOGLE SHEETS...")
        success = uploader.update_sheet(extracted_data)
        
        if success:
            # Move arquivo para pasta de processados
            edital_number = processor.get_edital_number()
            FileManager().move_to_processed(pdf_path, edital_number)
            print("\n✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
            return True
        else:
            print("\n❌ FALHA NO ENVIO PARA A PLANILHA")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        return False

def watch_folder_mode():
    """Modo de monitoramento contínuo de pasta"""
    file_manager = FileManager()
    uploader = SheetsUploader()
    last_processed = {}
    
    print("\n👁️  MODO DE MONITORAMENTO ATIVADO")
    print(f"📋 Monitorando pasta: {Settings().PDF_TO_PROCESS}")
    print("🔄 Verificando novos arquivos a cada 10 segundos...")
    print("🛑 Pressione CTRL+C para parar\n")
    
    try:
        while True:
            pending_pdfs = file_manager.get_pending_pdfs()
            
            for pdf_path in pending_pdfs:
                file_id = os.path.getmtime(pdf_path)
                if pdf_path not in last_processed or last_processed[pdf_path] != file_id:
                    process_single_pdf(pdf_path, uploader, clear_sheet=True)
                    last_processed[pdf_path] = file_id
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoramento interrompido pelo usuário")

def batch_process_mode():
    """Modo de processamento em lote"""
    file_manager = FileManager()
    uploader = SheetsUploader()
    
    pending_pdfs = file_manager.get_pending_pdfs()
    
    if not pending_pdfs:
        print("\nℹ️  Nenhum PDF encontrado na pasta para_processar/")
        print("📁 Coloque seus arquivos PDF na pasta e execute novamente")
        return
    
    print(f"\n📮 ENCONTRADOS {len(pending_pdfs)} ARQUIVOS PARA PROCESSAR")
    
    for i, pdf_path in enumerate(pending_pdfs, 1):
        print(f"\n{'='*60}")
        print(f"📤 PROCESSAMENTO EM LOTE ({i}/{len(pending_pdfs)})")
        print(f"{'='*60}")
        
        # Limpa planilha apenas para o primeiro arquivo
        clear_sheet = (i == 1)
        success = process_single_pdf(pdf_path, uploader, clear_sheet)
        
        if not success:
            print(f"\n⚠️  Continuando com o próximo arquivo...")
    
    print(f"\n{'='*60}")
    print(f"✅ PROCESSAMENTO EM LOTE CONCLUÍDO!")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Organiza arquivos nas pastas corretas
    FileManager().organize_files()
    
    print("\n" + "="*65)
    print("🚀 SISTEMA DE EXTRAÇÃO DE EDITAIS - GOOGLE SHEETS")
    print("="*65)
    
    # Verifica credenciais
    if not os.path.exists('credentials.json'):
        print("\n❌ ARQUIVO credentials.json NÃO ENCONTRADO!")
        print("🔧 Siga estas etapas:")
        print("1. Acesse https://console.cloud.google.com/")
        print("2. Crie um projeto e habilite a API do Google Sheets")
        print("3. Crie credenciais OAuth 2.0 (tipo: Aplicativo para Desktop)")
        print("4. Baixe o arquivo credentials.json e coloque na pasta do projeto")
        sys.exit(1)
    
    # Menu principal
    print("\n📋 ESCOLHA O MODO DE OPERAÇÃO:")
    print("1. Processar todos os PDFs da pasta (modo em lote)")
    print("2. Monitorar pasta continuamente (modo watch)")
    print("3. Sair")
    
    choice = input("\n➤ Sua escolha (1-3): ").strip()
    
    if choice == "1":
        batch_process_mode()
    elif choice == "2":
        watch_folder_mode()
    elif choice == "3":
        print("\n👋 Sistema encerrado. Até a próxima!")
    else:
        print("\n❌ Opção inválida. Tente novamente.")