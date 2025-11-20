# Arquitetura

## Visão Geral
A API fornece CRUD de clientes e gerenciamento de produtos favoritos. Produtos são validados contra a FakeStore API (`https://fakestoreapi.com/products/{id}`) e armazenados em cache local para reduzir latência e chamadas externas.

## Camadas
- Entrada (FastAPI Routers)
- Serviço (lógica: clientes, favoritos, produtos)
- Repositório (operações DB via SQLAlchemy)
- Infra (DB engine, sessão, http client)

## Fluxo Favorito
1. Usuario chama POST /favorites/{product_id}.
2. Serviço verifica se já existe favorito (unicidade).
3. Busca produto no cache; se ausente ou TTL expirado, faz fetch externo e atualiza/inserir.
4. Cria registro Favorite.
5. Retorna dados combinados.

## Estratégia de Cache
- Campo `last_sync` em Product.
- TTL configurável via env (`PRODUCT_CACHE_TTL_HOURS`).
- Atualização preguiçosa ao acessar (lazy refresh).

## Segurança
- Registro aberto (POST /auth/register).
- Login retorna JWT (POST /auth/login).
- Rotas protegidas exigem Bearer token.
- Autorização baseada em role para endpoints de administração.

## Escalabilidade
- Stateless (JWT) permite múltiplas réplicas.
- Cache em tabela `products` evita fan-out para API externa.
- Possível evoluir para Redis caso o volume de leitura seja alto.

## Próximas Evoluções
- Paginação em listagens.
- Rate limiting.
- Observabilidade (metrics, tracing).
- Revisão de produtos (reviews externos) futura.
