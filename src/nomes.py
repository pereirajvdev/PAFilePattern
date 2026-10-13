import re

def normalizar_nome(nome: str) -> str:
    """
    Normaliza o nome da pessoa, mantendo 'de', 'da' e 'do'
    com a primeira letra minúscula.
    """
    nome = re.sub(r"\s+", " ", nome).strip()
    nome = nome.title()

    nome = re.sub(r"\b(De|Da|Do)\b", lambda m: m.group(1).lower(), nome)

    return nome