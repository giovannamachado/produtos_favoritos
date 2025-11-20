#  Guia de Testes Manuais - API Produtos Favoritos

##  Pré-requisitos

1. **Ambiente configurado:**
   ```bash
   # Ativar ambiente virtual
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\Activate.ps1  # Windows PowerShell

   # Instalar dependências
   pip install -r requirements.txt

   # Configurar .env
   cp .env.example .env
   # Edite o .env com suas configurações de banco
   ```

2. **PostgreSQL rodando** com database `produtos_favoritos` criado

3. **Servidor iniciado:**
   ```bash
   uvicorn produtos_favoritos.main:app --reload
   ```

4. **Criar admin inicial:**
   ```bash
   python seeds_create_admin.py "Admin" "admin@test.com" "admin123"
   ```

5. **Ferramentas de teste:**
   - Swagger UI: http://localhost:8000/docs
   - Postman, Insomnia ou curl

---

##  Fase 1: Autenticação

### 1.1 Registrar Novo Usuário
**Endpoint:** `POST /auth/register`

**Request:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "password": "senha123"
  }'
```

**Validações:**
 Status: 201 Created
 Retorna: id, name, email, role ("user"), created_at
 NÃO retorna password
 Tentar registrar mesmo email novamente → 409 Conflict

---

### 1.2 Login
**Endpoint:** `POST /auth/login`

**Request (form-data):**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@example.com&password=senha123"
```

**Validações:**
 Status: 200 OK
 Retorna: access_token, token_type ("bearer")
 Credenciais erradas → 401 Unauthorized
 Email inexistente → 401 Unauthorized

** IMPORTANTE:** Salve o `access_token` para usar nos próximos testes!

---

### 1.3 Obter Dados do Usuário Autenticado
**Endpoint:** `GET /auth/me`

**Request:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**Validações:**
 Status: 200 OK
 Retorna dados do usuário logado
 Sem token → 401 Unauthorized
 Token inválido → 401 Unauthorized

---

##  Fase 2: Gerenciamento de Clientes (Admin)

** Use o token do admin para estes testes**

### 2.1 Listar Todos os Clientes
**Endpoint:** `GET /clients/`

**Request:**
```bash
curl -X GET http://localhost:8000/clients/ \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

**Validações:**
 Status: 200 OK
 Retorna array de clientes
 Usuário comum → 403 Forbidden
 Sem autenticação → 401 Unauthorized

---

### 2.2 Buscar Cliente por ID
**Endpoint:** `GET /clients/{id}`

**Request:**
```bash
curl -X GET http://localhost:8000/clients/1 \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

**Validações:**
 Status: 200 OK
 Retorna dados do cliente
 ID inexistente → 404 Not Found
 Usuário comum → 403 Forbidden

---

### 2.3 Criar Cliente (Admin pode criar user ou admin)
**Endpoint:** `POST /clients/?role=user`

**Request:**
```bash
curl -X POST "http://localhost:8000/clients/?role=user" \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Santos",
    "email": "maria@example.com",
    "password": "senha456"
  }'
```

**Validações:**
 Status: 201 Created
 Retorna cliente com role especificada
 role=admin também funciona
 Email duplicado → 409 Conflict
 Usuário comum tentando criar → 403 Forbidden

---

### 2.4 Atualizar Cliente (Admin)
**Endpoint:** `PATCH /clients/{id}`

**Request:**
```bash
curl -X PATCH http://localhost:8000/clients/2 \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Maria Santos Silva"}'
```

**Validações:**
 Status: 200 OK
 Nome atualizado
 ID inexistente → 404 Not Found

---

### 2.5 Atualizar Próprio Perfil (Qualquer usuário)
**Endpoint:** `PATCH /clients/me`

**Request:**
```bash
curl -X PATCH http://localhost:8000/clients/me \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva Oliveira"}'
```

**Validações:**
 Status: 200 OK
 Nome do usuário autenticado atualizado

---

### 2.6 Deletar Cliente (Admin)
**Endpoint:** `DELETE /clients/{id}`

**Request:**
```bash
curl -X DELETE http://localhost:8000/clients/3 \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

**Validações:**
 Status: 204 No Content
 Cliente removido do banco
 ID inexistente → 404 Not Found
 Usuário comum → 403 Forbidden

---

##  Fase 3: Produtos

### 3.1 Buscar Produto (Pública, usa cache)
**Endpoint:** `GET /products/{id}`

**Request:**
```bash
curl -X GET http://localhost:8000/products/1
```

**Validações:**
 Status: 200 OK
 Retorna: id, title, image, price, review
 review contém "Rating: X/5 (Y reviews)"
 Produto inexistente na API externa → 404 Not Found
 Segunda chamada retorna do cache (mais rápido)

** Teste de Cache:**
```bash
# Primeira chamada - busca na API externa (pode demorar)
time curl http://localhost:8000/products/1

# Segunda chamada - retorna do cache (instantâneo)
time curl http://localhost:8000/products/1
```

---

##  Fase 4: Favoritos

** Use token de usuário comum (não admin)**

### 4.1 Adicionar Produto aos Favoritos
**Endpoint:** `POST /favorites/{product_id}`

**Request:**
```bash
curl -X POST http://localhost:8000/favorites/1 \
  -H "Authorization: Bearer TOKEN_USER"
```

**Validações:**
 Status: 201 Created
 Retorna: product (com id, title, image, price, review) e created_at
 Produto é validado na API externa
 Produto inexistente → 404 Not Found
 Adicionar mesmo produto novamente → 409 Conflict
 Sem autenticação → 401 Unauthorized

---

### 4.2 Listar Favoritos
**Endpoint:** `GET /favorites/`

**Request:**
```bash
curl -X GET http://localhost:8000/favorites/ \
  -H "Authorization: Bearer TOKEN_USER"
```

**Validações:**
 Status: 200 OK
 Retorna array de favoritos com dados completos do produto
 Cada item tem: product e created_at
 Lista vazia se usuário não tem favoritos
 Sem autenticação → 401 Unauthorized
 Cada usuário vê apenas seus próprios favoritos

---

### 4.3 Remover Favorito
**Endpoint:** `DELETE /favorites/{product_id}`

**Request:**
```bash
curl -X DELETE http://localhost:8000/favorites/1 \
  -H "Authorization: Bearer TOKEN_USER"
```

**Validações:**
 Status: 204 No Content
 Favorito removido
 Produto não favoritado → 404 Not Found
 Sem autenticação → 401 Unauthorized

---

##  Fase 5: Validações de Regras de Negócio

### 5.1 Email Único
```bash
# Registrar usuário
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "test@test.com", "password": "123456"}'

# Tentar registrar novamente com mesmo email → 409
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test2", "email": "test@test.com", "password": "654321"}'
```

---

### 5.2 Produto Não Duplicado na Lista de Favoritos
```bash
# Adicionar favorito
curl -X POST http://localhost:8000/favorites/1 \
  -H "Authorization: Bearer TOKEN_USER"

# Tentar adicionar novamente → 409
curl -X POST http://localhost:8000/favorites/1 \
  -H "Authorization: Bearer TOKEN_USER"
```

---

### 5.3 Validação de Produto Externo
```bash
# Produto válido (existe na FakeStore API)
curl -X POST http://localhost:8000/favorites/1 \
  -H "Authorization: Bearer TOKEN_USER"

# Produto inválido (não existe)
curl -X POST http://localhost:8000/favorites/99999 \
  -H "Authorization: Bearer TOKEN_USER"
# Deve retornar 404
```

---

### 5.4 Produtos Exibem Review
```bash
# Buscar qualquer produto
curl http://localhost:8000/products/1

# Verificar no response:
# "review": "Rating: 3.9/5 (120 reviews)"
```

---

### 5.5 Isolamento de Favoritos por Usuário
```bash
# Login como usuário 1
TOKEN1=$(curl -X POST http://localhost:8000/auth/login \
  -d "username=user1@test.com&password=pass1" | jq -r .access_token)

# Adicionar favorito
curl -X POST http://localhost:8000/favorites/1 -H "Authorization: Bearer $TOKEN1"

# Login como usuário 2
TOKEN2=$(curl -X POST http://localhost:8000/auth/login \
  -d "username=user2@test.com&password=pass2" | jq -r .access_token)

# Listar favoritos do usuário 2 → deve estar vazio
curl http://localhost:8000/favorites/ -H "Authorization: Bearer $TOKEN2"
```

---

##  Fase 6: Segurança e Autorização

### 6.1 Rotas Protegidas
```bash
# Tentar acessar sem token → 401
curl http://localhost:8000/favorites/
curl http://localhost:8000/clients/
curl http://localhost:8000/auth/me

# Com token inválido → 401
curl http://localhost:8000/favorites/ -H "Authorization: Bearer token_invalido"
```

---

### 6.2 Autorização por Role
```bash
# Usuário comum tentando acessar rotas de admin → 403
curl -X GET http://localhost:8000/clients/ \
  -H "Authorization: Bearer TOKEN_USER"

curl -X POST http://localhost:8000/clients/?role=user \
  -H "Authorization: Bearer TOKEN_USER" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "test@test.com", "password": "123456"}'
```

---

##  Checklist Final de Requisitos

### Clientes
- [x] Criar cliente (POST /auth/register)
- [x] Visualizar clientes (GET /clients/ - admin)
- [x] Editar cliente (PATCH /clients/{id} - admin, PATCH /clients/me - próprio usuário)
- [x] Remover cliente (DELETE /clients/{id} - admin)
- [x] Nome e email obrigatórios
- [x] Email único

### Favoritos
- [x] Cliente tem lista de produtos favoritos
- [x] Produtos validados via API externa (FakeStore)
- [x] Produto não duplicado na lista
- [x] Exibe: ID, título, imagem, preço, review

### Autenticação/Autorização
- [x] API pública com autenticação JWT
- [x] Autorização por roles (admin/user)
- [x] Rotas protegidas

### Integração Externa
- [x] FakeStore API integrada
- [x] GET /products/{id}
- [x] Cache local com TTL

### Qualidade
- [x] Código estruturado
- [x] Boas práticas REST
- [x] Evita duplicidade
- [x] Performance (cache)
- [x] Documentação (Swagger)
- [x] Testes automatizados

---

##  Executar Testes Automatizados

```bash
# Executar todos os testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=produtos_favoritos --cov-report=html

# Teste específico
pytest tests/test_auth.py -v
pytest tests/test_favorites.py::test_add_favorite_success -v
```

---

##  Swagger UI

Acesse: **http://localhost:8000/docs**

Interface interativa para testar todos os endpoints:
1. Clique em "Authorize"
2. Cole o token (sem "Bearer")
3. Teste endpoints clicando em "Try it out"
