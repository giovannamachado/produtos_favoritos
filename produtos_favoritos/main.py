from fastapi import FastAPI

from .database import Base, engine
from .routers_auth import router as auth_router
from .routers_clients import router as clients_router
from .routers_favorites import router as favorites_router
from .routers_products import router as products_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Produtos Favoritos API", version="0.1.0",
              description="API para gerenciar clientes e seus produtos favoritos.")

app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(favorites_router)
app.include_router(products_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
