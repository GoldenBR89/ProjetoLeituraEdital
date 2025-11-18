# gui_app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from main import batch_process_mode, watch_folder_mode, FileManager
from config.settings import Settings

class LicitationExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Extrator de Editais v1.0")
        self.root.geometry("800x600")

        # --- Layout Principal ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar pesos das colunas e linhas para expansão
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # --- Widgets ---
        # Botão Selecionar PDFs
        self.select_pdf_btn = ttk.Button(main_frame, text="1. Selecionar PDF(s)", command=self.select_pdfs)
        self.select_pdf_btn.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # Botão Processar
        self.process_btn = ttk.Button(main_frame, text="2. Processar PDFs", command=self.start_processing, state=tk.DISABLED)
        self.process_btn.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # Botão Configurações
        self.settings_btn = ttk.Button(main_frame, text="3. Configurações", command=self.open_settings)
        self.settings_btn.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Barra de Progresso
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Área de Log
        self.log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status Bar
        self.status_var = tk.StringVar(value="Pronto.")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # --- Variáveis ---
        self.selected_pdfs = []
        self.settings_window = None

        # --- Inicializar ---
        self.setup_logging()

    def setup_logging(self):
        """Configura a exibição de logs na área de texto."""
        import logging

        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)  # Rola para o final
                self.text_widget.config(state=tk.DISABLED)

        # Configuração básica de logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # Adiciona o handler personalizado
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(text_handler)

    def select_pdfs(self):
        """Abre o diálogo para selecionar PDFs."""
        filetypes = (
            ('PDF files', '*.pdf'),
            ('All files', '*.*')
        )
        filenames = filedialog.askopenfilenames(
            title='Selecione os arquivos PDF do edital',
            initialdir='.',
            filetypes=filetypes
        )
        if filenames:
            self.selected_pdfs = list(filenames)
            self.process_btn.config(state=tk.NORMAL)
            logging.info(f"{len(self.selected_pdfs)} PDF(s) selecionado(s).")
            self.status_var.set(f"{len(self.selected_pdfs)} PDF(s) selecionado(s). Clique em Processar.")

    def start_processing(self):
        """Inicia o processamento em uma thread separada."""
        if not self.selected_pdfs:
            messagebox.showwarning("Aviso", "Nenhum PDF selecionado.")
            return

        # Copia os PDFs selecionados para a pasta 'to_process'
        file_manager = FileManager()
        for pdf_path in self.selected_pdfs:
            dest_path = os.path.join(file_manager.settings.PDF_TO_PROCESS, os.path.basename(pdf_path))
            # Evita sobrescrever
            counter = 1
            name, ext = os.path.splitext(dest_path)
            while os.path.exists(dest_path):
                dest_path = f"{name}_{counter}{ext}"
                counter += 1
            import shutil
            shutil.copy2(pdf_path, dest_path)
            logging.info(f"PDF copiado para processamento: {dest_path}")

        # Desabilita botões durante o processamento
        self.select_pdf_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)
        self.settings_btn.config(state=tk.DISABLED)

        # Inicia a thread de processamento
        processing_thread = threading.Thread(target=self.run_batch_processing)
        processing_thread.start()

    def run_batch_processing(self):
        """Executa o modo em lote do main.py."""
        try:
            # Limpa a pasta de processados antigos (opcional)
            # file_manager = FileManager()
            # import shutil
            # for f in os.listdir(file_manager.settings.PDF_PROCESSED):
            #     os.remove(os.path.join(file_manager.settings.PDF_PROCESSED, f))

            # Executa o processamento em lote
            batch_process_mode() # Esta função já está no seu main.py
            logging.info("Processamento concluído com sucesso.")
        except Exception as e:
            logging.error(f"Erro durante o processamento: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento:\n{e}")
        finally:
            # Reabilita botões após o processamento
            self.root.after(0, self.enable_buttons)

    def enable_buttons(self):
        """Reabilita os botões após o processamento."""
        self.select_pdf_btn.config(state=tk.NORMAL)
        self.process_btn.config(state=tk.NORMAL)
        self.settings_btn.config(state=tk.NORMAL)
        self.status_var.set("Processamento concluído.")

    def open_settings(self):
        """Abre a janela de configurações."""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift() # Traz a janela para frente se já estiver aberta
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Configurações")
        self.settings_window.geometry("500x300")
        self.settings_window.resizable(False, False)

        # Layout da janela de configurações
        settings_frame = ttk.Frame(self.settings_window, padding="10")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Label e Entry para SPREADSHEET_ID
        ttk.Label(settings_frame, text="ID da Planilha Google Sheets:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.spreadsheet_id_var = tk.StringVar(value=Settings.SPREADSHEET_ID)
        id_entry = ttk.Entry(settings_frame, textvariable=self.spreadsheet_id_var, width=60)
        id_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(0, weight=1)

        # Botão Salvar
        save_btn = ttk.Button(settings_frame, text="Salvar", command=self.save_settings)
        save_btn.grid(row=2, column=0, pady=(10, 0))

    def save_settings(self):
        """Salva as configurações alteradas no .env."""
        new_id = self.spreadsheet_id_var.get().strip()
        if not new_id:
            messagebox.showwarning("Aviso", "ID da planilha não pode ser vazio.")
            return

        # Lê o arquivo .env
        env_path = ".env"
        if not os.path.exists(env_path):
            # Se .env não existir, tenta copiar .env.example
            if os.path.exists(".env.example"):
                import shutil
                shutil.copy(".env.example", env_path)
                logging.info("Arquivo .env criado a partir de .env.example")
            else:
                messagebox.showerror("Erro", "Arquivo .env não encontrado e .env.example também não.")
                return

        # Lê o conteúdo atual do .env
        with open(env_path, "r", encoding="utf-8") as f:
            env_content = f.read()

        # Substitui ou adiciona a linha SPREADSHEET_ID
        import re
        if re.search(r'^SPREADSHEET_ID=.*$', env_content, re.MULTILINE):
            # Se a linha já existe, substitui
            env_content = re.sub(r'^SPREADSHEET_ID=.*$', f'SPREADSHEET_ID={new_id}', env_content, flags=re.MULTILINE)
        else:
            # Se a linha não existe, adiciona
            env_content += f"\nSPREADSHEET_ID={new_id}\n"

        # Escreve o conteúdo modificado de volta ao .env
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        logging.info("Configurações salvas no arquivo .env.")
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")


if __name__ == "__main__":
    root = tk.Tk()
    app = LicitationExtractorGUI(root)
    root.mainloop()