#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting AI-D-ANTS application...${NC}"

# Function to wait for database
wait_for_db() {
    echo -e "${YELLOW}Waiting for database connection...${NC}"

    # Extract database info from environment or use defaults
    DB_HOST=${DB_HOST:-db}
    DB_PORT=${DB_PORT:-5432}
    DB_USER=${DB_USER:-user}
    DB_NAME=${DB_NAME:-chat_app}

    # Wait for database to be ready
    for i in {1..30}; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
            echo -e "${GREEN}Database is ready!${NC}"
            return 0
        fi
        echo -e "${YELLOW}Waiting for database... (attempt $i/30)${NC}"
        sleep 2
    done

    echo -e "${RED}Database connection timeout!${NC}"
    exit 1
}

# Function to run migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"

    cd /app

    # Check if alembic is properly configured
    if [ ! -f "alembic.ini" ]; then
        echo -e "${RED}alembic.ini not found!${NC}"
        exit 1
    fi

    # Run migrations
    if python -m alembic upgrade head; then
        echo -e "${GREEN}Migrations completed successfully!${NC}"
    else
        echo -e "${RED}Migration failed!${NC}"
        exit 1
    fi
}

# Function to start application
start_app() {
    echo -e "${GREEN}Starting FastAPI application...${NC}"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info
}

# Main execution
main() {
    wait_for_db
    run_migrations
    start_app
}

# Run main function
main "$@"
