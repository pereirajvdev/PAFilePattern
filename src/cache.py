
import json
from pathlib import Path


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_CACHE = PASTA_PROJETO / ".cache_ignorados.json"


def carregar_cache(caminho: Path = ARQUIVO_CACHE) -> set[str]:
    """Carrega os identificadores dos arquivos ignorados."""
    if not caminho.exists():
        return set()

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list):
            return set()

        return {item for item in dados if isinstance(item, str)}

    except (json.JSONDecodeError, OSError):
        return set()


def salvar_cache(
    cache: set[str],
    caminho: Path = ARQUIVO_CACHE
) -> None:
    """Salva os identificadores dos arquivos ignorados."""
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(
            sorted(cache),
            arquivo,
            ensure_ascii=False,
            indent=2
        )


def identificador_arquivo(
    arquivo: Path,
    pasta_entrada: Path
) -> str:
    """Identifica o arquivo pelo caminho, tamanho e modificação."""
    caminho_relativo = arquivo.relative_to(pasta_entrada).as_posix()
    stat = arquivo.stat()

    return f"{caminho_relativo}|{stat.st_size}|{stat.st_mtime_ns}"
