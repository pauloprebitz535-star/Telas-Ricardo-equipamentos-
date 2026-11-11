"""Túnel SSH até o servidor da escola.

O MySQL da instituição só aceita conexão "de dentro" do servidor, então abrimos
um túnel: uma porta local do seu computador que leva até o MySQL pelo SSH.

    seu PC (127.0.0.1:PORTA_LIVRE)  --SSH-->  servidor (127.0.0.1:3306)
"""
import os

from sshtunnel import SSHTunnelForwarder

from . import config  # noqa: F401  (só para carregar o .env)

_tunel = None


def _exigir(nome: str) -> str:
    valor = os.getenv(nome)
    if not valor:
        raise RuntimeError(f"A variável {nome} não foi encontrada no arquivo .env")
    return valor


def abrir_tunel() -> SSHTunnelForwarder:
    global _tunel
    if _tunel is not None and _tunel.is_active:
        return _tunel

    host_banco = os.getenv("DB_HOST", "127.0.0.1")
    porta_banco = int(os.getenv("DB_PORT", "3306"))

    _tunel = SSHTunnelForwarder(
        (_exigir("SSH_HOST"), int(os.getenv("SSH_PORT", "22"))),
        ssh_username=_exigir("SSH_USER"),
        ssh_password=_exigir("SSH_PASSWORD"),
        remote_bind_address=(host_banco, porta_banco),
        local_bind_address=("127.0.0.1", 0),  # porta 0 = o sistema escolhe uma porta livre
        allow_agent=False,
        host_pkey_directories=[],
        set_keepalive=30.0,                    # mantém o túnel vivo
    )
    _tunel.start()
    print(f"[túnel] aberto: 127.0.0.1:{_tunel.local_bind_port} -> {host_banco}:{porta_banco} via {os.getenv('SSH_HOST')}")
    return _tunel


def fechar_tunel() -> None:
    global _tunel
    if _tunel is not None:
        _tunel.stop()
        _tunel = None
        print("[túnel] fechado")
