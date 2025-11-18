import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Google Sheets Configuration
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "SUA_PLANILHA_ID_AQUI")
    
    # Folder Configuration
    PDF_TO_PROCESS = os.getenv("PDF_TO_PROCESS", "data/to_process")
    PDF_PROCESSED = os.getenv("PDF_PROCESSED", "data/processed")
    
    # OCR Configuration
    USE_OCR = os.getenv("USE_OCR", "False").lower() == "true"
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    # Processing Configuration
    MAX_PAGES = int(os.getenv("MAX_PAGES", "3"))  # Número máximo de páginas a analisar
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
    
    # Field Mapping to Cells (BASEADO NA SUA IMAGEM)
    CELL_MAPPING = {
        "Orgão": "B2",
        "Edital de Licitação": "B3",
        "CNPJ Órgão": "B4",
        "Cidade e Estado": "B5",
        "Nº Pregão e Processo": "B6",
        "Telefones": "B7",
        "E-mail": "B8",
        "Prazo de pagamento": "B9",
        "Plataforma": "B10",
        "UASG": "B11",
        "Modalidade de compra": "F3",
        "Prazo de entrega": "F4",
        "Local de entrega": "F5",
        "Validade da proposta": "F6",
        "Catálogo técnico": "F7",
        "Modo de Disputa": "F11"
    }