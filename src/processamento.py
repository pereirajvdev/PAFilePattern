import shutil
from pathlib import Path
from tqdm import tqdm

from logger import log_ok, log_warning
from normalizador import normalizar_arquivo

def obter_destino_disponivel(destino: Path) -> Path:
    """
    Retorna um caminho disponível.
    Se o arquivo já existir, adiciona (2), (3), etc.
    """

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

def processar_pasta(
    pasta_entrada: Path,
    pasta_saida: Path | None,
    pasta_ignorados: Path
):
    """
    Processa todos os PDFs da pasta de entrada.
    """

    if pasta_saida:
        pasta_saida.mkdir(parents=True, exist_ok=True)

    pasta_ignorados.mkdir(parents=True, exist_ok=True)

    arquivos = [
        arquivo
        for arquivo in pasta_entrada.rglob("*.pdf")
        if pasta_ignorados not in arquivo.parents
    ]

    if not arquivos:
        print("[INFO] Nenhum arquivo PDF encontrado.")
        return

    print(f"[INFO] Encontrados {len(arquivos)} arquivos.\n")

    processados = 0
    ignorados = 0

    for arquivo in tqdm(
        arquivos,
        desc="Processando",
        unit="arquivo",
        dynamic_ncols=True
    ):

        novo_nome = normalizar_arquivo(arquivo)

        if novo_nome is None:
            destino_ignorado = pasta_ignorados / arquivo.name

            shutil.copy2(
                arquivo,
                destino_ignorado
            )

            log_warning(
                f"Arquivo ignorado: {arquivo.name}"
            )

            ignorados += 1
            continue

        if pasta_saida:
            # Modo com --out
            destino = pasta_saida / novo_nome
            destino = obter_destino_disponivel(destino)

            shutil.copy2(arquivo, destino)

        else:
            # Modo sem --out
            destino = arquivo.parent / novo_nome
            destino = obter_destino_disponivel(destino)

            arquivo.rename(destino)

        log_ok(
            f"Arquivo processado: {arquivo.name} -> {novo_nome}"
        )

        processados += 1

    print()
    print("─" * 50)
    print("Processamento concluído")
    print("─" * 50)
    print(f"✓ Processados: {processados}")
    print(f"! Ignorados:   {ignorados}")
    print("─" * 50)

