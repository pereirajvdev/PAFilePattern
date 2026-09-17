import shutil
from pathlib import Path

from normalizador import normalizar_arquivo

def processar_pasta(pasta_entrada: Path, pasta_saida: Path, pasta_ignorados: Path):
    """
    Processa todos os PDFs da pasta de entrada.
    """

    pasta_saida.mkdir(parents=True, exist_ok=True)
    pasta_ignorados.mkdir(parents=True, exist_ok=True)

    arquivos = list(pasta_entrada.glob("*.pdf"))

    if not arquivos:
        print("[INFO] Nenhum arquivo PDF encontrado.")
        return

    print(f"[INFO] Encontrados {len(arquivos)} arquivos.\n")

    processados = 0
    ignorados = 0

    for arquivo in arquivos:

        novo_nome = normalizar_arquivo(arquivo)

        if novo_nome is None:
            destino_ignorado = pasta_ignorados / arquivo.name

            shutil.copy2(
                arquivo,
                destino_ignorado
            )

            print(f"[IGNORADO] {arquivo.name}\n")

            ignorados += 1
            continue

        destino = pasta_saida / novo_nome

        shutil.copy2(arquivo, destino)

        print(f"[OK] {arquivo.name}")
        print(f"     -> {novo_nome}\n")

        processados += 1

    print("================================")
    print("Processamento concluído.")
    print(f"Processados: {processados}")
    print(f"Ignorados:   {ignorados}")
    print(f"Saída:       {pasta_saida}")
    print(f"Ignorados:   {pasta_ignorados}")
    print("================================")

