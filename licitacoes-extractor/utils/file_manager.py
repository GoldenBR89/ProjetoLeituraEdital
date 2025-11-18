import os
import shutil
from config.settings import Settings

class FileManager:
    def __init__(self):
        self.settings = Settings()
        self._create_directories()
    
    def _create_directories(self):
        """Cria diretórios necessários se não existirem"""
        for directory in [self.settings.PDF_TO_PROCESS, self.settings.PDF_PROCESSED]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 Diretório criado: {directory}")
    
    def get_pending_pdfs(self):
        """Retorna lista de PDFs pendentes de processamento"""
        pdf_files = []
        for file in os.listdir(self.settings.PDF_TO_PROCESS):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(self.settings.PDF_TO_PROCESS, file))
        return pdf_files
    
    def move_to_processed(self, pdf_path, edital_number):
        """Move arquivo processado para pasta de processados"""
        try:
            filename = os.path.basename(pdf_path)
            new_filename = f"{edital_number}_{filename}" if edital_number else filename
            dest_path = os.path.join(self.settings.PDF_PROCESSED, new_filename)
            
            # Garante nome único
            counter = 1
            while os.path.exists(dest_path):
                name_parts = new_filename.rsplit('.', 1)
                new_filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                dest_path = os.path.join(self.settings.PDF_PROCESSED, new_filename)
                counter += 1
            
            shutil.move(pdf_path, dest_path)
            print(f"📦 Arquivo movido para: {dest_path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao mover arquivo: {str(e)}")
            return False
    
    def organize_files(self):
        """Organiza arquivos nas pastas corretas"""
        # Move todos os PDFs da raiz para pasta de processamento
        for file in os.listdir('.'):
            if file.lower().endswith('.pdf') and file != 'credentials.json':
                dest = os.path.join(self.settings.PDF_TO_PROCESS, file)
                if not os.path.exists(dest):
                    shutil.move(file, dest)
                    print(f"MOVED: {file} -> {dest}")