from pathlib import Path
from tqdm import tqdm

from logger import log_ok, log_warning
from normalizador import normalizar_arquivo
from cache import carregar_cache, salvar_cache, identificador_arquivo
from arquivos import (
    enviar_para_ignorados,
    enviar_para_copiados,
    listar_pdfs,
)


def processar_pasta(
    pasta_entrada: Path,
    pasta_saida: Path | None,
    pasta_ignorados: Path,
    pasta_nao_processar: Path | None = None,
):
    """Processa PDFs, separando ignorados e arquivos duplicados."""

    pasta_entrada = pasta_entrada.resolve()
    copiar = pasta_saida is not None

    if pasta_saida:
        pasta_saida.mkdir(parents=True, exist_ok=True)
        pasta_saida = pasta_saida.resolve()

    pasta_ignorados.mkdir(parents=True, exist_ok=True)
    pasta_ignorados = pasta_ignorados.resolve()

    if pasta_nao_processar:
        pasta_nao_processar = pasta_nao_processar.resolve()

    pasta_base = pasta_saida if copiar else pasta_entrada

    pasta_copiados = pasta_base / "copiados"
    pasta_copiados_diferentes = pasta_base / "copiados diferente"

    pastas_excluidas = [
        pasta_ignorados,
        pasta_copiados,
        pasta_copiados_diferentes,
    ]

    if pasta_saida:
        pastas_excluidas.append(pasta_saida)

    if pasta_nao_processar:
        pastas_excluidas.append(pasta_nao_processar)

    arquivos = listar_pdfs(
        pasta_entrada,
        pastas_excluidas,
    )

    if not arquivos:
        print("[INFO] Nenhum arquivo PDF encontrado.")
        return

    print(f"[INFO] Encontrados {len(arquivos)} arquivos.\n")

    cache_ignorados = carregar_cache()

    processados = 0
    ignorados = 0
    copias = 0

    for arquivo in tqdm(
        arquivos,
        desc="Processando",
        unit="arquivo",
        dynamic_ncols=True,
    ):
        try:
            identificador = identificador_arquivo(
                arquivo,
                pasta_entrada,
            )

            if identificador in cache_ignorados:
                log_warning(
                    f"Ignorado pelo cache, sem mover: {arquivo.name}"
                )
                ignorados += 1
                continue

            novo_nome = normalizar_arquivo(arquivo)

            if novo_nome is None:
                destino = enviar_para_ignorados(
                    arquivo,
                    pasta_ignorados,
                    copiar,
                )

                cache_ignorados.add(identificador)

                acao = "copiado" if copiar else "movido"

                log_warning(
                    f"Arquivo ignorado e {acao}: "
                    f"{arquivo.name} -> {destino}"
                )

                ignorados += 1
                continue

            destino = (
                pasta_saida / novo_nome
                if copiar
                else arquivo.parent / novo_nome
            )

            if not copiar and arquivo.resolve() == destino.resolve():
                processados += 1
                continue

            if destino.exists():
                mesma_tamanho = (
                    arquivo.stat().st_size == destino.stat().st_size
                )

                pasta_destino = (
                    pasta_copiados
                    if mesma_tamanho
                    else pasta_copiados_diferentes
                )

                destino_copia = enviar_para_copiados(
                    arquivo,
                    pasta_destino,
                    copiar,
                    novo_nome,
                )

                descricao = (
                    "Cópia criada"
                    if copiar and mesma_tamanho
                    else "Cópia diferente criada"
                    if copiar
                    else "Cópia movida"
                    if mesma_tamanho
                    else "Cópia diferente movida"
                )

                log_warning(
                    f"{descricao}: {arquivo.name} -> {destino_copia}"
                )

                copias += 1
                continue

            from arquivos import copiar_ou_mover

            copiar_ou_mover(
                arquivo,
                destino,
                copiar,
            )

            log_ok(
                f"Arquivo processado: "
                f"{arquivo.name} -> {destino.name}"
            )

            processados += 1

        except Exception as erro:
            log_warning(
                f"Erro ao processar {arquivo.name}: {erro}"
            )

    salvar_cache(cache_ignorados)

    print()
    print("─" * 50)
    print("Processamento concluído")
    print("─" * 50)
    print(f"✓ Processados: {processados}")
    print(f"! Ignorados:   {ignorados}")
    print(
        f"↪ {'Cópias criadas' if copiar else 'Cópias movidas'}: "
        f"{copias}"
    )
    print("─" * 50)