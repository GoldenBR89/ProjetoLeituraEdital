import os
import json
from dotenv import load_dotenv
from database.init_db import DatabaseManager
from security.encryption import EncryptionManager

class UserSettings:
    def __init__(self, user_id=None, username=None):
        self.user_id = user_id
        self.username = username
        self.db_manager = DatabaseManager()
        self.enc_manager = EncryptionManager()
        self.settings = self._load_user_settings()
    
    def _load_user_settings(self):
        """Carrega as configurações específicas do usuário"""
        if not self.user_id:
            return self._load_default_settings()
        
        # Carrega configurações da planilha
        sheet_config = self.db_manager.get_spreadsheet_config(self.user_id)
        
        # Carrega credenciais do Google
        google_credentials = self.db_manager.get_google_credentials(self.user_id)
        
        return {
            'SPREADSHEET_ID': sheet_config['spreadsheet_id'] if sheet_config else os.getenv("SPREADSHEET_ID", "SUA_PLANILHA_ID_AQUI"),
            'SPREADSHEET_NAME': sheet_config['spreadsheet_name'] if sheet_config else "Minha Planilha",
            'GOOGLE_CREDENTIALS': google_credentials or None,
            'PDF_TO_PROCESS': os.getenv("PDF_TO_PROCESS", "data/to_process"),
            'PDF_PROCESSED': os.getenv("PDF_PROCESSED", "data/processed"),
            'USE_OCR': os.getenv("USE_OCR", "False").lower() == "true",
            'TESSERACT_PATH': os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            'MAX_PAGES': int(os.getenv("MAX_PAGES", "3")),
            'RETRY_ATTEMPTS': int(os.getenv("RETRY_ATTEMPTS", "3")),
            'CELL_MAPPING': {
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
        }
    
    def _load_default_settings(self):
        """Carrega configurações padrão quando não há usuário logado"""
        return {
            'SPREADSHEET_ID': os.getenv("SPREADSHEET_ID", "SUA_PLANILHA_ID_AQUI"),
            'SPREADSHEET_NAME': "Minha Planilha",
            'GOOGLE_CREDENTIALS': None,
            'PDF_TO_PROCESS': os.getenv("PDF_TO_PROCESS", "data/to_process"),
            'PDF_PROCESSED': os.getenv("PDF_PROCESSED", "data/processed"),
            'USE_OCR': os.getenv("USE_OCR", "False").lower() == "true",
            'TESSERACT_PATH': os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            'MAX_PAGES': int(os.getenv("MAX_PAGES", "3")),
            'RETRY_ATTEMPTS': int(os.getenv("RETRY_ATTEMPTS", "3")),
            'CELL_MAPPING': {
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
        }
    
    def save_spreadsheet_config(self, spreadsheet_id, spreadsheet_name=None):
        """Salva a configuração da planilha para o usuário atual"""
        if not self.user_id:
            raise ValueError("Nenhum usuário logado para salvar configurações")
        
        self.db_manager.save_spreadsheet_config(self.user_id, spreadsheet_id, spreadsheet_name)
        # Recarrega as configurações
        self.settings = self._load_user_settings()
    
    def save_google_credentials(self, credentials_json):
        """Salva as credenciais do Google para o usuário atual"""
        if not self.user_id:
            raise ValueError("Nenhum usuário logado para salvar credenciais")
        
        self.db_manager.save_google_credentials(self.user_id, credentials_json)
        # Recarrega as configurações
        self.settings = self._load_user_settings()
    
    def __getattr__(self, name):
        """Permite acesso às configurações como atributos"""
        return self.settings.get(name)
    
    def get(self, key, default=None):
        """Método para obter configurações com valor padrão"""
        return self.settings.get(key, default)