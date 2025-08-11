# FastAPI Chat Application

This project is a chat application built using FastAPI, which allows users to have conversations. Each conversation can contain multiple messages. The application uses PostgreSQL as the database to store conversations and messages, and SQLAlchemy as the ORM for database interactions.

## Environment Variables Configuration

This project uses environment variables for all configuration. **No sensitive data should be hardcoded in the source code or Docker files.**

### Setup Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your specific values:
   ```bash
   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/chat_app
   POSTGRES_DB=chat_app
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_secure_password

   # Security Configuration (CHANGE THESE IN PRODUCTION!)
   SECRET_KEY=your_very_secure_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Application Configuration
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

   # Docker Database Configuration (for container communication)
   DOCKER_DATABASE_URL=postgresql://user:password@db:5432/chat_app
   ```

### Important Security Notes

- **Never commit the `.env` file to version control**
- Change the `SECRET_KEY` in production to a strong, unique value
- Use strong passwords for database access
- Set `DEBUG=False` in production
- Update `ALLOWED_HOSTS` with your actual domain names

## Project Structure

```
fastapi-chat-app
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1
│   │       ├── __init__.py
│   │       ├── api.py
│   │       ├── endpoints
│   │       │   ├── __init__.py
│   │       │   ├── conversations.py
│   │       │   └── messages.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   └── message.py
│   └── crud
│       ├── __init__.py
│       ├── conversation.py
│       └── message.py
├── alembic
│   ├── versions
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api.py
├── requirements.txt
├── .env.example
├── .env (create from .env.example)
├── docker-compose.yml
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd fastapi-chat-app
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Create a PostgreSQL database and update the `.env` file with the database connection details.

5. **Run migrations:**
   ```
   alembic upgrade head
   ```

6. **Start the application:**
   ```
   uvicorn app.main:app --reload
   ```

## Usage

- The API provides endpoints for managing conversations and messages.
- You can access the API documentation at `http://localhost:8000/docs`.

## Testing

- To run the tests, use:
  ```
  pytest
  ```

## License

This project is licensed under the MIT License.
