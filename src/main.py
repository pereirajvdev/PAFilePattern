import argparse
import re
import shutil
from pathlib import Path
from datetime import date

SETORES = {
    "SEMS",
    "SEDUC",
    "SEMOSP",
    "SEFIN",
    "SARH",
    "SECOM",
    "SEDEC",
    "SEMAP",
    "SEMOB",
    "SESP",
    "SEMCI",
    "SEDESO",
    "SEGOV",
    "PGM",
    "SEMMADA",
    "SEPLAN",
    "SESMT",
    "SELTC",
}

def completar_periodo(inicio, fim):
    """
    Completa os anos ausentes e garante que o período
    tenha data inicial <= data final.
    """

    dia_inicio, mes_inicio, ano_inicio = inicio
    dia_fim, mes_fim, ano_fim = fim

    # Se nenhum ano foi informado, usamos o ano atual.
    if ano_inicio is None and ano_fim is None:
        ano_fim = date.today().year
        ano_inicio = ano_fim

    # Se apenas o início possui ano
    elif ano_inicio is not None and ano_fim is None:
        ano_fim = ano_inicio

    # Se apenas o fim possui ano
    elif ano_inicio is None and ano_fim is not None:
        ano_inicio = ano_fim

    inicio = date(ano_inicio, mes_inicio, dia_inicio)
    fim = date(ano_fim, mes_fim, dia_fim)

    # Se o início ficou depois do fim,
    # assumimos que o período atravessou o ano.
    if inicio > fim:
        ano_inicio -= 1
        inicio = date(ano_inicio, mes_inicio, dia_inicio)

    return inicio, fim

def normalizar_data(data: str) -> tuple[int, int, int | None]:
    partes = re.split(r"[./-]", data)

    if len(partes) == 3:
        dia = int(partes[0])
        mes = int(partes[1])
        ano = int(partes[2])

        if ano < 100:
            ano += 2000

        return dia, mes, ano

    if len(partes) == 2:
        dia = int(partes[0])
        mes = int(partes[1])
        return dia, mes, None

    numeros = re.sub(r"\D", "", data)

    if len(numeros) == 8:
        return (
            int(numeros[:2]),
            int(numeros[2:4]),
            int(numeros[4:8])
        )

    if len(numeros) == 6:
        return (
            int(numeros[:2]),
            int(numeros[2:4]),
            2000 + int(numeros[4:6])
        )

    if len(numeros) == 4:
        return (
            int(numeros[:2]),
            int(numeros[2:4]),
            None
        )

    raise ValueError(f"Data inválida: {data}")

def formatar_periodo(inicio, fim):
    return (
        f"{inicio.day:02d}.{inicio.month:02d}.{inicio.year:04d} "
        f"A "
        f"{fim.day:02d}.{fim.month:02d}.{fim.year:04d}"
    )

def extrair_data(texto: str) -> str | None:
    """
    Procura datas em formatos comuns dentro do texto.
    """

    padroes = [
        r"\b\d{2}[./-]\d{2}[./-]\d{2,4}\b",
        r"\b\d{8}\b",
        r"\b\d{6}\b",
    ]

    for padrao in padroes:
        resultado = re.search(padrao, texto)

        if resultado:
            return resultado.group()

    return None


def extrair_periodo(texto: str):
    data = (
        r"(?:"
        r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
        r"|\d{8}"
        r"|\d{6}"
        r"|\d{1,2}[./-]\d{1,2}"
        r")"
    )

    padrao = (
        f"({data})"
        r"\s+(?:[aA]|-)\s+"
        f"({data})"
    )

    resultado = re.search(padrao, texto)

    if not resultado:
        return None

    inicio = normalizar_data(resultado.group(1))
    fim = normalizar_data(resultado.group(2))

    return inicio, fim, resultado.start(), resultado.end()


def normalizar_nome(nome: str) -> str:
    """
    Normaliza o nome da pessoa.
    """

    nome = re.sub(r"\s+", " ", nome).strip()

    return nome.upper()

def identificar_setor(partes: list[str]):
    """
    Identifica o setor utilizando a lista de setores conhecidos.

    O setor pode estar:
    - separado por " - "
    - grudado ao final do nome
    """

    # Primeiro procura um campo que seja exatamente um setor
    for i in range(len(partes) - 1, -1, -1):
        parte = partes[i].upper().strip()

        if parte in SETORES:
            nome = " ".join(partes[:i])

            if not nome:
                return None

            return nome, parte

    # Caso o setor esteja grudado ao final do nome,
    # procura um setor conhecido no final do texto.
    texto = " ".join(partes).strip()
    texto_upper = texto.upper()

    setores_ordenados = sorted(
        SETORES,
        key=len,
        reverse=True
    )

    for setor in setores_ordenados:
        if texto_upper.endswith(setor):
            nome = texto[:-len(setor)].strip()

            if nome:
                return nome, setor

    return None

def normalizar_arquivo(caminho: Path) -> str | None:
    """
    Recebe o caminho de um PDF e tenta gerar o novo nome.
    """

    nome_original = caminho.stem

    # Remove o prefixo PA
    texto = re.sub(
        r"^\s*PA\s*[-–—]?\s*",
        "",
        nome_original,
        flags=re.IGNORECASE
    )

    # converte espaços multiplicados em único
    texto = re.sub(r"\s+", " ", texto).strip()
    
    resultado_periodo = extrair_periodo(texto)

    if resultado_periodo is None:
        print(f"[AVISO] Não foi possível identificar o período: {caminho.name}")
        return None

    inicio, fim, inicio_pos, fim_pos = resultado_periodo

    # Remove exatamente o período encontrado
    texto_sem_periodo = texto[:inicio_pos] + texto[fim_pos:]

    # Limpa separadores duplicados
    texto_sem_periodo = re.sub(
        r"\s*[-–—]\s*",
        " - ",
        texto_sem_periodo
    )

    partes = [
        parte.strip()
        for parte in texto_sem_periodo.split(" - ")
        if parte.strip()
    ]

    if len(partes) < 2:
        print(f"[AVISO] Não foi possível identificar nome/setor: {caminho.name}")
        return None

    resultado_nome_setor = identificar_setor(partes)

    if resultado_nome_setor is None:
        print(f"[AVISO] Não foi possível identificar nome/setor: {caminho.name}")
        return None

    nome, setor = resultado_nome_setor

    nome = normalizar_nome(nome)
    setor = setor.upper().strip()
    
    inicio, fim = completar_periodo(inicio, fim)

    periodo = formatar_periodo(inicio, fim)

    return f"PA - {nome} - {setor} - {periodo}.pdf"


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


def main():
    parser = argparse.ArgumentParser(
        description="Normaliza nomes de arquivos PDF."
    )

    parser.add_argument(
        "entrada",
        help="Pasta contendo os arquivos PDF."
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Pasta onde os arquivos normalizados serão salvos."
    )

    parser.add_argument(
        "--ignored",
        required=True,
        help="Pasta onde os arquivos que não puderam ser processados serão salvos."
    )

    args = parser.parse_args()

    pasta_entrada = Path(args.entrada)
    pasta_saida = Path(args.out)
    pasta_ignorados = Path(args.ignored)

    if not pasta_entrada.exists():
        print(f"[ERRO] Pasta de entrada não encontrada: {pasta_entrada}")
        return

    if not pasta_entrada.is_dir():
        print(f"[ERRO] A entrada não é uma pasta: {pasta_entrada}")
        return

    processar_pasta(pasta_entrada, pasta_saida, pasta_ignorados)


if __name__ == "__main__":
    main()