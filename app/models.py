"""Tabelas do banco (o mesmo desenho do arquivo banco/schema.sql)."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # a senha NUNCA é guardada pura
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="Ativo")


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # Pessoa Física / Pessoa Jurídica
    documento: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)  # CPF ou CNPJ, só números
    nome: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(11), nullable=False)  # só números, com DDD
    email: Mapped[str] = mapped_column(String(60), nullable=False, default="")


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    codigo: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    fornecedor_id: Mapped[int] = mapped_column(ForeignKey("fornecedores.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Disponível")

    categoria: Mapped[Categoria] = relationship()
    fornecedor: Mapped[Fornecedor] = relationship()
