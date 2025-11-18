import re

class ExtractionPatterns:
    """Padrões regex especializados para extração de editais brasileiros com base em variações reais"""

    COMMON_PATTERNS = {
        # Orgão - Várias formas comuns
        "orgao_1": r"ÓRGÃO\s*[:\s]*([A-Z][A-Za-z\s\.\-]+)",
        "orgao_2": r"ORGÃO\s*[:\s]*([A-Z][A-Za-z\s\.\-]+)",
        "orgao_3": r"ENTIDADE\s*[:\s]*([A-Z][A-Za-z\s\.\-]+)",
        "orgao_4": r"PREFEITURA\s+MUNICIPAL\s+DE\s+([A-Z][A-Za-z\s\-]+)",
        "orgao_5": r"SECRETARIA\s+MUNICIPAL\s+DE\s+[A-Z][a-z\s]+(?:\s+DE\s+[A-Z][a-z\s]+)?\s+DE\s+([A-Z][A-Za-z\s\-]+)",
        "orgao_6": r"GOVERNO\s+DO\s+ESTADO\s+DE\s+([A-Z][A-Za-z\s\-]+)",
        "orgao_7": r"([A-Z][A-Za-z\s]+)\s*-\s*([A-Z]{2})\b",
        
        # CNPJ Órgão - Vários formatos
        "cnpj_1": r"CNPJ\s*[:\s]*([\d\.\-\/]{14,18})",
        "cnpj_2": r"CNPJ\s+nº\s*([\d\.\-\/]{14,18})",
        "cnpj_3": r"INSCRIÇÃO\s+NO\s+CNPJ\s*[:\s]*([\d\.\-\/]{14,18})",
        "cnpj_4": r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})",
        "cnpj_5": r"(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})",
        
        # Cidade e Estado - Vários formatos
        "cidade_estado_1": r"([\w\s\-]+)\s*[-–]\s*(?:Estado do|do|da|de)\s*([\w\s]+)",
        "cidade_estado_2": r"([\w\s\-]+)\s*-\s*([A-Z]{2})\b",
        "cidade_estado_3": r"Local\s+de\s+Entrega\s*[:\s]*([\w\s\-]+)\s*,\s*([A-Z]{2})\b",
        "cidade_estado_4": r"Município:\s*([\w\s\-]+)\s*-\s*UF:\s*([^\n]+)",
        "cidade_estado_5": r"Endereço\s+de\s+entrega\s*[:\s]*([^\n]+)",
        "cidade_estado_6": r"(\w+)\s*-\s*([A-Z]{2})\b",
        
        # Nº Pregão e Processo - Vários formatos
        "processo_1": r"Processo\s+Administrativo\s*[:\s]*No\s*([\d\./\-]+)",
        "processo_2": r"PROCESSO\s+ADMINISTRATIVO\s+No\s+([\d\./\-]+)",
        "processo_3": r"Processo\s+de\s+Compras\s*[:\s]*No\s*([\d\./\-]+)",
        "pregao_1": r"PREGÃO\s+ELETRÔNICO\s+No\s+([\d\./\-]+)",
        "pregao_2": r"Processo\s+de\s+Pregão\s*[:\s]*No\s*([\d\./\-]+)",
        "pregao_3": r"Nº\s+do\s+Pregão\s*[:\s]*([\d\./\-]+)",
        "processo_pregao_1": r"PROCESSO\s+ADMINISTRATIVO\s+No\s+([\d\./\-]+)\s*\|\s*PREGÃO\s+ELETRÔNICO\s+No\s+([\d\./\-]+)",
        
        # Telefones - Vários formatos
        "telefone_1": r"Fone\s*[:\s]*\((\d{2})\)\s*(\d{4,5})[-\s]*(\d{4})",
        "telefone_2": r"Telefones?\s*[:\s]*\((\d{2})\)\s*(\d{4,5})[-\s]*(\d{4})",
        "telefone_3": r"Contato\s*[:\s]*\((\d{2})\)\s*(\d{4,5})[-\s]*(\d{4})",
        "telefone_4": r"(\(\d{2}\)\s*\d{4,5}[-\s]*\d{4})",
        "telefone_5": r"(\d{2}\s*\d{4,5}[-\s]*\d{4})",
        "telefone_6": r"(\d{2}[\s-]\d{4,5}[\s-]\d{4})",
        
        # E-mail
        "email_1": r"E[-]mail\s*[:\s]*([\w\.\-]+@[\w\.\-]+\.\w+)",
        "email_2": r"e[-]mail\s*[:\s]*([\w\.\-]+@[\w\.\-]+\.\w+)",
        "email_3": r"contato@[\w\.\-]+\.\w+",
        "email_4": r"(\w+@[\w\.\-]+\.\w+)",
        
        # Prazo de pagamento - Vários formatos
        "prazo_pagamento_1": r"Prazo\s+de\s+pagamento\s*[:\s]*([\d]+)\s+dias\s+após",
        "prazo_pagamento_2": r"Forma\s+de\s+pagamento\s*[:\s]*([\d]+)\s+dias\s+após",
        "prazo_pagamento_3": r"(\d+)\s+dias\s+após\s+a\s+entrega",
        "prazo_pagamento_4": r"(\d+)\s+dias\s+após\s+a\s+recepção",
        
        # Plataforma - Vários sistemas comuns
        "plataforma_1": r"Plataforma\s+de\s+Licitação\s*[:\s]*(Bolsa\s+de\s+Licitações|BLL|Comprasnet|Portal\s+de\s+Compras\s+Públicas|LICITAÇÃO|PREGÃO|BANRISUL|BANDEP|BANPARÁ|BANESPA|BANESPS|BANESTES)",
        "plataforma_2": r"Plataforma\s+eletrônica\s*[:\s]*(Bolsa\s+de\s+Licitações|BLL|Comprasnet|Portal\s+de\s+Compras\s+Públicas)",
        "plataforma_3": r"Plataforma\s+de\s+Pregão\s+Eletrônico\s*[:\s]*(Bolsa\s+de\s+Licitações|BLL|Comprasnet)",
        "plataforma_4": r"Plataforma\s+do\s+Pregão\s+Eletrônico\s*[:\s]*(Bolsa\s+de\s+Licitações|BLL|Comprasnet)",
        
        # UASG
        "uasg_1": r"UASG\s*[:\s]*(\d+)",
        "uasg_2": r"Código\s+UASG\s*[:\s]*(\d+)",
        "uasg_3": r"(\d{6})",
        
        # Modalidade de compra
        "modalidade_1": r"Modalidade\s+de\s+compra\s*[:\s]*(PREGÃO|DISPENSA|INEXIGIBILIDADE|TOMADA DE PREÇOS|CONCORRÊNCIA|CONVITE|LEILÃO|REGISTRO DE PREÇO)",
        "modalidade_2": r"Tipo\s+de\s+Licitação\s*[:\s]*(PREGÃO|DISPENSA|INEXIGIBILIDADE|TOMADA DE PREÇOS|CONCORRÊNCIA|CONVITE|LEILÃO|REGISTRO DE PREÇO)",
        "modalidade_3": r"REGISTRO DE PREÇO",
        "modalidade_4": r"MODALIDADE\s+DE\s+LICITAÇÃO\s*[:\s]*(PREGÃO|DISPENSA|INEXIGIBILIDADE|TOMADA DE PREÇOS|CONCORRÊNCIA|CONVITE|LEILÃO|REGISTRO DE PREÇO)",
        "modalidade_5": r"(\w+[\s,;]?\s*(\w+))",
        
        # Prazo de entrega
        "prazo_entrega_1": r"Prazo\s+de\s+entrega\s*[:\s]*([\d]+)\s+dias\s+úteis",
        "prazo_entrega_2": r"Prazo\s+de\s+entrega\s*[:\s]*([\d]+)\s+dias",
        "prazo_entrega_3": r"Entrega\s+em\s+até\s+([\d]+)\s+dias",
        "prazo_entrega_4": r"([\d]+)\s+dias\s+úteis\s+após\s+a\s+ordem\s+de\s+compra",
        "prazo_entrega_5": r"(\d+)\s+dia[s]?",
        
        # Local de entrega
        "local_entrega_1": r"Local\s+de\s+entrega\s*[:\s]*([^\n]+)",
        "local_entrega_2": r"Endereço\s+de\s+entrega\s*[:\s]*([^\n]+)",
        "local_entrega_3": r"Entrega\s+no\s+endereço\s+de\s+[\w\s]+:\s*([^\n]+)",
        "local_entrega_4": r"Local\s+de\s+entrega:\s*([^\n]+)",
        
        # Validade da proposta
        "validade_proposta_1": r"Validade\s+da\s+proposta\s*[:\s]*([\d]+)\s+dias",
        "validade_proposta_2": r"Proposta\s+válida\s+por\s+([\d]+)\s+dias",
        "validade_proposta_3": r"Validade\s+da\s+proposta\s*[:\s]*([\d]+)\s+dia[s]?",
        "validade_proposta_4": r"(\d+)\s+dias\s+após\s+a\s+entrega",
        
        # Catálogo técnico
        "catalogo_tecnico_1": r"Catálogo\s+técnico\s*[:\s]*(Sim|Não)",
        "catalogo_tecnico_2": r"Catálogo\s+técnico\s*[:\s]*(necessário|obrigatório|requisito)",
        "catalogo_tecnico_3": r"Necessário\s+catálogo\s+técnico\s+para\s+itens\s+específicos",
        "catalogo_tecnico_4": r"É\s+necessário\s+fornecer\s+catálogo\s+técnico",
        "catalogo_tecnico_5": r"Catálogo\s+Técnico\s*[:\s]*([^\n]+)",
        
        # Modo de Disputa
        "modo_disputa_1": r"Modo\s+de\s+disputa\s*[:\s]*(Aberto|Fechar|Aberto e Fechado)",
        "modo_disputa_2": r"Disputa\s+em\s+duas\s+fases\s*[:\s]*(Aberto|Fechar|Aberto e Fechado)",
        "modo_disputa_3": r"MODALIDADE\s+DE\s+DISPUTA\s*[:\s]*(Aberto|Fechar|Aberto e Fechado)",
        "modo_disputa_4": r"MODO\s+DE\s+DISPUTA\s+ABERTO",
        "modo_disputa_5": r"MODO\s+DE\s+DISPUTA\s+ABERTO E FECHADO",
        "modo_disputa_6": r"(\w+[\s,;]?\s*(\w+))",
    }
    
    @classmethod
    def extract_field(cls, field_name, text):
        """Extrai um campo específico usando múltiplos padrões de fallback"""
        patterns = {
            "Orgão": ["orgao_1", "orgao_2", "orgao_3", "orgao_4", "orgao_5", "orgao_6", "orgao_7"],
            "CNPJ Órgão": ["cnpj_1", "cnpj_2", "cnpj_3", "cnpj_4", "cnpj_5"],
            "Cidade e Estado": ["cidade_estado_1", "cidade_estado_2", "cidade_estado_3", "cidade_estado_4", "cidade_estado_5", "cidade_estado_6"],
            "Nº Pregão e Processo": ["processo_1", "processo_2", "processo_3", "pregao_1", "pregao_2", "pregao_3", "processo_pregao_1"],
            "Telefones": ["telefone_1", "telefone_2", "telefone_3", "telefone_4", "telefone_5", "telefone_6"],
            "E-mail": ["email_1", "email_2", "email_3", "email_4"],
            "Prazo de pagamento": ["prazo_pagamento_1", "prazo_pagamento_2", "prazo_pagamento_3", "prazo_pagamento_4"],
            "Plataforma": ["plataforma_1", "plataforma_2", "plataforma_3", "plataforma_4"],
            "UASG": ["uasg_1", "uasg_2", "uasg_3"],
            "Modalidade de compra": ["modalidade_1", "modalidade_2", "modalidade_3", "modalidade_4", "modalidade_5"],
            "Prazo de entrega": ["prazo_entrega_1", "prazo_entrega_2", "prazo_entrega_3", "prazo_entrega_4", "prazo_entrega_5"],
            "Local de entrega": ["local_entrega_1", "local_entrega_2", "local_entrega_3", "local_entrega_4"],
            "Validade da proposta": ["validade_proposta_1", "validade_proposta_2", "validade_proposta_3", "validade_proposta_4"],
            "Catálogo técnico": ["catalogo_tecnico_1", "catalogo_tecnico_2", "catalogo_tecnico_3", "catalogo_tecnico_4", "catalogo_tecnico_5"],
            "Modo de Disputa": ["modo_disputa_1", "modo_disputa_2", "modo_disputa_3", "modo_disputa_4", "modo_disputa_5", "modo_disputa_6"],
        }
        
        field_patterns = patterns.get(field_name, [])
        for pattern_name in field_patterns:
            pattern = cls.COMMON_PATTERNS[pattern_name]
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Processamento especial para campos compostos
                if field_name == "Nº Pregão e Processo":
                    if len(match.groups()) >= 2:
                        processo = match.group