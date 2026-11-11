-- Rode no MySQL (banco aluno06). O FastAPI também cria essas tabelas sozinho
-- (Base.metadata.create_all), então este arquivo é opcional / para conferência.

CREATE TABLE IF NOT EXISTS usuarios (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario     VARCHAR(20)  NOT NULL,
  senha_hash  VARCHAR(255) NOT NULL,            -- hash Argon2, nunca a senha pura
  criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuarios_usuario (usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categorias (
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome       VARCHAR(40)  NOT NULL,
  descricao  VARCHAR(120) NOT NULL DEFAULT '',
  status     VARCHAR(10)  NOT NULL DEFAULT 'Ativo',
  PRIMARY KEY (id),
  UNIQUE KEY uq_categorias_nome (nome),
  CONSTRAINT ck_categorias_status CHECK (status IN ('Ativo','Inativo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fornecedores (
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  tipo       VARCHAR(20)  NOT NULL,             -- Pessoa Física / Pessoa Jurídica
  documento  VARCHAR(14)  NOT NULL,             -- CPF ou CNPJ, só números
  nome       VARCHAR(60)  NOT NULL,
  telefone   VARCHAR(11)  NOT NULL,             -- só números, com DDD
  email      VARCHAR(60)  NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fornecedores_documento (documento),
  UNIQUE KEY uq_fornecedores_nome (nome),
  CONSTRAINT ck_fornecedores_tipo CHECK (tipo IN ('Pessoa Física','Pessoa Jurídica'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS equipamentos (
  id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome           VARCHAR(50)  NOT NULL,
  codigo         VARCHAR(8)   NOT NULL,
  categoria_id   INT UNSIGNED NOT NULL,
  fornecedor_id  INT UNSIGNED NOT NULL,
  status         VARCHAR(20)  NOT NULL DEFAULT 'Disponível',
  PRIMARY KEY (id),
  UNIQUE KEY uq_equipamentos_codigo (codigo),
  KEY ix_equipamentos_categoria (categoria_id),
  KEY ix_equipamentos_fornecedor (fornecedor_id),
  CONSTRAINT fk_equip_categoria  FOREIGN KEY (categoria_id)  REFERENCES categorias(id)   ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_equip_fornecedor FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT ck_equip_status CHECK (status IN ('Disponível','Em uso','Em manutenção'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
