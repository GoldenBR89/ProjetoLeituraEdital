import re

class ExtractionPatterns:
    """Padrões regex especializados para extração de editais brasileiros"""
    
    COMMON_PATTERNS = {
        # Padrões para Orgão
        "orgao_1": r"ORGÃO:\s*([^\n]+)",
        "orgao_2": r"ENTIDADE:\s*([^\n]+)",
        "orgao_3": r"ÓRGÃO:\s*([^\n]+)",
        "orgao_4": r"PREFEITURA\s+MUN\.\s+DE\s+([^\n]+)",  # Ex: PREFEITURA MUN. DE DOM MACEDO COSTA
        
        # Padrões para CNPJ Órgão
        "cnpj_1": r"CNPJ\s*[:\s]*([\d\.\-\/]{14,18})",
        "cnpj_2": r"(?:CNPJ|Cadastro Nacional|Inscrição Estadual)\s*[:\s]*([\d\.\-\/]{14,18})",
        "cnpj_3": r"CNPJ\s+nº\s*([\d\.\-\/]{14,18})",  # Ex: CNPJ nº 13.827.019/0001-58
        
        # Padrões para Cidade e Estado
        "cidade_estado_1": r"([\w\s\-]+)\s*[-–]\s*(?:Estado do|do|da|de)\s*([\w\s]+)",
        "cidade_estado_2": r"Município:\s*([^\n]+)\s*[-–]\s*UF:\s*([^\n]+)",
        "cidade_estado_3": r"([\w\s\-]+)\s*-\s*([\w\s]+)",  # Ex: Dom Macedo Costa - BA
        
        # Padrões para Nº Pregão e Processo
        "processo_1": r"PROCESSO\s*[:\s]*([\d\./\-]+)",
        "processo_2": r"PROCESSO\s+ADMINISTRATIVO\s+No\s+([\d\./\-]+)",  # Ex: PROCESSO ADMINISTRATIVO No 021/2025
        "pregao_1": r"PREGÃO(?:\s+ELETRÔNICO)?\s*(?:Nº|N\.º|No)\s*([\d\./\-]+)",
        "pregao_2": r"PREGÃO\s+ELETRÔNICO\s+No\s+([\d\./\-]+)",  # Ex: PREGÃO ELETRÔNICO No 021/2025
        
        # Padrões para Telefones
        "telefone_1": r"Telefones?:\s*([\d\(\)\-\s\+]+)",
        "telefone_2": r"Fone(?:s)?:\s*([\d\(\)\-\s\+]+)",
        "telefone_3": r"Fone\/Fax:\s*([\d\(\)\-\s\+\/]+)",  # Ex: Fone/Fax: (75)3648-2127/ 3648-2169
        
        # Padrões para E-mail (geralmente não encontrado em editais oficiais)
        "email_1": r"E-mails?:\s*([\w\.\-]+@[\w\.\-]+\.\w+)",
        
        # Padrões para Prazo de pagamento (muito variável, difícil de padronizar)
        "prazo_pagamento_1": r"Prazo\s+de\s+pagamento\s*[:\s]*([^\n]+)",
        
        # Padrões para Plataforma
        "plataforma_1": r"Plataforma\s*[:\s]*([^\n]+)",
        "plataforma_2": r"plataforma\s+eletrônica\s+([^\n]+)",  # Ex: plataforma eletrônica Bolsa de Licitações e Leilões – BLL
        
        # Padrões para UASG (muitas vezes não explicitamente marcado como UASG)
        "uasg_1": r"UASG\s*[:\s]*(\d+)",
        
        # Padrões para Modalidade de compra
        "modalidade_1": r"MODALIDADE\s*[:\s]*([^\n]+)",
        "modalidade_2": r"modalidade\s+([^\n]+)",  # Ex: modalidade PREGÃO, PARA REGISTRO DE PREÇO
        
        # Padrões para Prazo de entrega (muito variável)
        "prazo_entrega_1": r"Prazo\s+de\s+entrega\s*[:\s]*([^\n]+)",
        
        # Padrões para Local de entrega (muito variável)
        "local_entrega_1": r"Local\s+de\s+entrega\s*[:\s]*([^\n]+)",
        
        # Padrões para Validade da proposta (muito variável)
        "validade_proposta_1": r"Validade\s+da\s+proposta\s*[:\s]*([^\n]+)",
        
        # Padrões para Catálogo técnico (muitas vezes não explicitamente marcado)
        "catalogo_tecnico_1": r"Catálogo\s+técnico\s*[:\s]*([^\n]+)",
        
        # Padrões para Modo de Disputa
        "modo_disputa_1": r"Modo\s+de\s+Disputa\s*[:\s]*([^\n]+)",
        "modo_disputa_2": r"MODO\s+DE\s+DISPUTA\s+([^\n]+)",  # Ex: MODO DE DISPUTA ABERTO E FECHADO
    }
    
    @classmethod
    def extract_field(cls, field_name, text):
        """Extrai um campo específico usando múltiplos padrões de fallback"""
        patterns = {
            "Orgão": ["orgao_1", "orgao_2", "orgao_3", "orgao_4"],
            "CNPJ Órgão": ["cnpj_1", "cnpj_2", "cnpj_3"],
            "Cidade e Estado": ["cidade_estado_1", "cidade_estado_2", "cidade_estado_3"],
            "Nº Pregão e Processo": ["processo_1", "processo_2", "pregao_1", "pregao_2"], # Combina processo e pregão
            "Telefones": ["telefone_1", "telefone_2", "telefone_3"],
            "E-mail": ["email_1"],
            "Prazo de pagamento": ["prazo_pagamento_1"],
            "Plataforma": ["plataforma_1", "plataforma_2"],
            "UASG": ["uasg_1"],
            "Modalidade de compra": ["modalidade_1", "modalidade_2"],
            "Prazo de entrega": ["prazo_entrega_1"],
            "Local de entrega": ["local_entrega_1"],
            "Validade da proposta": ["validade_proposta_1"],
            "Catálogo técnico": ["catalogo_tecnico_1"],
            "Modo de Disputa": ["modo_disputa_1", "modo_disputa_2"],
        }
        
        field_patterns = patterns.get(field_name, [])
        for pattern_name in field_patterns:
            pattern = cls.COMMON_PATTERNS[pattern_name]
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Processamento especial para campos compostos (ex: Nº Pregão e Processo)
                if field_name == "Nº Pregão e Processo":
                    processo_match = re.search(cls.COMMON_PATTERNS["processo_2"], text, re.IGNORECASE)
                    pregao_match = re.search(cls.COMMON_PATTERNS["pregao_2"], text, re.IGNORECASE)
                    processo = processo_match.group(1) if processo_match else ""
                    pregao = pregao_match.group(1) if pregao_match else ""
                    if processo and pregao:
                        return f"PROCESSO ADMINISTRATIVO No {processo} | PREGÃO ELETRÔNICO No {pregao}"
                    elif processo:
                        return f"PROCESSO ADMINISTRATIVO No {processo}"
                    elif pregao:
                        return f"PREGÃO ELETRÔNICO No {pregao}"
                
                # Processamento especial para Cidade e Estado
                elif field_name == "Cidade e Estado" and len(match.groups()) >= 2:
                    cidade = match.group(1).strip()
                    estado = match.group(2).strip()
                    return f"{cidade} - {estado}"
                
                return match.group(1).strip() if match.lastindex else match.group(0).strip()
        
        return "NÃO ENCONTRADO"