import re

class ExtractionPatterns:
    """Padrões regex extremamente aprimorados para análise de editais brasileiros"""

    COMMON_PATTERNS = {

        # ---------------------------
        # ORGÃO (captura robusta)
        # ---------------------------
        "orgao_1": r"(?:ÓRGÃO|ORG[AÃ]O|ENTIDADE)\s*[:\-–]\s*([A-Z0-9][A-Za-z0-9\s\.\-ºª/]+)",
        "orgao_2": r"(PREFEITURA\s+MUNICIPAL\s+DE\s+[A-Z][A-Za-z\s\-]+)",
        "orgao_3": r"(GOVERNO\s+DO\s+ESTADO\s+DE\s+[A-Z][A-Za-z\s\-]+)",
        "orgao_4": r"(SECRETARIA\s+MUNICIPAL\s+DE\s+[A-Z][A-Za-z\s]+)",

        # ---------------------------
        # CNPJ (ultra tolerante)
        # ---------------------------
        "cnpj_1": r"CNPJ\s*[:\-–]?\s*((?:\d{2}\D?\d{3}\D?\d{3}\D?\d{4}\D?\d{2}))",
        "cnpj_2": r"CNPJ\s*(?:Nº|No|N°)?\s*[:\-–]?\s*((?:\d{2}\D?\d{3}\D?\d{3}\D?\d{4}\D?\d{2}))",

        # ---------------------------
        # CIDADE - ESTADO
        # ---------------------------
        "cidade_estado_1": r"([A-Z][A-Za-z\s\-]+)\s*[-–]\s*(?:UF\s*)?([A-Z]{2})\b",
        "cidade_estado_2": r"Munic[ií]pio\s*[:\-–]\s*([A-Z][A-Za-z\s\-]+)\s*[-–]\s*([A-Z]{2})",
        "cidade_estado_3": r"Local\s+de\s+Entrega\s*[:\-–]\s*([^\n,]+)\s*,\s*([A-Z]{2})",

        # ---------------------------
        # PROCESSO / PREGÃO
        # ---------------------------
        "processo_1": r"Processo\s+(?:Administrativo\s*)?(?:Nº|No|N°)?\s*[:\-–]?\s*([\d\.\/\-]+)",
        "processo_2": r"PROCESSO\s+ADMINISTRATIVO\s+(?:Nº|No)?\s*([\d\.\/\-]+)",
        "pregao_1": r"PREG[AÃ]O\s+ELETR[ÔO]NICO\s+(?:Nº|No|N°)?\s*([\d\.\/\-]+)",
        "pregao_2": r"N[úu]mero\s+do\s+Preg[aã]o\s*[:\-–]?\s*([\d\.\/\-]+)",
        "processo_pregao_1": r"PROCESSO.*?([\d\.\/\-]+).*?PREG[AÃ]O.*?([\d\.\/\-]+)",

        # ---------------------------
        # TELEFONE (super tolerante)
        # ---------------------------
        "telefone_1": r"\(?(\d{2})\)?\s*(\d{4,5})[-\s]?(\d{4})",
        "telefone_2": r"Tel(?:efone)?s?[:\s]*(\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4})",

        # ---------------------------
        # EMAIL
        # ---------------------------
        "email_1": r"([\w\.\-]+@[\w\.\-]+\.\w+)",
        "email_2": r"E[- ]?mail\s*[:\-–]?\s*([\w\.\-]+@[\w\.\-]+\.\w+)",

        # ---------------------------
        # PRAZO DE PAGAMENTO
        # ---------------------------
        "prazo_pagamento_1": r"(\d+)\s+dias\s+(?:ap[oó]s|depois)",
        "prazo_pagamento_2": r"Pagamento\s*[:\-–]?\s*(\d+)\s*dias",

        # ---------------------------
        # PLATAFORMA
        # ---------------------------
        "plataforma_1": r"(Comprasnet|BLL|Bolsa\s+de\s+Licita[cç][aã]o|Portal\s+de\s+Compras\s+Públicas)",
        "plataforma_2": r"Preg[aã]o\s+Eletr[oô]nico\s+pela\s+plataforma\s+([A-Za-z\s]+)",

        # ---------------------------
        # UASG
        # ---------------------------
        "uasg_1": r"UASG\s*[:\-–]?\s*(\d{6})",

        # ---------------------------
        # MODALIDADE
        # ---------------------------
        "modalidade_1": r"(PREG[AÃ]O|DISPENSA|INEXIGIBILIDADE|TOMADA\s+DE\s+PRE[ÇC]OS|CONCORR[EÊ]NCIA|CONVITE|LEIL[AÃ]O|REGISTRO\s+DE\s+PRE[ÇC]OS)",

        # ---------------------------
        # PRAZO DE ENTREGA
        # ---------------------------
        "prazo_entrega_1": r"(\d+)\s+dias\s+úteis",
        "prazo_entrega_2": r"Entrega\s+em\s+até\s+(\d+)\s+dias",

        # ---------------------------
        # LOCAL DE ENTREGA
        # ---------------------------
        "local_entrega_1": r"Local\s+de\s+Entrega\s*[:\-–]\s*([^\n]+)",

        # ---------------------------
        # VALIDADE PROPOSTA
        # ---------------------------
        "validade_proposta_1": r"Validade\s+da\s+proposta\s*[:\-–]?\s*(\d+)\s+dias",
        "validade_proposta_2": r"Proposta\s+v[aá]lida\s+por\s+(\d+)\s+dias",

        # ---------------------------
        # CATÁLOGO TÉCNICO
        # ---------------------------
        "catalogo_tecnico_1": r"(cat[aá]logo\s+t[eé]cnico)",
        "catalogo_tecnico_2": r"(necess[aá]rio\s+cat[aá]logo)",

        # ---------------------------
        # MODO DE DISPUTA
        # ---------------------------
        "modo_disputa_1": r"Modo\s+de\s+Disputa\s*[:\-–]?\s*(Aberto|Fechado|Aberto\s+e\s+Fechado)",
    }

    @classmethod
    def extract_field(cls, field_name, text):

        patterns = {
            "Orgão": ["orgao_1", "orgao_2", "orgao_3", "orgao_4"],
            "CNPJ Órgão": ["cnpj_1", "cnpj_2"],
            "Cidade e Estado": ["cidade_estado_1", "cidade_estado_2", "cidade_estado_3"],
            "Nº Pregão e Processo": ["processo_pregao_1", "pregao_1", "pregao_2", "processo_1", "processo_2"],
            "Telefones": ["telefone_1", "telefone_2"],
            "E-mail": ["email_1", "email_2"],
            "Prazo de pagamento": ["prazo_pagamento_1", "prazo_pagamento_2"],
            "Plataforma": ["plataforma_1", "plataforma_2"],
            "UASG": ["uasg_1"],
            "Modalidade de compra": ["modalidade_1"],
            "Prazo de entrega": ["prazo_entrega_1", "prazo_entrega_2"],
            "Local de entrega": ["local_entrega_1"],
            "Validade da proposta": ["validade_proposta_1", "validade_proposta_2"],
            "Catálogo técnico": ["catalogo_tecnico_1", "catalogo_tecnico_2"],
            "Modo de Disputa": ["modo_disputa_1"],
        }

        for pattern_name in patterns.get(field_name, []):
            regex = cls.COMMON_PATTERNS[pattern_name]
            match = re.search(regex, text, re.IGNORECASE | re.MULTILINE)

            if match:
                groups = match.groups()

                # ------- CASOS ESPECIAIS -------
                if field_name == "Nº Pregão e Processo":
                    if len(groups) >= 2:
                        return f"PROCESSO: {groups[0]} | PREGÃO: {groups[1]}"
                    return groups[0]

                if field_name == "Cidade e Estado":
                    return f"{groups[0]} - {groups[1]}"

                if field_name == "Telefones":
                    if len(groups) == 3:
                        return f"({groups[0]}) {groups[1]}-{groups[2]}"
                    return match.group(0)

                if field_name == "Catálogo técnico":
                    return "Exige catálogo técnico"

                return match.group(1) if len(groups) >= 1 else match.group(0)

        return "NÃO ENCONTRADO"
