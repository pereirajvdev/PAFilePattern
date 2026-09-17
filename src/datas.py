import re
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

    # Primeiro tenta encontrar um período com duas datas
    padrao_periodo = (
        f"({data})"
        r"\s+(?:[aA]|-)\s+"
        f"({data})"
    )

    resultado = re.search(padrao_periodo, texto)

    if resultado:
        inicio = normalizar_data(resultado.group(1))
        fim = normalizar_data(resultado.group(2))

        return inicio, fim, resultado.start(), resultado.end()

    # Se não encontrou período, procura uma única data
    resultado = re.search(data, texto)

    if resultado:
        data_unica = normalizar_data(resultado.group())

        return (
            data_unica,
            data_unica,
            resultado.start(),
            resultado.end()
        )

    return None