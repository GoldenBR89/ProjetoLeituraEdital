import sqlite3
import os
from cryptography.fernet import Fernet

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'users.db')
        self.key_path = os.path.join(os.path.dirname(__file__), 'encryption.key')
        self._init_encryption_key()
        self._init_database()
    
    def _init_encryption_key(self):
        """Gera ou carrega a chave de criptografia"""
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
        else:
            with open(self.key_path, 'rb') as key_file:
                key = key_file.read()
        self.cipher_suite = Fernet(key)
    
    def _init_database(self):
        """Cria as tabelas do banco de dados se não existirem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabela de configurações do Google Sheets
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sheet_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            spreadsheet_id TEXT NOT NULL,
            spreadsheet_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        
        # Tabela para armazenar credenciais do Google criptografadas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_google_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            encrypted_credentials BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_by_username(self, username):
        """Obtém informações do usuário pelo nome de usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def create_user(self, username, name, email, password_hash):
        """Cria um novo usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO users (username, name, email, password_hash)
            VALUES (?, ?, ?, ?)
            ''', (username, name, email, password_hash))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
        finally:
            conn.close()
    
    def save_google_credentials(self, user_id, credentials_json):
        """Salva credenciais do Google criptografadas"""
        encrypted_data = self.cipher_suite.encrypt(credentials_json.encode())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO user_google_credentials (user_id, encrypted_credentials)
        VALUES (?, ?)
        ''', (user_id, encrypted_data))
        conn.commit()
        conn.close()
    
    def get_google_credentials(self, user_id):
        """Obtém credenciais do Google descriptografadas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT encrypted_credentials FROM user_google_credentials WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            encrypted_data = result[0]
            decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
            return decrypted_data
        return None
    
    def save_spreadsheet_config(self, user_id, spreadsheet_id, spreadsheet_name=None):
        """Salva configuração da planilha do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO user_sheet_configs (user_id, spreadsheet_id, spreadsheet_name)
        VALUES (?, ?, ?)
        ''', (user_id, spreadsheet_id, spreadsheet_name))
        conn.commit()
        conn.close()
    
    def get_spreadsheet_config(self, user_id):
        """Obtém configuração da planilha do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT spreadsheet_id, spreadsheet_name FROM user_sheet_configs WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'spreadsheet_id': result[0],
                'spreadsheet_name': result[1] or 'Minha Planilha'
            }
        return None