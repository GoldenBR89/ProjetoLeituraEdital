import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "SUA_PLANILHA_ID_AQUI")
    PDF_TO_PROCESS = os.getenv("PDF_TO_PROCESS", "data/to_process")
    PDF_PROCESSED = os.getenv("PDF_PROCESSED", "data/processed")
    USE_OCR = os.getenv("USE_OCR", "False").lower() == "true"
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    MAX_PAGES = int(os.getenv("MAX_PAGES", "3"))
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
    CELL_MAPPING = {
    "Orgão": "E2",
    "Edital de Licitação": "E3",
    "CNPJ Órgão": "E4",
    "Cidade e Estado": "E5",
    "Nº Pregão e Processo": "E6",
    "Telefones": "E7",
    "E-mail": "E8",
    "Prazo de pagamento": "E9",
    "Plataforma": "E10",
    "UASG": "E11",
    "Modalidade de compra": "G3",
    "Prazo de entrega": "G4",
    "Local de entrega": "G5",
    "Validade da proposta": "G6",
    "Catálogo técnico": "G7",
    "Modo de Disputa": "G11"
}