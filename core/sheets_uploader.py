import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.settings import Settings

class SheetsUploader:
    def __init__(self):
        self.settings = Settings()
        self.creds = self._authenticate()
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def _authenticate(self):
        creds = None
        token_path = 'token.pickle'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    ['https://www.googleapis.com/auth/spreadsheets']
                )
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def update_sheet(self, data, edital_link=None):
        if edital_link:
            data["Edital de Licitação"] = edital_link
        elif "Edital de Licitação" not in data:
            data["Edital de Licitação"] = "LINK_NÃO_FORNECIDO"
        
        batch_data = []
        
        for field, cell_ref in self.settings.CELL_MAPPING.items():
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
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.settings.SPREADSHEET_ID,
                body=body
            ).execute()
            
            print(f"✅ {len(batch_data)} campos atualizados na planilha!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar planilha: {str(e)}")
            return False
    
    def clear_sheet(self):
        batch_data = []
        for cell_ref in self.settings.CELL_MAPPING.values():
            batch_data.append({
                "range": cell_ref,
                "values": [[""]]
            })
        
        try:
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": batch_data
            }
            
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.settings.SPREADSHEET_ID,
                body=body
            ).execute()
            
            print("✅ Planilha limpa para novo edital!")
            return True
        except Exception as e:
            print(f"❌ Erro ao limpar planilha: {str(e)}")
            return False