"""Conexão com o MySQL (passando pelo túnel SSH)."""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from . import config  # noqa: F401  (carrega o .env)
from .tunel import abrir_tunel, fechar_tunel


class Base(DeclarativeBase):
    """Classe base de todas as tabelas (models.py)."""


engine = None
SessionLocal = sessionmaker(autoflush=False, autocommit=False)


def iniciar_banco() -> None:
    """Abre o túnel, conecta no MySQL e cria as tabelas que ainda não existem."""
    global engine

    if os.getenv("USAR_TUNEL", "true").lower() == "true":
        tunel = abrir_tunel()
        host, porta = "127.0.0.1", tunel.local_bind_port
    else:  # rodando direto no servidor da escola, sem túnel
        host, porta = os.getenv("DB_HOST", "127.0.0.1"), int(os.getenv("DB_PORT", "3306"))

    # URL.create cuida de caracteres especiais na senha (como o @)
    url = URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=host,
        port=porta,
        database=os.getenv("DB_NAME"),
        query={"charset": "utf8mb4"},
    )
    engine = create_engine(url, pool_pre_ping=True, pool_recycle=280, connect_args={"connect_timeout": 10})
    SessionLocal.configure(bind=engine)

    from . import models  # noqa: F401  (registra as tabelas)
    Base.metadata.create_all(engine)
    print("[banco] conectado e tabelas conferidas")


def encerrar_banco() -> None:
    if engine is not None:
        engine.dispose()
    fechar_tunel()


def get_db():
    """Entrega uma sessão do banco para cada requisição e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
