
import shutil

from pathlib import Path
from tqdm import tqdm

from logger import log_ok, log_warning
from normalizador import normalizar_arquivo
from cache import carregar_cache, salvar_cache, identificador_arquivo
from arquivos import obter_destino_disponivel


def processar_pasta(
    pasta_entrada: Path,
    pasta_saida: Path | None,
    pasta_ignorados: Path,
    pasta_nao_processar: Path | None = None
):
    """Processa PDFs, separando ignorados e arquivos duplicados."""

    pasta_entrada = pasta_entrada.resolve()
    pasta_ignorados.mkdir(parents=True, exist_ok=True)

    if pasta_saida:
        pasta_saida.mkdir(parents=True, exist_ok=True)
        pasta_saida = pasta_saida.resolve()

    if pasta_nao_processar:
        pasta_nao_processar = pasta_nao_processar.resolve()

    pasta_base = pasta_saida if pasta_saida else pasta_entrada
    pasta_copias = pasta_base / "copias"
    pasta_copias_diferentes = pasta_base / "copias diferentes"

    cache_ignorados = carregar_cache()

    pastas_excluidas = [
        pasta.resolve()
        for pasta in [
            pasta_ignorados,
            pasta_base / "copias",
            pasta_base / "copias diferentes",
            *([pasta_nao_processar] if pasta_nao_processar else []),
        ]
    ]

    arquivos = [
        arquivo
        for arquivo in pasta_entrada.rglob("*.pdf")
        if not any(
            excluida == pai.resolve()
            for excluida in pastas_excluidas
            for pai in arquivo.parents
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
            identificador = identificador_arquivo(
                arquivo, pasta_entrada
            )

            # Arquivos já registrados não são processados novamente.
            if identificador in cache_ignorados:
                log_warning(
                    f"Ignorado pelo cache, sem mover: {arquivo.name}"
                )
                ignorados += 1
                continue

            novo_nome = normalizar_arquivo(arquivo)

            if novo_nome is None:
                destino_ignorado = obter_destino_disponivel(
                    pasta_ignorados / arquivo.name
                )

                if pasta_saida:
                    shutil.copy2(arquivo, destino_ignorado)
                    log_warning(
                        f"Arquivo ignorado e copiado: "
                        f"{arquivo.name} -> {destino_ignorado}"
                    )
                else:
                    shutil.move(str(arquivo), str(destino_ignorado))
                    log_warning(
                        f"Arquivo ignorado e movido: {arquivo.name}"
                    )

                cache_ignorados.add(identificador)
                ignorados += 1
                continue

            destino = (
                pasta_saida / novo_nome
                if pasta_saida
                else arquivo.parent / novo_nome
            )

            if not pasta_saida and arquivo.resolve() == destino.resolve():
                processados += 1
                continue

            if destino.exists():
                mesma_tamanho = (
                    arquivo.stat().st_size == destino.stat().st_size
                )

                pasta_destino = (
                    pasta_copias
                    if mesma_tamanho
                    else pasta_copias_diferentes
                )

                pasta_destino.mkdir(parents=True, exist_ok=True)

                destino_copia = obter_destino_disponivel(
                    pasta_destino / novo_nome
                )

                if pasta_saida:
                    shutil.copy2(arquivo, destino_copia)
                    descricao = (
                        "Cópia criada"
                        if mesma_tamanho
                        else "Cópia diferente criada"
                    )
                else:
                    shutil.move(str(arquivo), str(destino_copia))
                    descricao = (
                        "Cópia movida"
                        if mesma_tamanho
                        else "Cópia diferente movida"
                    )

                log_warning(
                    f"{descricao}: {arquivo.name} -> {destino_copia}"
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
            log_warning(f"Erro ao processar {arquivo.name}: {erro}")

    salvar_cache(cache_ignorados)

    print()
    print("─" * 50)
    print("Processamento concluído")
    print("─" * 50)
    print(f"✓ Processados: {processados}")
    print(f"! Ignorados:   {ignorados}")
    descricao_copias = "Cópias criadas" if pasta_saida else "Cópias movidas"
    print(f"↪ {descricao_copias}: {copias}")
    print("─" * 50)
