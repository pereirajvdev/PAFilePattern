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


def mover_para_copias(arquivo: Path, pasta_copias: Path) -> Path:
    """
    Move o arquivo duplicado para a pasta copias,
    evitando sobrescrever arquivos existentes.
    """
    pasta_copias.mkdir(parents=True, exist_ok=True)

    destino = obter_destino_disponivel(pasta_copias / arquivo.name)

    shutil.move(str(arquivo), str(destino))

    return destino


def processar_pasta(
    pasta_entrada: Path,
    pasta_saida: Path | None,
    pasta_ignorados: Path,
    pasta_nao_processar: Path | None = None
):
    """
    Processa PDFs, separando arquivos ignorados e cópias
    que possuem o mesmo nome de destino e tamanho em bytes.
    """

    if pasta_saida:
        pasta_saida.mkdir(parents=True, exist_ok=True)

    pasta_ignorados.mkdir(parents=True, exist_ok=True)

    # A pasta copias fica na saída, se houver --out;
    # caso contrário, fica na pasta de entrada.
    pasta_base = pasta_saida if pasta_saida else pasta_entrada
    pasta_copias = pasta_base / "copias"

    arquivos = [
        arquivo
        for arquivo in pasta_entrada.rglob("*.pdf")
        if pasta_ignorados not in arquivo.parents
        and pasta_copias not in arquivo.parents
        and (
            pasta_nao_processar is None
            or pasta_nao_processar not in arquivo.parents
        )
    ]

    if not arquivos:
        print("[INFO] Nenhum arquivo PDF encontrado.")
        return

    print(f"[INFO] Encontrados {len(arquivos)} arquivos.\n")

    processados = 0
    ignorados = 0
    copias = 0

    for arquivo in tqdm(
        arquivos,
        desc="Processando",
        unit="arquivo",
        dynamic_ncols=True
    ):
        try:
            novo_nome = normalizar_arquivo(arquivo)

            if novo_nome is None:
                destino_ignorado = obter_destino_disponivel(
                    pasta_ignorados / arquivo.name
                )

                shutil.move(str(arquivo), str(destino_ignorado))

                log_warning(
                    f"Arquivo ignorado e movido: {arquivo.name}"
                )

                ignorados += 1
                continue

            if pasta_saida:
                destino = pasta_saida / novo_nome
            else:
                destino = arquivo.parent / novo_nome

            # O arquivo já está com o nome correto.
            if arquivo.resolve() == destino.resolve():
                processados += 1
                continue

            
            # Já existe um arquivo com o nome desejado.
            if destino.exists():

                if arquivo.stat().st_size == destino.stat().st_size:
                    # Mesmo nome e mesmo tamanho
                    destino_copia = mover_para_copias(
                        arquivo,
                        pasta_base / "copias"
                    )

                    log_warning(
                        f"Cópia movida: {arquivo.name} -> "
                        f"{destino_copia}"
                    )

                    copias += 1
                    continue

                else:
                    # Mesmo nome, mas tamanho diferente
                    destino_copia = mover_para_copias(
                        arquivo,
                        pasta_base / "copias diferentes"
                    )

                    log_warning(
                        f"Cópia diferente movida: {arquivo.name} -> "
                        f"{destino_copia}"
                    )

                    copias += 1
                    continue


            if pasta_saida:
                shutil.copy2(arquivo, destino)
            else:
                arquivo.rename(destino)

            log_ok(
                f"Arquivo processado: {arquivo.name} -> {destino.name}"
            )

            processados += 1

        except Exception as erro:
            log_warning(
                f"Erro ao processar {arquivo.name}: {erro}"
            )

    print()
    print("─" * 50)
    print("Processamento concluído")
    print("─" * 50)
    print(f"✓ Processados: {processados}")
    print(f"! Ignorados:   {ignorados}")
    print(f"↪ Cópias movidas: {copias}")
    print("─" * 50)
