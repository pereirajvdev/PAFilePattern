import re

def normalizar_nome(nome: str) -> str:
    """
    Normaliza o nome da pessoa.
    """

    nome = re.sub(r"\s+", " ", nome).strip()

    return nome.upper()