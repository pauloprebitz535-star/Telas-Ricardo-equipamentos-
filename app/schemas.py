"""Formato dos dados que entram e saem da API (e as validações de cada campo)."""
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from .validadores import cnpj_valido, cpf_valido, so_digitos, validar_nome

TipoPessoa = Literal["Pessoa Física", "Pessoa Jurídica"]
StatusCategoria = Literal["Ativo", "Inativo"]
StatusEquipamento = Literal["Disponível", "Em uso", "Em manutenção"]

EMAIL = re.compile(r"^[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")


# ---------------- LOGIN / USUÁRIO ----------------
class LoginIn(BaseModel):
    usuario: str
    senha: str


class UsuarioIn(BaseModel):
    usuario: str
    senha: str

    @field_validator("usuario")
    @classmethod
    def v_usuario(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.fullmatch(r"[a-z0-9_.]{3,20}", v):
            raise ValueError("Usuário: de 3 a 20 caracteres, só letras, números, ponto e _ (sem @).")
        return v

    @field_validator("senha")
    @classmethod
    def v_senha(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")
        if len(v) > 50:
            raise ValueError("A senha deve ter no máximo 50 caracteres.")
        return v


# ---------------- CATEGORIA ----------------
class CategoriaIn(BaseModel):
    nome: str
    descricao: str = ""
    status: StatusCategoria = "Ativo"

    @field_validator("nome")
    @classmethod
    def v_nome(cls, v: str) -> str:
        return validar_nome(v, "Nome", 3, 40)

    @field_validator("descricao")
    @classmethod
    def v_descricao(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 120:
            raise ValueError("Descrição deve ter no máximo 120 caracteres.")
        if "@" in v:
            raise ValueError("O @ só é permitido no campo de e-mail.")
        return v


class CategoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    descricao: str
    status: str


# ---------------- FORNECEDOR ----------------
class FornecedorIn(BaseModel):
    # A ordem importa: "tipo" vem primeiro para o CPF/CNPJ e o nome poderem consultá-lo
    tipo: TipoPessoa
    documento: str
    nome: str
    telefone: str
    email: str = ""

    @field_validator("documento")
    @classmethod
    def v_documento(cls, v: str, info: ValidationInfo) -> str:
        digitos = so_digitos(v)
        if info.data.get("tipo") == "Pessoa Física":
            if not cpf_valido(digitos):
                raise ValueError("CPF inválido.")
        elif not cnpj_valido(digitos):
            raise ValueError("CNPJ inválido.")
        return digitos

    @field_validator("nome")
    @classmethod
    def v_nome(cls, v: str, info: ValidationInfo) -> str:
        fisica = info.data.get("tipo") == "Pessoa Física"
        return validar_nome(v, "Nome" if fisica else "Razão social", 3, 60, so_letras=fisica)

    @field_validator("telefone")
    @classmethod
    def v_telefone(cls, v: str) -> str:
        d = so_digitos(v)
        if len(d) not in (10, 11) or d[0] == "0" or (len(d) == 11 and d[2] != "9"):
            raise ValueError("Telefone inválido. Digite o DDD + número.")
        return d

    @field_validator("email")
    @classmethod
    def v_email(cls, v: str) -> str:
        v = v.strip().lower()
        if v == "":
            return v
        if v.count("@") != 1:
            raise ValueError("O e-mail precisa ter exatamente um @.")
        if len(v) > 60 or not EMAIL.fullmatch(v):
            raise ValueError("Digite um e-mail válido. Ex: nome@gmail.com")
        return v


class FornecedorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: str
    documento: str
    nome: str
    telefone: str
    email: str


# ---------------- EQUIPAMENTO ----------------
class EquipamentoIn(BaseModel):
    nome: str
    codigo: str
    categoria_id: int
    fornecedor_id: int
    status: StatusEquipamento = "Disponível"

    @field_validator("nome")
    @classmethod
    def v_nome(cls, v: str) -> str:
        return validar_nome(v, "Nome", 3, 50)

    @field_validator("codigo")
    @classmethod
    def v_codigo(cls, v: str) -> str:
        v = v.strip()
        if not (v.isascii() and v.isdigit()):
            raise ValueError("Use apenas números.")
        if not 3 <= len(v) <= 8:
            raise ValueError("Código deve ter de 3 a 8 dígitos.")
        return v


class EquipamentoOut(BaseModel):
    id: int
    nome: str
    codigo: str
    categoria_id: int
    fornecedor_id: int
    categoria_nome: str
    fornecedor_nome: str
    status: str
