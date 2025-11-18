import sqlite3
import os
from database.init_db import DatabaseManager

def initialize_system():
    """Inicializa o sistema e cria o banco de dados"""
    print("Inicializando sistema de extração de editais...")
    db_manager = DatabaseManager()
    
    # Verifica se há usuários existentes
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database', 'users.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"Sistema inicializado com sucesso!")
    print(f"Total de usuários cadastrados: {user_count}")
    
    # Cria pasta para tokens se não existir
    if not os.path.exists('data'):
        os.makedirs('data/to_process')
        os.makedirs('data/processed')
        print("Pastas de dados criadas.")

if __name__ == "__main__":
    initialize_system()