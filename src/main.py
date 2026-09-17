import argparse
import re
import shutil
from pathlib import Path
from datetime import date

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

def normalizar_data(data: str) -> str:
    """
    Converte datas nos formatos:
    DD-MM-AA
    DD.MM.AA
    DD/MM/AA
    DDMMYYYY
    DD-MM-YYYY
    etc.

    Para o padrão final:
    DD.MM.AA
    """

    numeros = re.sub(r"\D", "", data)

    if len(numeros) == 8:
        # DDMMYYYY
        dia = int(numeros[:2])
        mes = int(numeros[2:4])
        ano = int(numeros[4:8])

    elif len(numeros) == 6:
        # DDMMYY
        dia = int(numeros[:2])
        mes = int(numeros[2:4])
        ano = 2000 + int(numeros[4:6])

    elif len(numeros) == 4:
        # DDMM
        dia = int(numeros[:2])
        mes = int(numeros[2:4])
        ano = None

    else:
        raise ValueError(f"Data inválida: {data}")

    return dia, mes, ano

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
    """
    Procura dois valores de data separados por 'a' ou 'A'.

    Exemplos:
        10.09 A 16.10.26
        31-08-26 a 14-09-26
        24082026 a 28082026
        20.12 a 10.01.26
    """

    data = (
        r"(?:"
        r"\d{2}[./-]\d{2}[./-]\d{2,4}"
        r"|\d{8}"
        r"|\d{6}"
        r"|\d{2}[./-]\d{2}"
        r")"
    )

    padrao = (
        f"({data})"
        r"\s+[aA]\s+"
        f"({data})"
    )

    resultado = re.search(padrao, texto)

    if not resultado:
        return None, None

    inicio = normalizar_data(resultado.group(1))
    fim = normalizar_data(resultado.group(2))

    return inicio, fim


def normalizar_nome(nome: str) -> str:
    """
    Normaliza o nome da pessoa.
    """

    nome = re.sub(r"\s+", " ", nome).strip()

    return nome.upper()


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

    # Extrai o período
    inicio, fim = extrair_periodo(texto)

    if not inicio or not fim:
        print(f"[AVISO] Não foi possível identificar o período: {caminho.name}")
        return None

    # Remove o período do texto
    texto_sem_periodo = re.sub(
        r"("
        r"\d{2}[./-]\d{2}[./-]\d{2,4}"
        r"|\d{8}"
        r"|\d{6}"
        r"|\d{2}[./-]\d{2}"
        r")"
        r"\s+[aA]\s+"
        r"("
        r"\d{2}[./-]\d{2}[./-]\d{2,4}"
        r"|\d{8}"
        r"|\d{6}"
        r"|\d{2}[./-]\d{2}"
        r")",
        "",
        texto,
        count=1
    )

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

    # O último campo é considerado o setor
    setor = partes[-1]

    # Tudo antes do setor é considerado nome
    nome = " ".join(partes[:-1])

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