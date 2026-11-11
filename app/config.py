"""Carrega o arquivo .env (senhas e configurações) como variáveis de ambiente."""
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")
