from fastapi import FastAPI

from .database import Base, engine
from .routers_auth import router as auth_router
from .routers_clients import router as clients_router
from .routers_favorites import router as favorites_router
from .routers_products import router as products_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Produtos Favoritos API",
    version="0.1.0",
    description="""
    ## API para gerenciar clientes e seus produtos favoritos

    Esta API permite:
    * **Gerenciar clientes** - Cadastro, autenticação e perfis
    * **Produtos favoritos** - Adicionar e gerenciar produtos favoritos validados externamente
    * **Integração com FakeStore API** - Validação e cache de produtos
    * **Autenticação JWT** - Segurança com tokens Bearer
    * **Autorização por roles** - Separação entre usuários comuns e administradores

    ### Autenticação
    1. Registre-se em `/auth/register` ou faça login em `/auth/login`
    2. Use o token retornado no header: `Authorization: Bearer {token}`
    3. Clique em "Authorize" e cole o token (sem "Bearer")

    ### Roles
    * **user** - Pode gerenciar apenas seus próprios favoritos
    * **admin** - Pode gerenciar todos os clientes e criar novos admins
    """,
    contact={
        "name": "Giovanna Machado",
        "email": "giovanna@example.com"
    },
    license_info={
        "name": "MIT"
    }
)

app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(favorites_router)
app.include_router(products_router)


@app.get("/health", tags=["health"], summary="Health Check")
def health():
    """Verifica se a API está funcionando."""
    return {"status": "ok"}
