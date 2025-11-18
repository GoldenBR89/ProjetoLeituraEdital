import os
import re
import pdfplumber
from PyPDF2 import PdfReader
from config.settings import Settings
from config.patterns import ExtractionPatterns
from utils.ocr_handler import OCRHandler

class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.settings = Settings()
        self.text = ""
        self.extracted_data = {}
    
    def extract_text(self):
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                pages = min(len(pdf.pages), self.settings.MAX_PAGES)
                for i in range(pages):
                    page = pdf.pages[i]
                    self.text += page.extract_text() + "\n"
            
            if len(self.text.strip()) < 100 and self.settings.USE_OCR:
                self.text = OCRHandler.process_pdf(self.pdf_path, self.settings.MAX_PAGES)
            
            if len(self.text.strip()) < 100:
                reader = PdfReader(self.pdf_path)
                pages = min(len(reader.pages), self.settings.MAX_PAGES)
                for i in range(pages):
                    page = reader.pages[i]
                    self.text += page.extract_text() + "\n"
            
            return self.text
        
        except Exception as e:
            print(f"❌ Erro na extração de texto: {str(e)}")
            return ""
    
    def extract_all_fields(self):
        if not self.text:
            self.extract_text()
        
        normalized_text = self._normalize_text(self.text)
        
        for field in self.settings.CELL_MAPPING.keys():
            if field in ["Edital de Licitação"]:
                continue
            
            self.extracted_data[field] = ExtractionPatterns.extract_field(field, normalized_text)
        
        return self.extracted_data
    
    def _normalize_text(self, text):
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
        text = re.sub(r'\n(?![A-Z])', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\x00', '')
        return text.strip()
    
    def get_edital_number(self):
        filename = os.path.basename(self.pdf_path)
        match = re.search(r'(\d+[-_]\d+)', filename)
        if match:
            return match.group(1).replace('_', '/').replace('-', '/')
        
        if "Nº Pregão e Processo" in self.extracted_data:
            match = re.search(r'PREGÃO(?:\s+ELETRÔNICO)?\s*(?:Nº|N\.º|No)\s*([\d\./\-]+)', 
                             self.extracted_data["Nº Pregão e Processo"])
            if match:
                return match.group(1).replace('/', '_')
        
        return "edital_sem_numero"