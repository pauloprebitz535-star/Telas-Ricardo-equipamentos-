"""Hash de senha (Argon2) e token de login (JWT)."""
import os
import time

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import config  # noqa: F401  (carrega o .env)

_ph = PasswordHasher()
_HASH_FALSO = _ph.hash("senha-falsa")  # usado quando o usuário não existe (evita revelar quem existe)
bearer = HTTPBearer(auto_error=False)
DURACAO_TOKEN = 8 * 60 * 60  # 8 horas


def gerar_hash(senha: str) -> str:
    """Gera o hash (com salt aleatório embutido). É isso que vai para a coluna senha_hash."""
    return _ph.hash(senha)


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    try:
        return _ph.verify(senha_hash or _HASH_FALSO, senha) and senha_hash is not None
    except (VerificationError, InvalidHashError):
        return False


def _chave() -> str:
    chave = os.getenv("SECRET_KEY")
    if not chave:
        raise RuntimeError("A variável SECRET_KEY não foi encontrada no arquivo .env")
    return chave


def criar_token(usuario: str) -> str:
    agora = int(time.time())
    return jwt.encode({"sub": usuario, "iat": agora, "exp": agora + DURACAO_TOKEN}, _chave(), algorithm="HS256")


def usuario_logado(cred: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    """Dependência: bloqueia a rota se não vier um token válido."""
    if cred is None:
        raise HTTPException(401, "Faça login para continuar.")
    try:
        return jwt.decode(cred.credentials, _chave(), algorithms=["HS256"])["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Sessão inválida ou expirada. Entre novamente.")
