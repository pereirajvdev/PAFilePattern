from datetime import datetime
from pathlib import Path
from tqdm import tqdm


PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "logs"


def create_log_file() -> Path:
    """Cria um novo arquivo de log para a execução atual."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = LOG_DIR / f"normalizer_{timestamp}.log"

    log_file.touch()

    return log_file


LOG_FILE = create_log_file()


def write_log(level: str, message: str) -> None:
    """Escreve uma mensagem no arquivo de log."""

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{level}] {message}\n")


def log_ok(message: str) -> None:
    write_log("OK", message)


def log_error(message: str) -> None:
    tqdm.write(f"[ERRO] {message}")
    write_log("ERRO", message)


def log_warning(message: str) -> None:
    tqdm.write(f"[AVISO] {message}"+"\n")
    write_log("AVISO", message)