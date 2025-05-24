# 🔖 OG Tag Image Previewer

This is a fullstack web application to scrape and preview an Open Graph image from any given URL.
Consisting of:
- A FastAPI + PostgreSQL backend
- A React.js + Vite frontend

# Backend - FastAPI + PostgreSQL + Redis

## Features
- FastAPI for async, high-performance APIs.
- PostgreSQL as the relational database
- Redis as the cache
- Asynchronous SQLAlchemy (asyncpg)
- CORS support and logging
- Modular project structure
- Web UI of API docs at /docs

## Why FastAPI + PostgreSQL?

- FastAPI is modern, fast, and supports async out of the box with automatic validation compared to Django in Python ecosystem. It also provide a playground web ui for docs and testing at http://localhost:8000/docs
- PostgreSQL is a powerful, scalable relational database.
- SQLAlchemy (async) provides a full-featured ORM for PostgreSQL.
- Redis is a widely used, easy-to-set-up distributed cache that supports horizontal scaling.

## Setup Instructions

### 1. Requirements
- Python 3
- PostgreSQL running locally
- Redis running locally
- Virtualenv (python -m venv venv)

### 2. Set up Database URL

Install PostgreSQL (If you didn't)
```
brew install postgresql
brew services start postgresql
psql --version # verify
```

On PostgreSQl cli
```
psql -U username -d postgres -c "CREATE DATABASE og_preview;"
```

In codebase

```
cd backend
export DATABASE_URL="postgresql+asyncpg://<username>:<password>@localhost:5432/og_preview"
```

### 3. Run Redis
```
brew install redis
brew services start redis
redis-cli ping # Test, it should response PONG
```

### 4. Install dependencies
```
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Run the application

```
cd backend
uvicorn main:app --reload
```

- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 6. Run unit tests

```
cd backend

# To run specific test
python3 -m tests.test_og_scraper

# To run all tests
python -m unittest discover -s tests
```

## Future Improvements

### Code base level
- Split backend vs frontend into two repositories
Add authentication (OAuth2 or JWT)
- Add styling check (mypy, black)
- Add database schema migration support (Alembic)
- Replace the cursor id in pagination logic with timestamp or other logic to prevent data leak.
- Support more sorting types to APIs
- Add integration tests

### System level
- CI/CD pipeline (e.g., GitHub Actions)
- Docker setup and Deployment (e.g., Kubernetes, GCP/AWS)
- Add rate limiting, logging improvements
- Horizontally scale on database, Redis, server and add load balancer.
- Split very complicate scrapping tasks to async workers (e.g., Kafka, Celery).

____

# Frontend - React.js + Vite

## Features

- Vite for fast bundling and dev environment
- React.js for building UI components
- Fetches data from FastAPI backend

## Why Vite + React.js?

- Vite offers a lightning-fast dev server and optimized build process.
- React.js is widely adopted and allows fast, flexible UI development.

## Setup Instructions

### 1. Requirements
- Node.js

### 2. Install dependencies

```
cd frontend
npm install
```

### 3. Run the development server

```
npm run dev
```

Visit UI: http://localhost:5173

## Future Improvements

- Replace the load more button with the scrolling down event
- Add routing with React Router
- Add global state management (Redux)
- Add form validation
- Improve UI with component libraries (e.g., Chakra UI, Material UI)
- Unit tests and integration tests.
