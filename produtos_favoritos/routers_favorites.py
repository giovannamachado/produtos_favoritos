from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .deps import get_current_active_user
from .models import Client, Favorite, Product
from .products_service import get_or_refresh_product
from .schemas import FavoriteRead

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/", response_model=list[FavoriteRead])
async def list_favorites(db: Session = Depends(get_db), current: Client = Depends(get_current_active_user)):
    favorites = db.query(Favorite).filter(
        Favorite.client_id == current.id).all()
    result = []
    for fav in favorites:
        product = await get_or_refresh_product(db, fav.product_id)
        result.append(FavoriteRead(product=product, created_at=fav.created_at))
    return result


@router.post("/{product_id}", response_model=FavoriteRead, status_code=201)
async def add_favorite(product_id: int, db: Session = Depends(get_db), current: Client = Depends(get_current_active_user)):
    existing = db.query(Favorite).filter(
        Favorite.client_id == current.id, Favorite.product_id == product_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Produto já favoritado")
    product = await get_or_refresh_product(db, product_id)
    favorite = Favorite(client_id=current.id, product_id=product.id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return FavoriteRead(product=product, created_at=favorite.created_at)


@router.delete("/{product_id}", status_code=204)
async def remove_favorite(product_id: int, db: Session = Depends(get_db), current: Client = Depends(get_current_active_user)):
    favorite = db.query(Favorite).filter(
        Favorite.client_id == current.id, Favorite.product_id == product_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    db.delete(favorite)
    db.commit()
    return None
