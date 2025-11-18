import os
import re
import pdfplumber
from PyPDF2 import PdfReader
from config.settings import Settings
from config.patterns import ExtractionPatterns
from utils.ocr_handler import OCRHandler
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.settings = Settings()
        self.text = ""
        self.extracted_data = {}
    
    def extract_text(self):
        """Extrae texto do PDF usando múltiplos métodos (PDF, OCR)"""
        try:
            # Primeiro, tente extrair texto normal (PDF)
            with pdfplumber.open(self.pdf_path) as pdf:
                pages = min(len(pdf.pages), self.settings.MAX_PAGES)
                for i in range(pages):
                    page = pdf.pages[i]
                    self.text += page.extract_text() + "\n"
            
            # Verifica se o texto é suficiente
            if len(self.text.strip()) < 100:
                # Se não tiver texto suficiente, use OCR
                self.text = OCRHandler.process_pdf(self.pdf_path, self.settings.MAX_PAGES)
            
            # Se ainda não tiver texto, tente com PyPDF2
            if len(self.text.strip()) < 100:
                reader = PdfReader(self.pdf_path)
                pages = min(len(reader.pages), self.settings.MAX_PAGES)
                for i in range(pages):
                    page = reader.pages[i]
                    self.text += page.extract_text() + "\n"
            
            return self.text
        
        except Exception as e:
            logger.error(f"Erro na extração de texto: {str(e)}")
            return ""
    
    def _normalize_text(self, text):
        """Normaliza o texto para facilitar a extração"""
        # Remove quebras quebradas
        text = text.replace("\n", " ")
        # Remove múltiplos espaços
        text = re.sub(r"\s+", " ", text)
        # Separa letras coladas em números
        text = re.sub(r"([A-Za-z])(\d)", r"\1 \2", text)
        # Separa números coladas em letras
        text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)
        # Normaliza hífens
        text = re.sub(r"[–—]", "-", text)
        # Remove caracteres especiais
        text = re.sub(r"[\x00-\x1f]", "", text)
        return text.strip()
    
    def extract_all_fields(self):
        """Extrai todos os campos do edital com fallback inteligente"""
        self.extracted_data = {}
        self.text = self._normalize_text(self.text)
        
        # Primeiro, tente extrair com padrões regex
        for field in self.settings.CELL_MAPPING.keys():
            if field in ["Edital de Licitação"]:
                continue
            
            # Tenta extrair com padrões regex
            self.extracted_data[field] = ExtractionPatterns.extract_field(field, self.text)
            
            # Se ainda não for encontrado, tente outros métodos
            if self.extracted_data[field] == "NÃO ENCONTRADO":
                # Tenta extrair com base em palavras-chave
                self.extracted_data[field] = self._extract_by_keywords(field, self.text)
                
                # Se ainda não for encontrado, tente com OCR (se não tiver sido usado)
                if self.extracted_data[field] == "NÃO ENCONTRADO" and self.settings.USE_OCR:
                    self.extracted_data[field] = self._extract_with_ocr(field)
        
        return self.extracted_data
    
    def _extract_by_keywords(self, field_name, text):
        """Tenta extrair com base em palavras-chave"""
        keywords = {
            "Orgão": ["órgão", "entidade", "prefeitura", "secretaria", "governo"],
            "CNPJ Órgão": ["cnpj", "inscrição", "código"],
            "Cidade e Estado": ["município", "cidade", "estado", "uf", "localização"],
            "Nº Pregão e Processo": ["pregão", "processo", "número", "nº"],
            "Telefones": ["telefone", "fones", "contato", "lado", "fale conosco"],
            "E-mail": ["e-mail", "email", "contato", "fale conosco"],
            "Prazo de pagamento": ["prazo", "pagamento", "vencimento", "pago"],
            "Plataforma": ["plataforma", "sistema", "ferramenta", "sistema de licitação"],
            "UASG": ["uasg", "código uasg", "código uasg"],
            "Modalidade de compra": ["modalidade", "tipo", "licitação", "compra"],
            "Prazo de entrega": ["prazo", "entrega", "entregas", "recepção"],
            "Local de entrega": ["local", "entrega", "recepção", "fornecimento"],
            "Validade da proposta": ["validade", "proposta", "válido", "prazo"],
            "Catálogo técnico": ["catálogo", "técnic", "especificação", "ficha"],
            "Modo de Disputa": ["modo", "disputa", "aberto", "fechado"]
        }
        
        # Para cada palavra-chave, tente encontrar o texto
        for keyword in keywords.get(field_name, []):
            pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            matches = pattern.findall(text)
            
            if matches:
                # Encontrou a palavra-chave, tente extrair o valor
                start_idx = text.find(matches[0])
                end_idx = start_idx + len(matches[0])
                
                # Busca para a direita
                for i in range(start_idx, min(start_idx + 200, len(text))):
                    if text[i] in ['\n', ' ', '.', ';', ':', ')', '}', ']', '-', '–', '—', '–']:
                        end_idx = i
                        break
                
                # Busca para a esquerda
                for i in range(start_idx - 1, max(0, start_idx - 100), -1):
                    if text[i] in ['\n', ' ', '.', ';', ':', '(', '{', '[', '-', '–', '—', '–']:
                        start_idx = i
                        break
                
                value = text[start_idx:end_idx].strip()
                if len(value) > 2:
                    return value
        
        return "NÃO ENCONTRADO"
    
    def _extract_with_ocr(self, field_name):
        """Tenta extrair usando OCR (Tesseract) para PDFs escaneados"""
        if not self.settings.USE_OCR:
            return "NÃO ENCONTRADO"
        
        # Use a lógica de OCR para extrair
        ocr_text = OCRHandler.process_pdf(self.pdf_path, self.settings.MAX_PAGES)
        
        # Tente extrair com o texto do OCR
        extracted = ExtractionPatterns.extract_field(field_name, ocr_text)
        
        # Se ainda não for encontrado, tente com palavras-chave
        if extracted == "NÃO ENCONTRADO":
            keywords = {
                "Orgão": ["órgão", "entidade", "prefeitura", "secretaria", "governo"],
                "CNPJ Órgão": ["cnpj", "inscrição", "código"],
                "Cidade e Estado": ["município", "cidade", "estado", "uf", "localização"],
                "Nº Pregão e Processo": ["pregão", "processo", "número", "nº"],
                "Telefones": ["telefone", "fones", "contato", "lado", "fale conosco"],
                "E-mail": ["e-mail", "email", "contato", "fale conosco"],
                "Prazo de pagamento": ["prazo", "pagamento", "vencimento", "pago"],
                "Plataforma": ["plataforma", "sistema", "ferramenta", "sistema de licitação"],
                "UASG": ["uasg", "código uasg", "código uasg"],
                "Modalidade de compra": ["modalidade", "tipo", "licitação", "compra"],
                "Prazo de entrega": ["prazo", "entrega", "entregas", "recepção"],
                "Local de entrega": ["local", "entrega", "recepção", "fornecimento"],
                "Validade da proposta": ["validade", "proposta", "válido", "prazo"],
                "Catálogo técnico": ["catálogo", "técnic", "especificação", "ficha"],
                "Modo de Disputa": ["modo", "disputa", "aberto", "fechado"]
            }
            
            for keyword in keywords.get(field_name, []):
                pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
                matches = pattern.findall(ocr_text)
                
                if matches:
                    start_idx = ocr_text.find(matches[0])
                    end_idx = start_idx + len(matches[0])
                    
                    # Busca para a direita
                    for i in range(start_idx, min(start_idx + 200, len(ocr_text))):
                        if ocr_text[i] in ['\n', ' ', '.', ';', ':', ')', '}', ']', '-', '–', '—', '–']:
                            end_idx = i
                            break
                    
                    # Busca para a esquerda
                    for i in range(start_idx - 1, max(0, start_idx - 100), -1):
                        if ocr_text[i] in ['\n', ' ', '.', ';', ':', '(', '{', '[', '-', '–', '—', '–']:
                            start_idx = i
                            break
                    
                    value = ocr_text[start_idx:end_idx].strip()
                    if len(value) > 2:
                        return value
            
            return "NÃO ENCONTRADO"
        
        return extracted
    
    def get_edital_number(self):
        """Obtém o número do edital do nome do arquivo ou do texto"""
        # Primeiro, tente extrair do nome do arquivo
        filename = os.path.basename(self.pdf_path)
        match = re.search(r'(\d+[-_]\d+)', filename)
        if match:
            return match.group(1).replace('_', '/').replace('-', '/')
        
        # Se não tiver no nome, tente extrair do texto
        return "edital_sem_numero"