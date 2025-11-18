import re

# -----------------------------
# 1. Normalização do texto
# -----------------------------
def normalize_text(text):
    # Remove quebras quebradas
    text = text.replace("\n", " ")
    # Remove múltiplos espaços
    text = re.sub(r"\s+", " ", text)
    # Separa letras coladas em números (problema comum de PDF)
    text = re.sub(r"([A-Za-z])(\d)", r"\1 \2", text)
    # Separa números colados em letras
    text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)
    # Normaliza hífens
    text = re.sub(r"[–—]", "-", text)

    return text.strip()

# -----------------------------
# 2. Função auxiliar para extrair com fallback
# -----------------------------
def extract_first(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

# -----------------------------
# 3. Função principal de extração
# -----------------------------
def extract_editais(text):
    text = normalize_text(text)

    data = {
        "modalidade": extract_first(text, [
            r"(PREGÃO ELETRÔNICO)",
            r"(PREGÃO)",
        ]),

        "pregao_numero": extract_first(text, [
            r"PREGÃO ELETRÔNICO\s*(\d{5}\/\d{4})",
            r"PREGÃO\s*(\d{5}\/\d{4})",
        ]),

        "uasg": extract_first(text, [
            r"UASG\s*\(?.*?\)?\s*(\d{6})",
            r"CONTRATANTE\s*\(UASG\)\s*(\d{6})",
        ]),

        "objeto": extract_first(text, [
            r"OBJETO\s*(.*?)(?=\s*VALOR TOTAL|VALOR\s*TOTAL)",
        ]),

        "valor_total": extract_first(text, [
            r"VALOR TOTAL.*?R\$\s*([\d\.\,]+)",
            r"R\$\s*([\d\.\,]+)",
        ]),

        "data_sessao": extract_first(text, [
            r"Dia\s*(\d{2}\/\d{2}\/\d{4})",
        ]),

        "hora_sessao": extract_first(text, [
            r"às\s*(\d{2}:\d{2})",
        ]),

        "modo_disputa": extract_first(text, [
            r"MODO DE DISPUTA:\s*([a-zA-Z ]+)",
        ]),

        "criterio_julgamento": extract_first(text, [
            r"CRITÉRIO DE JULGAMENTO:\s*([a-zA-Z ]+)",
        ]),
    }

    return data


# -----------------------------
# 4. Exemplo de uso
# -----------------------------
if __name__ == "__main__":
    texto = """ PREGÃO ELETRÔNICO90015/2025 CONTRATANTE (UASG) 154046 OBJETO Aquisição de equipamentos para estruturação dos laboratórios do Instituto de Ciências Humanas e Sociais, conforme condições e exigências estabelecidas neste instrumento. VALOR TOTAL DA CONTRATAÇÃO R$ R$ 416.797,55 (Quatrocentos e dezesseis mil, setecentos e noventa e sete reais, cinquenta e cinco centavos) DATA DA SESSÃO PÚBLICA Dia 19/11/2025 às 09:30 horas (horário de Brasília) CRITÉRIO DE JULGAMENTO: menor preço por item MODO DE DISPUTA: aberto """

    resultado = extract_editais(texto)
    print(resultado)
