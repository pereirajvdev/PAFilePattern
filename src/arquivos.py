import shutil

from pathlib import Path


PASTAS_EXCLUIDAS = {
    "copiados",
    "copiados diferente",
    "ignorados",
}


def obter_destino_disponivel(destino: Path) -> Path:
    """Adiciona (2), (3), etc., se o destino já existir."""
    if not destino.exists():
        return destino

    contador = 2

    while True:
        novo_destino = (
            destino.parent
            / f"{destino.stem} ({contador}){destino.suffix}"
        )

        if not novo_destino.exists():
            return novo_destino

        contador += 1


def copiar_ou_mover(
    arquivo: Path,
    destino: Path,
    copiar: bool,
) -> Path:
    """Copia ou move um arquivo sem sobrescrever outro."""
    destino.parent.mkdir(parents=True, exist_ok=True)

    destino = obter_destino_disponivel(destino)

    if copiar:
        shutil.copy2(arquivo, destino)
    else:
        shutil.move(str(arquivo), str(destino))

    return destino


def enviar_para_ignorados(
    arquivo: Path,
    pasta_ignorados: Path,
    copiar: bool,
) -> Path:
    """Envia um arquivo para a pasta de ignorados."""
    return copiar_ou_mover(
        arquivo,
        pasta_ignorados / arquivo.name,
        copiar,
    )


def enviar_para_copiados(
    arquivo: Path,
    pasta_destino: Path,
    copiar: bool,
    nome: str | None = None,
) -> Path:
    """Envia um arquivo para a pasta de cópias correspondente."""
    return copiar_ou_mover(
        arquivo,
        pasta_destino / (nome or arquivo.name),
        copiar,
    )


def listar_pdfs(
    pasta_entrada: Path,
    pastas_excluidas: list[Path],
) -> list[Path]:
    """Lista PDFs sem percorrer pastas excluídas."""
    arquivos = []
    pastas_excluidas_resolvidas = {
        pasta.resolve()
        for pasta in pastas_excluidas
    }

    for pasta_atual, subpastas, nomes_arquivos in __import__("os").walk(
        pasta_entrada
    ):
        pasta_atual = Path(pasta_atual).resolve()

        subpastas[:] = [
            nome
            for nome in subpastas
            if (
                nome.casefold() not in PASTAS_EXCLUIDAS
                and (pasta_atual / nome).resolve()
                not in pastas_excluidas_resolvidas
            )
        ]

        for nome in nomes_arquivos:
            if nome.lower().endswith(".pdf"):
                arquivos.append(pasta_atual / nome)

    return arquivos