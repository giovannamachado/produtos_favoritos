# 🛍️ API de Produtos Favoritos

Uma API REST para gerenciar clientes e seus produtos favoritos, integrando com a FakeStore API para validação de produtos.

---

## 🎯 Sobre o Projeto

 A ideia: permitir que clientes marquem produtos como favoritos, com validação em tempo real contra uma API externa.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos

- Python 3.10, 3.11 ou 3.12 (no Windows, use 3.12)
- PostgreSQL rodando
- Git

### Passo a Passo

**1. Clone o repositório**
```bash
git clone git@github.com:giovannamachado/produtos_favoritos.git
cd produtos_favoritos
```

**2. Crie e ative o ambiente virtual**
```bash

# Windows (PowerShell)
# Garanta Python 3.12:
# Se precisar instalar: winget install Python.Python.3.12
winget install -e --id Python.Python.3.12


# Se já tiver o Python.3.12 instalado, pule para essa etapa e recrie o ambiente (Remove ambiente antigo (se existir) para garantir uma instalação limpa)
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
py -3.12 -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

**3. Instale as dependências**
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Nota para Windows:** Caso esteja com Python 3.13+ ou 3.14 e veja erro do `pydantic-core` pedindo Rust/Cargo, recrie o venv com Python 3.12 conforme acima (é o caminho mais simples e rápido).


**4. Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o .env com suas configurações de banco
```

Exemplo de `.env`:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/produtos_favoritos
JWT_SECRET=seu-secret-super-seguro-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=60
PRODUCT_CACHE_TTL_HOURS=24
```

**5. Crie o banco de dados**
```bash
# Escolha uma das opções abaixo:
# Opção A: Via Docker (necessário ter o docker desktop instalado)
# 1. Subir o container do Postgres
docker run --name postgres-local -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
docker exec -it postgres-local createdb -U postgres produtos_favoritos

# 2. Criar o banco de dados dentro do container
docker exec -it postgres-local createdb -U postgres produtos_favoritos

#Opção B: Via Instalação Local
# Via linha de comando psql
psql -U postgres -c "CREATE DATABASE produtos_favoritos;"
```

**6. Crie um usuário admin inicial**
```bash
python seeds_create_admin.py "Admin" "admin@email.com" "senha123"
```
**7. Inicie o servidor**
```bash
uvicorn produtos_favoritos.main:app --reload
```
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

```bash
pytest --cov=produtos_favoritos --cov-report=html

```
---
Escolhi FastAPI pela performance (é assíncrono de verdade) e pela documentação automática via OpenAPI. Além disso, a validação de dados com Pydantic economiza muito tempo e evita bugs bobos.

### Sistema de Cache
implementei um cache local dos produtos da API externa.

**O problema:** Toda vez que alguém lista favoritos, precisaria buscar dados de N produtos na API externa. Isso é lento e pode sobrecarregar a API.

# Exemplo simplificado
if product and not ttl_expired(product):
    return product  # Retorna do cache - super rápido!
# Senão, busca na API externa e atualiza o cache
```

### Autenticação e Autorização

**JWT (JSON Web Tokens):** Stateless, escalável, funciona bem em arquiteturas distribuídas. O token carrega as informações do usuário e expira após 60 minutos (configurável).

**Bcrypt para senhas:** Salva senha em texto plano. Bcrypt é lento de propósito (dificulta ataques de força bruta) e adiciona salt automático.
**Sistema de Roles:** Separa usuários comuns de admins. Usuários só mexem nos próprios favoritos, admins podem gerenciar todos os clientes. Simples e efetivo.

- `*_service.py` → Lógica de negócio

Isso facilita manutenção e testes. Se amanhã eu precisar trocar o banco ou adicionar Redis, consigo fazer com mudanças mínimas.

```python
id: int (PK)
role: str ('user' ou 'admin')
```

id: int (PK, mesmo ID da API externa)
image: str (URL)
price: float
review: str (ex: "Rating: 4.5/5 (120 reviews)")
last_sync: datetime (para controle do TTL)

### Favorite (Favorito)
```python
id: int (PK)
# Garante que um cliente não favoritará o mesmo produto 2x
```

---

## 🔐 Endpoints

### Autenticação
- `POST /auth/register` - Criar conta
- `POST /auth/login` - Login (retorna JWT)
- `GET /auth/me` - Dados do usuário logado

### Clientes (requer admin)
- `GET /clients/` - Listar todos
- `GET /clients/{id}` - Buscar por ID
- `POST /clients/?role=user` - Criar novo cliente
- `PATCH /clients/{id}` - Atualizar cliente
- `DELETE /clients/{id}` - Deletar cliente

### Próprio Perfil (qualquer usuário autenticado)
- `PATCH /clients/me` - Atualizar próprio nome

### Favoritos (requer autenticação)
- `GET /favorites/` - Listar meus favoritos
- `POST /favorites/{product_id}` - Adicionar favorito
- `DELETE /favorites/{product_id}` - Remover favorito

### Produtos (público)
- `GET /products/{id}` - Buscar produto (usa cache)

---

## 🎨 Funcionalidades Extras

- **Health Check:** `GET /health` - Verifica se a API está viva
- **Documentação automática:** Swagger UI em `/docs`
- **Validação robusta:** Pydantic garante tipos corretos
- **Testes completos:** 27 testes automatizados (100% passing)
- **Mensagens de erro descritivas:** Facilita debugging

---

## 🐛 Tratamento de Erros

Todos os erros retornam JSON com formato consistente:
```json
{
  "detail": "Descrição clara do erro"
}
```

Status codes corretos:
- `200/201` → Sucesso
- `400` → Validação falhou
- `401` → Não autenticado
- `403` → Sem permissão
- `404` → Não encontrado
- `409` → Conflito (ex: email duplicado)
- `500` → Erro interno

---


## 👩‍💻 Autora
 Giovanna Machado
