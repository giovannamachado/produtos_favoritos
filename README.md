# API de Produtos Favoritos

## Objetivo
Gerenciar clientes e seus produtos favoritos validando contra a FakeStore API.

## Stack
- Python, FastAPI
- PostgreSQL + SQLAlchemy
- Autenticação JWT (python-jose) + hash de senha (passlib)
- Cache de produtos local (tabela `products`) com TTL configurável

## Modelos
- Client: id, name, email (único), password_hash, role (user/admin), created_at
- Product: id (igual ao ID externo), title, image, price, review (nullable), last_sync
- Favorite: id, client_id FK, product_id FK, created_at (unique constraint em (client_id, product_id))

## Endpoints (planejados)
Auth:
- POST /auth/register
- POST /auth/login -> JWT
- GET /me -> dados do cliente autenticado
- PATCH /me -> alterar nome

Clientes (admin):
- GET /clients
- GET /clients/{id}
- POST /clients (criar cliente admin ou user)
- PATCH /clients/{id}
- DELETE /clients/{id}

Favoritos:
- GET /favorites -> lista favoritos do usuário (com dados de produto)
- POST /favorites/{product_id} -> adiciona favorito (valida produto)
- DELETE /favorites/{product_id} -> remove favorito

Produtos:
- GET /products/{product_id} -> retorna produto (usa cache/local fetch)

## Autorização
- Rotas /clients* restritas a role=admin.
- Rotas de favoritos referenciam somente o usuário autenticado.

## Execução rápida
```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
uvicorn produtos_favoritos.main:app --reload
```

