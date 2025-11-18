import os
import pickle
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.settings import Settings
from config.user_settings import UserSettings
from utils.file_manager import FileManager

class SheetsUploader:
    def __init__(self, user_id=None, username=None):
        self.user_settings = UserSettings(user_id, username)
        self.creds = self._authenticate()
        self.service = build('sheets', 'v4', credentials=self.creds) if self.creds else None
    
    def _authenticate(self):
        """Autentica com base nas credenciais do usuário logado"""
        creds = None
        token_path = f'token_{self.user_settings.user_id}.pickle' if self.user_settings.user_id else 'token.pickle'
        
        # Tenta carregar token existente
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não tem credenciais válidas, precisa autenticar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Erro ao refresh token: {str(e)}")
                    return None
            
            else:
                # Usa as credenciais do usuário ou as padrão
                google_credentials = self.user_settings.GOOGLE_CREDENTIALS
                if google_credentials:
                    # Salva credenciais temporariamente para usar no fluxo OAuth
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                        json.dump(json.loads(google_credentials), temp_file)
                        temp_file_path = temp_file.name
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            temp_file_path,
                            ['https://www.googleapis.com/auth/spreadsheets']
                        )
                        os.unlink(temp_file_path)  # Remove o arquivo temporário
                    except Exception as e:
                        logger.error(f"Erro ao criar fluxo OAuth: {str(e)}")
                        return None
                else:
                    # Usa credenciais padrão
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json',
                        ['https://www.googleapis.com/auth/spreadsheets']
                    )
                
                try:
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"Erro ao autenticar com Google: {str(e)}")
                    return None
            
            # Salva o token
            if creds:
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
        
        return creds
    
    def update_sheet(self, data, edital_link=None):
        """Atualiza a planilha com dados extraídos"""
        spreadsheet_id = self.user_settings.SPREADSHEET_ID
        
        if edital_link:
            data["Edital de Licitação"] = edital_link
        elif "Edital de Licitação" not in 
            data["Edital de Licitação"] = "LINK_NÃO_FORNECIDO"
        
        batch_data = []
        
        for field, cell_ref in self.user_settings.CELL_MAPPING.items():
            value = data.get(field, "NÃO ENCONTRADO")
            
            if field == "Nº Pregão e Processo" and "NÃO ENCONTRADO" not in value:
                value = value.replace("PROCESSO ADMINISTRATIVO No", "PROCESSO:").replace("PREGÃO ELETRÔNICO No", "PREGÃO:")
            
            batch_data.append({
                "range": cell_ref,
                "values": [[value]]
            })
        
        try:
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": batch_data
            }
            
            if self.service is None:
                logger.error("Serviço do Google Sheets não inicializado.")
                return False
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"✅ {len(batch_data)} campos atualizados na planilha!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar planilha: {str(e)}")
            return False
    
    def clear_sheet(self):
        """Limpa os campos da planilha para novo edital"""
        spreadsheet_id = self.user_settings.SPREADSHEET_ID
        batch_data = []
        
        for cell_ref in self.user_settings.CELL_MAPPING.values():
            batch_data.append({
                "range": cell_ref,
                "values": [[""]]
            })
        
        try:
            if self.service is None:
                logger.error("Serviço do Google Sheets não inicializado.")
                return False
            
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": batch_data
            }
            
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info("✅ Planilha limpa para novo edital!")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao limpar planilha: {str(e)}")
            return False