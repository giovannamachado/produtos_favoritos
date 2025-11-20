from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import Client

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/auth/login", scheme_name="JWT")
settings = get_settings()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(reuseable_oauth)) -> Client:
    credentials_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Credenciais inválidas", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.jwt_secret,
                             algorithms=[settings.jwt_algorithm])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc
    user = db.query(Client).filter(Client.email == email).first()
    if not user:
        raise credentials_exc
    return user


def get_current_active_user(current: Client = Depends(get_current_user)) -> Client:
    return current


def get_current_admin(current: Client = Depends(get_current_user)) -> Client:
    if current.role != "admin":
        raise HTTPException(
            status_code=403, detail="Acesso restrito a administradores")
    return current
