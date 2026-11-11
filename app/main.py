"""API FastAPI: login com hash + CRUD de categorias, fornecedores e equipamentos."""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import RAIZ
from .database import encerrar_banco, get_db, iniciar_banco
from .models import Categoria, Equipamento, Fornecedor, Usuario
from .schemas import (CategoriaIn, CategoriaOut, EquipamentoIn, EquipamentoOut,
                      FornecedorIn, FornecedorOut, LoginIn, UsuarioIn)
from .seguranca import bearer, criar_token, gerar_hash, usuario_logado, verificar_senha


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    iniciar_banco()      # abre o túnel SSH, conecta e cria as tabelas
    yield
    encerrar_banco()


app = FastAPI(title="Controle de Equipamentos", lifespan=ciclo_de_vida)

ORIGENS = [
    "http://127.0.0.1:5500", "http://localhost:5500",   # Live Server
    "http://127.0.0.1:8000", "http://localhost:8000",   # o próprio FastAPI
]
app.add_middleware(CORSMiddleware, allow_origins=ORIGENS, allow_methods=["*"], allow_headers=["*"])


def salvar(db: Session, msg_conflito: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, msg_conflito)


def buscar(db: Session, modelo, id: int, rotulo: str):
    obj = db.get(modelo, id)
    if obj is None:
        raise HTTPException(404, f"{rotulo} não encontrado(a).")
    return obj


# ---------------- AUTENTICAÇÃO ----------------
@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(RAIZ / "index.html", headers={"Cache-Control": "no-store"})

@app.post("/auth/registrar", status_code=201)
def registrar(dados: UsuarioIn, db: Session = Depends(get_db),
              cred: HTTPAuthorizationCredentials | None = Depends(bearer)):
    # O primeiro usuário pode ser criado sem login; depois disso só quem está logado cria outros.
    if db.scalar(select(func.count()).select_from(Usuario)) > 0:
        usuario_logado(cred)
    db.add(Usuario(usuario=dados.usuario, senha_hash=gerar_hash(dados.senha)))
    salvar(db, "Esse usuário já existe.")
    return {"usuario": dados.usuario}


@app.post("/auth/login")
def login(dados: LoginIn, db: Session = Depends(get_db)):
    nome = dados.usuario.strip().lower()
    u = db.scalar(select(Usuario).where(Usuario.usuario == nome))
    if not verificar_senha(dados.senha, u.senha_hash if u else None):
        raise HTTPException(401, "Usuário ou senha incorretos.")
    return {"access_token": criar_token(u.usuario), "token_type": "bearer", "usuario": u.usuario}


# ---------------- CATEGORIAS ----------------
@app.get("/categorias", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    return db.scalars(select(Categoria).order_by(Categoria.nome)).all()


@app.post("/categorias", response_model=CategoriaOut, status_code=201)
def criar_categoria(dados: CategoriaIn, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    c = Categoria(**dados.model_dump())
    db.add(c)
    salvar(db, "Já existe uma categoria com esse nome.")
    return c


@app.put("/categorias/{id}", response_model=CategoriaOut)
def editar_categoria(id: int, dados: CategoriaIn, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    c = buscar(db, Categoria, id, "Categoria")
    for campo, valor in dados.model_dump().items():
        setattr(c, campo, valor)
    salvar(db, "Já existe uma categoria com esse nome.")
    return c


@app.delete("/categorias/{id}", status_code=204)
def excluir_categoria(id: int, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    db.delete(buscar(db, Categoria, id, "Categoria"))
    salvar(db, "Categoria em uso por algum equipamento.")


# ---------------- FORNECEDORES ----------------
@app.get("/fornecedores", response_model=list[FornecedorOut])
def listar_fornecedores(db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    return db.scalars(select(Fornecedor).order_by(Fornecedor.nome)).all()


@app.post("/fornecedores", response_model=FornecedorOut, status_code=201)
def criar_fornecedor(dados: FornecedorIn, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    f = Fornecedor(**dados.model_dump())
    db.add(f)
    salvar(db, "Já existe fornecedor com esse documento ou nome.")
    return f


@app.put("/fornecedores/{id}", response_model=FornecedorOut)
def editar_fornecedor(id: int, dados: FornecedorIn, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    f = buscar(db, Fornecedor, id, "Fornecedor")
    for campo, valor in dados.model_dump().items():
        setattr(f, campo, valor)
    salvar(db, "Já existe fornecedor com esse documento ou nome.")
    return f


@app.delete("/fornecedores/{id}", status_code=204)
def excluir_fornecedor(id: int, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    db.delete(buscar(db, Fornecedor, id, "Fornecedor"))
    salvar(db, "Fornecedor em uso por algum equipamento.")


# ---------------- EQUIPAMENTOS ----------------
def eq_out(e: Equipamento) -> EquipamentoOut:
    return EquipamentoOut(id=e.id, nome=e.nome, codigo=e.codigo, categoria_id=e.categoria_id,
                          fornecedor_id=e.fornecedor_id, categoria_nome=e.categoria.nome,
                          fornecedor_nome=e.fornecedor.nome, status=e.status)


def conferir_vinculos(db: Session, dados: EquipamentoIn) -> None:
    buscar(db, Categoria, dados.categoria_id, "Categoria")
    buscar(db, Fornecedor, dados.fornecedor_id, "Fornecedor")


@app.get("/equipamentos", response_model=list[EquipamentoOut])
def listar_equipamentos(db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    return [eq_out(e) for e in db.scalars(select(Equipamento).order_by(Equipamento.nome)).all()]


@app.post("/equipamentos", response_model=EquipamentoOut, status_code=201)
def criar_equipamento(dados: EquipamentoIn, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    conferir_vinculos(db, dados)
    e = Equipamento(**dados.model_dump())
    db.add(e)
    salvar(db, "Já existe um equipamento com esse código.")
    db.refresh(e)
    return eq_out(e)


@app.put("/equipamentos/{id}", response_model=EquipamentoOut)
def editar_equipamento(id: int, dados: EquipamentoIn, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    e = buscar(db, Equipamento, id, "Equipamento")
    conferir_vinculos(db, dados)
    for campo, valor in dados.model_dump().items():
        setattr(e, campo, valor)
    salvar(db, "Já existe um equipamento com esse código.")
    db.refresh(e)
    return eq_out(e)


@app.delete("/equipamentos/{id}", status_code=204)
def excluir_equipamento(id: int, db: Session = Depends(get_db), _: str = Depends(usuario_logado)):
    db.delete(buscar(db, Equipamento, id, "Equipamento"))
    salvar(db, "Não foi possível excluir o equipamento.")
