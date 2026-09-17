SETORES = {
    "SEMS",
    "SEDUC",
    "SEMOSP",
    "SEFIN",
    "SARH",
    "SECOM",
    "SEDEC",
    "SEMAP",
    "SEMOB",
    "SESP",
    "SEMCI",
    "SEDESO",
    "SEGOV",
    "PGM",
    "SEMMADA",
    "SEPLAN",
    "SESMT",
    "SELTC",
}

def identificar_setor(partes: list[str]):
    """
    Identifica o setor utilizando a lista de setores conhecidos.

    O setor pode estar:
    - separado por " - "
    - grudado ao final do nome
    """

    # Procura primeiro um campo que seja exatamente um setor
    for i in range(len(partes) - 1, -1, -1):
        parte = partes[i].upper().strip()

        if parte in SETORES:
            nome = " ".join(partes[:i])

            if not nome:
                return None

            return nome, parte

    # Caso o setor esteja grudado ao final do nome
    texto = " ".join(partes).strip()
    texto_upper = texto.upper()

    # Setores maiores primeiro
    setores_ordenados = sorted(
        SETORES,
        key=len,
        reverse=True
    )

    for setor in setores_ordenados:
        if texto_upper.endswith(setor):
            nome = texto[:-len(setor)].strip()

            if nome:
                return nome, setor

    return None