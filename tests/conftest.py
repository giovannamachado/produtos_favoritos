"""Configuração de fixtures para testes."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from produtos_favoritos.database import Base, get_db
from produtos_favoritos.main import app
from produtos_favoritos.models import Client
from produtos_favoritos.security import hash_password

# Banco de dados em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Cria uma sessão de banco de dados para cada teste."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Cria um cliente de teste com banco de dados mockado."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Cria um usuário de teste."""
    user = Client(
        name="Test User",
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Cria um admin de teste."""
    admin = Client(
        name="Test Admin",
        email="admin@example.com",
        password_hash=hash_password("adminpass123"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def user_token(client, test_user):
    """Gera token para usuário comum."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, test_admin):
    """Gera token para admin."""
    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "adminpass123"}
    )
    return response.json()["access_token"]
