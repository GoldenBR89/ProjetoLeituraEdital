import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from config.settings import Settings

class OCRHandler:
    @staticmethod
    def setup_tesseract():
        """Configura o caminho do Tesseract OCR"""
        settings = Settings()
        
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
        # Para Linux/Mac o caminho geralmente já está configurado
    
    @staticmethod
    def process_pdf(pdf_path, max_pages=3):
        """Processa PDF com OCR e retorna o texto extraído"""
        try:
            OCRHandler.setup_tesseract()
            
            print("🔍 Processando PDF com OCR (pode demorar alguns segundos)...")
            
            # Converte PDF para imagens
            images = convert_from_path(
                pdf_path,
                dpi=300,
                first_page=1,
                last_page=max_pages,
                thread_count=2
            )
            
            full_text = ""
            for i, image in enumerate(images):
                print(f"  📄 Processando página {i+1}/{min(max_pages, len(images))} com OCR...")
                
                # Pré-processamento da imagem para melhorar OCR
                image = image.convert('L')  # Converte para escala de cinza
                image = image.point(lambda x: 0 if x < 140 else 255, '1')  # Binarização
                
                # Extrai texto com OCR
                text = pytesseract.image_to_string(
                    image,
                    lang='por',
                    config='--psm 6 --oem 1'
                )
                full_text += text + "\n"
            
            print("✅ OCR concluído com sucesso!")
            return full_text
            
        except Exception as e:
            print(f"❌ Erro no processamento OCR: {str(e)}")
            print("💡 Dica: Instale o Tesseract OCR e poppler para PDFs escaneados")
            return ""