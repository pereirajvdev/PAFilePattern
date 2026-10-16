import argparse
from pathlib import Path

from processamento import processar_pasta


def main():
    parser = argparse.ArgumentParser(
        description="Normaliza nomes de arquivos PDF."
    )

    parser.add_argument(
        "entrada",
        help="Pasta contendo os arquivos PDF.",
    )

    parser.add_argument(
        "--out",
        help="Pasta de destino dos arquivos normalizados.",
    )

    parser.add_argument(
        "--ignorar",
        dest="ignorar",
        help="Pasta onde os arquivos ignorados serão salvos."
    )
    parser.add_argument(
        "--notthis",
        help="Pasta que não deve ser processada.",
    )

    args = parser.parse_args()

    pasta_entrada = Path(args.entrada)
    pasta_saida = Path(args.out) if args.out else None

    pasta_ignorados = (
        Path(args.ignorar)
        if args.ignorar
        else (pasta_saida or pasta_entrada) / "Ignorados"
    )

    pasta_nao_processar = (
        Path(args.notthis)
        if args.notthis
        else None
    )

    if not pasta_entrada.exists():
        print(
            f"[ERRO] Pasta de entrada não encontrada: {pasta_entrada}"
        )
        return

    if not pasta_entrada.is_dir():
        print(f"[ERRO] A entrada não é uma pasta: {pasta_entrada}")
        return

    processar_pasta(
        pasta_entrada,
        pasta_saida,
        pasta_ignorados,
        pasta_nao_processar,
    )


if __name__ == "__main__":
    main()