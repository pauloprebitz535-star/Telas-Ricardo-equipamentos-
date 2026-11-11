"""Validações usadas pelo servidor (o servidor nunca confia só no que o navegador validou)."""


def so_digitos(texto: str) -> str:
    return "".join(c for c in texto if c.isascii() and c.isdigit())


def cpf_valido(cpf: str) -> bool:
    """Confere os 2 dígitos verificadores do CPF."""
    if len(cpf) != 11 or not (cpf.isascii() and cpf.isdigit()) or len(set(cpf)) == 1:
        return False
    for t in (9, 10):
        soma = sum(int(cpf[i]) * (t + 1 - i) for i in range(t))
        dv = (soma * 10) % 11
        if dv == 10:
            dv = 0
        if dv != int(cpf[t]):
            return False
    return True


def cnpj_valido(cnpj: str) -> bool:
    """Confere os 2 dígitos verificadores do CNPJ."""
    if len(cnpj) != 14 or not (cnpj.isascii() and cnpj.isdigit()) or len(set(cnpj)) == 1:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    for t, pesos in ((12, pesos1), (13, pesos2)):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(t))
        resto = soma % 11
        dv = 0 if resto < 2 else 11 - resto
        if dv != int(cnpj[t]):
            return False
    return True


def validar_nome(valor: str, rotulo: str, minimo: int, maximo: int, so_letras: bool = False) -> str:
    """Limpa e valida um nome. O @ nunca é aceito aqui (só no campo de e-mail)."""
    v = " ".join(valor.split())
    if not v:
        raise ValueError(f"{rotulo} é obrigatório.")
    if len(v) < minimo:
        raise ValueError(f"{rotulo} deve ter pelo menos {minimo} caracteres.")
    if len(v) > maximo:
        raise ValueError(f"{rotulo} deve ter no máximo {maximo} caracteres.")
    if so_letras:
        if not all(c.isalpha() or c in " '.-" for c in v):
            raise ValueError("Use apenas letras.")
    elif not all(c.isalnum() or c in " .,'&/()-" for c in v):
        raise ValueError("Use apenas letras, números e os símbolos . , - & ( )")
    return v
