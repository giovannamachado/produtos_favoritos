"""Script para criar admin inicial.
Uso: python seeds_create_admin.py <nome> <email> <senha>
"""
import sys

from produtos_favoritos.database import Base, SessionLocal, engine
from produtos_favoritos.models import Client
from produtos_favoritos.security import hash_password

Base.metadata.create_all(bind=engine)


def main():
    if len(sys.argv) < 4:
        print("Uso: python seeds_create_admin.py <nome> <email> <senha>")
        sys.exit(1)
    name, email, password = sys.argv[1:4]
    db = SessionLocal()
    try:
        existing = db.query(Client).filter(Client.email == email).first()
        if existing:
            print("Email já existe. Abortando.")
            return
        admin = Client(name=name, email=email,
                       password_hash=hash_password(password), role="admin")
        db.add(admin)
        db.commit()
        print("Admin criado com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
