
import shutil
from pathlib import Path


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


def mover_para_copias(
    arquivo: Path,
    pasta_copias: Path
) -> Path:
    """Move um arquivo para a pasta de cópias sem sobrescrever."""
    pasta_copias.mkdir(parents=True, exist_ok=True)

    destino = obter_destino_disponivel(
        pasta_copias / arquivo.name
    )

    shutil.move(str(arquivo), str(destino))

    return destino
