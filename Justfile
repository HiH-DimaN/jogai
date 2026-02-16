# Jogai development commands

# Start all services
dev:
    docker compose up --build

# Stop all services
down:
    docker compose down

# Run alembic migration
migrate:
    docker compose exec backend alembic upgrade head

# Create new alembic migration
makemigration msg="auto":
    docker compose exec backend alembic revision --autogenerate -m "{{msg}}"

# Show logs
logs service="backend":
    docker compose logs -f {{service}}

# Run database seed
seed:
    docker compose exec backend python -m app.database.seed

# Open psql shell
psql:
    docker compose exec postgres psql -U jogai -d jogai

# Open redis-cli
redis-cli:
    docker compose exec redis redis-cli
