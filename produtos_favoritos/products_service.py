from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .config import get_settings
from .models import Product

settings = get_settings()
BASE_URL = "https://fakestoreapi.com/products"


async def fetch_external_product(product_id: int) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{BASE_URL}/{product_id}")
        if r.status_code == 404:
            raise HTTPException(
                status_code=404, detail="Produto não encontrado na API externa")
        r.raise_for_status()
        return r.json()


def ttl_expired(product: Product) -> bool:
    return datetime.utcnow() - product.last_sync > timedelta(hours=settings.product_cache_ttl_hours)


async def get_or_refresh_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product and not ttl_expired(product):
        return product
    data = await fetch_external_product(product_id)
    if product:
        product.title = data.get("title", product.title)
        product.image = data.get("image", product.image)
        product.price = float(data.get("price", product.price))
        product.last_sync = datetime.utcnow()
    else:
        product = Product(
            id=product_id,
            title=data.get("title"),
            image=data.get("image"),
            price=float(data.get("price", 0)),
            review=None,
            last_sync=datetime.utcnow()
        )
        db.add(product)
    db.commit()
    db.refresh(product)
    return product
