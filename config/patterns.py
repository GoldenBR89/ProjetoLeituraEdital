import re

class ExtractionPatterns:
    COMMON_PATTERNS = {
        "orgao_1": r"ORGÃO:\s*([^\n]+)",
        "orgao_2": r"ENTIDADE:\s*([^\n]+)",
        "orgao_3": r"ÓRGÃO:\s*([^\n]+)",
        "cnpj_1": r"CNPJ\s*[:\s]*([\d\.\-\/]{14,18})",
        "cnpj_2": r"(?:CNPJ|Cadastro Nacional|Inscrição Estadual)\s*[:\s]*([\d\.\-\/]{14,18})",
        "cidade_estado_1": r"([\w\s\-]+)\s*[-–]\s*(?:Estado do|do|da|de)\s*([\w\s]+)",
        "cidade_estado_2": r"Município:\s*([^\n]+)\s*[-–]\s*UF:\s*([^\n]+)",
        "processo_1": r"PROCESSO\s*[:\s]*([\d\./\-]+)",
        "pregao_1": r"PREGÃO(?:\s+ELETRÔNICO)?\s*(?:Nº|N\.º|No)\s*([\d\./\-]+)",
        "telefone_1": r"Telefones?:\s*([\d\(\)\-\s\+]+)",
        "telefone_2": r"Fone(?:s)?:\s*([\d\(\)\-\s\+]+)",
        "email_1": r"E-mails?:\s*([\w\.\-]+@[\w\.\-]+\.\w+)",
        "prazo_pagamento_1": r"Prazo\s+de\s+pagamento\s*[:\s]*([^\n]+)",
        "plataforma_1": r"Plataforma\s*[:\s]*([^\n]+)",
        "uasg_1": r"UASG\s*[:\s]*(\d+)",
        "modalidade_1": r"MODALIDADE\s*[:\s]*([^\n]+)",
        "prazo_entrega_1": r"Prazo\s+de\s+entrega\s*[:\s]*([^\n]+)",
        "local_entrega_1": r"Local\s+de\s+entrega\s*[:\s]*([^\n]+)",
        "validade_proposta_1": r"Validade\s+da\s+proposta\s*[:\s]*([^\n]+)",
        "catalogo_tecnico_1": r"Catálogo\s+técnico\s*[:\s]*([^\n]+)",
        "modo_disputa_1": r"Modo\s+de\s+Disputa\s*[:\s]*([^\n]+)",
    }
    
    @classmethod
    def extract_field(cls, field_name, text):
        patterns = {
            "Orgão": ["orgao_1", "orgao_2", "orgao_3"],
            "CNPJ Órgão": ["cnpj_1", "cnpj_2"],
            "Cidade e Estado": ["cidade_estado_1", "cidade_estado_2"],
            "Nº Pregão e Processo": ["processo_1", "pregao_1"],
            "Telefones": ["telefone_1", "telefone_2"],
            "E-mail": ["email_1"],
            "Prazo de pagamento": ["prazo_pagamento_1"],
            "Plataforma": ["plataforma_1"],
            "UASG": ["uasg_1"],
            "Modalidade de compra": ["modalidade_1"],
            "Prazo de entrega": ["prazo_entrega_1"],
            "Local de entrega": ["local_entrega_1"],
            "Validade da proposta": ["validade_proposta_1"],
            "Catálogo técnico": ["catalogo_tecnico_1"],
            "Modo de Disputa": ["modo_disputa_1"],
        }
        
        field_patterns = patterns.get(field_name, [])
        for pattern_name in field_patterns:
            pattern = cls.COMMON_PATTERNS[pattern_name]
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if field_name == "Nº Pregão e Processo":
                    processo = match.group(1) if match.groups() else ""
                    pregao_match = re.search(cls.COMMON_PATTERNS["pregao_1"], text, re.IGNORECASE)
                    pregao = pregao_match.group(1) if pregao_match else ""
                    return f"PROCESSO ADMINISTRATIVO No {processo} | PREGÃO ELETRÔNICO No {pregao}"
                
                elif field_name == "Cidade e Estado" and len(match.groups()) >= 2:
                    cidade = match.group(1).strip()
                    estado = match.group(2).strip()
                    return f"{cidade} - {estado}"
                
                return match.group(0).strip()
        
        return "NÃO ENCONTRADO"