<div align="center">
  <h1>🔗 Link Shortener Backend</h1>
  <p>
    <strong>A high-performance, scalable link shortening service with analytics built with FastAPI and PostgreSQL</strong>
  </p>
  <p>
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-reference">API Reference</a> •
    <a href="#deployment">Deployment</a>
  </p>
  
  [![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![Tests](https://github.com/yourusername/link-shortener-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/link-shortener-backend/actions)
</div>

## 🌟 Features

### Core Features

- **URL Shortening**: Convert long URLs into short, shareable links
- **Custom Short Codes**: Create memorable custom short codes
- **Link Management**: Full CRUD operations for managing links
- **Password Protection**: Secure sensitive links with passwords
- **Analytics Dashboard**: Track clicks, referrers, and geographic data
- **Custom Domains**: Support for custom domain mapping
- **API-First Design**: Fully documented RESTful API with OpenAPI/Swagger
- **User Authentication**: JWT-based authentication system
- **Rate Limiting**: Protect against abuse with configurable rate limits
- **Bulk Operations**: Import/export links in various formats
- **Link Expiration**: Set expiration dates for temporary links

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework for building APIs with Python 3.7+
- **Database**: 
  - [PostgreSQL](https://www.postgresql.org/) - Powerful, open source relational database
  - [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
  - [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- **Authentication**: [JWT](https://jwt.io/) - JSON Web Tokens for secure authentication
- **Validation**: [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management
- **Async**: [asyncpg](https://github.com/MagicStack/asyncpg) - Fast PostgreSQL database client

### Development & Testing
- **Testing**: 
  - [pytest](https://docs.pytest.org/) - Test framework
  - [pytest-cov](https://pytest-cov.readthedocs.io/) - Test coverage
  - [HTTPX](https://www.python-httpx.org/) - Async HTTP client for testing
- **Code Quality**:
  - [Black](https://github.com/psf/black) - Code formatter
  - [isort](https://pycqa.github.io/isort/) - Import sorter
  - [mypy](http://mypy-lang.org/) - Static type checking
  - [flake8](https://flake8.pycqa.org/) - Linter

### Deployment
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **CI/CD**: [GitHub Actions](https://github.com/features/actions)
- **Monitoring**: [Prometheus](https://prometheus.io/) & [Grafana](https://grafana.com/) (optional)
- **Logging**: [Loguru](https://github.com/Delgan/loguru) - Simplified logging

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)
- Docker & Docker Compose (recommended for development)
- Git (for version control)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/link-shortener-backend.git
   cd link-shortener-backend
   ```

2. **Set up Python environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/link_shortener
   
   # Security
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Application
   DEBUG=True
   DEFAULT_DOMAIN=localhost:8000
   SHORT_CODE_LENGTH=6
   MAX_SHORT_CODE_LENGTH=50
   
   # Rate limiting (requests per minute)
   RATE_LIMIT=100
   ```

4. **Set up the database**
   ```bash
   # Create database (if not using Docker)
   createdb link_shortener
   
   # Run migrations
   alembic upgrade head
   
   # Seed initial data (optional)
   python -m app.db.init_db
   ```

5. **Run the application**
   ```bash
   # Development server with auto-reload
   uvicorn app.main:app --reload
   
   # Production server (with Gunicorn)
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

6. **Access the application**
   - API: `http://localhost:8000`
   - Interactive API docs (Swagger UI): `http://localhost:8000/docs`
   - Alternative API docs (ReDoc): `http://localhost:8000/redoc`
   - Health check: `http://localhost:8000/health`

### Running with Docker

For development or production deployment using Docker:

```bash
# Build and start services
docker-compose up --build

# Run specific services
docker-compose up -d postgres redis

# View logs
docker-compose logs -f

# Run tests
docker-compose run --rm web pytest
```

## 🧪 Testing

Run the complete test suite:

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_links.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

## 📚 API Reference

Detailed API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Authentication

All protected endpoints require a valid JWT token in the `Authorization` header:
```
Authorization: Bearer your-jwt-token
```

### Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/token` - Get access token
- `POST /api/v1/auth/refresh` - Refresh access token

#### Links

The Link API supports both minimal and advanced usage patterns. Start simple and add features as needed.

**1. Minimal Request (Just URL)**
```http
POST /api/v1/links/
Content-Type: application/json
Authorization: Bearer your-jwt-token

{
  "url": "https://example.com/very/long/url"
}
```

**2. With Custom Short Code**
```http
POST /api/v1/links/
Content-Type: application/json
Authorization: Bearer your-jwt-token

{
  "url": "https://example.com/very/long/url",
  "short_code": "mylink"
}
```

**3. With Title and Description**
```http
POST /api/v1/links/
Content-Type: application/json
Authorization: Bearer your-jwt-token

{
  "url": "https://example.com/very/long/url",
  "title": "My Example Link",
  "description": "This is an example link for testing"
}
```

**4. Advanced Usage (Custom Domain, Pixels, Tags)**
```http
POST /api/v1/links/
Content-Type: application/json
Authorization: Bearer your-jwt-token

{
  "url": "https://example.com/marketing/campaign",
  "space_id": "123e4567-e89b-12d3-a456-426614174000",
  "domain_id": "short.ly",
  "short_code": "campaign2024",
  "title": "Marketing Campaign 2024",
  "description": "Main landing page for our 2024 marketing campaign",
  "tags": ["marketing", "campaign", "2024"],
  "password": "secret123",
  "pixel_ids": [
    "123e4567-e89b-12d3-a456-426614174001",
    "123e4567-e89b-12d3-a456-426614174002"
  ],
  "expires_at": "2024-12-31T23:59:59"
}
```

**Response (All Examples)**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "space_id": "123e4567-e89b-12d3-a456-426614174001",
  "short_code": "abc123",
  "url": "https://example.com/very/long/url",
  "title": "My Example Link",
  "short_url": "http://localhost:8000/abc123",
  "is_active": true,
  "created_at": "2023-05-15T10:30:45.123456"
}
```

**Field Descriptions**
- `url` (required): The destination URL to redirect to
- `space_id` (optional): Space ID for organization
- `domain_id` (optional): Custom domain name (must be verified)
- `short_code` (optional): Custom short code (auto-generated if not provided)
- `title` (optional): Human-readable title for the link
- `description` (optional): Longer description for the link
- `tags` (optional): Array of tags for categorization
- `password` (optional): Password protection for the link
- `pixel_ids` (optional): Array of pixel IDs for tracking
- `expires_at` (optional): ISO datetime when link expires

**Other Endpoints**
- `GET /api/v1/links` - List all links (paginated)
- `GET /api/v1/links/{link_id}` - Get link details
- `PUT /api/v1/links/{link_id}` - Update a link
- `DELETE /api/v1/links/{link_id}` - Delete a link
- `GET /go/{short_code}` - Redirect to original URL

#### Analytics
- `GET /api/v1/analytics/links/{link_id}` - Get link analytics
- `GET /api/v1/analytics/domains/{domain}` - Get domain analytics
- `GET /api/v1/analytics/summary` - Get summary statistics

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `postgresql://user:password@localhost:5432/link_shortener` |
| `SECRET_KEY` | Secret key for JWT | `your-secret-key` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration (minutes) | `30` |
| `DEFAULT_DOMAIN` | Default domain for short links | `localhost:8000` |
| `SHORT_CODE_LENGTH` | Length of auto-generated codes | `6` |
| `MAX_SHORT_CODE_LENGTH` | Max length of custom codes | `50` |
| `RATE_LIMIT` | Requests per minute | `100` |
| `DEBUG` | Enable debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🚀 Deployment

### Production Setup

1. **Set up a production database**
   ```bash
   # Example for PostgreSQL on Ubuntu
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo -u postgres createuser -P link_shortener
   sudo -u postgres createdb -O link_shortener link_shortener_prod
   ```

2. **Install application**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Set production environment variables
   export DATABASE_URL=postgresql://user:password@localhost:5432/link_shortener_prod
   export DEBUG=False
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

### Docker Production

```bash
# Build and run in production mode
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write tests for new features
- Update documentation when necessary
- Use type hints for better code clarity
- Keep commits small and focused

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - The ORM for database operations
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations made easy
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management
- [Docker](https://www.docker.com/) - Containerization platform
- [GitHub Actions](https://github.com/features/actions) - CI/CD pipeline

## 📈 Monitoring & Logging

### Application Metrics

Metrics are exposed in Prometheus format at `/metrics`:

```bash
# Example metrics endpoint
curl http://localhost:8000/metrics
```

### Logging Configuration

Logs are structured in JSON format and can be configured via environment variables:

```python
# Example log message
{
  "timestamp": "2023-05-15T10:30:45.123456",
  "level": "INFO",
  "message": "Application startup complete",
  "module": "app.main",
  "function": "startup_event"
}
```

## 🔒 Security

### Authentication Flow

1. User authenticates with email/password
2. Server validates credentials and issues JWT token
3. Client includes token in `Authorization` header for subsequent requests
4. Server validates token on each protected endpoint

### Security Headers

The application includes security headers by default:
- Content Security Policy (CSP)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- HSTS (in production)

## 📦 Dependencies

### Production Dependencies

- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- Python-JOSE - JWT implementation
- asyncpg - Async PostgreSQL client
- python-multipart - Form parsing
- uvicorn - ASGI server

### Development Dependencies

- pytest - Testing framework
- HTTPX - Async HTTP client
- pytest-asyncio - Async test support
- pytest-cov - Coverage reporting
- black - Code formatting
- isort - Import sorting
- mypy - Static type checking
- flake8 - Linting

## 🌍 Internationalization (i18n)

The API supports multiple languages through the `Accept-Language` header:

```http
GET /api/v1/links
Accept-Language: es  # Returns responses in Spanish
```

## 📱 Mobile Support

The API is designed to work seamlessly with mobile applications, with features like:
- Token-based authentication
- Rate limiting
- Optimized payloads
- Offline support (coming soon)

## 🔄 API Versioning

The API follows semantic versioning (SemVer) and is versioned in the URL:

```
/api/v1/...  # Current stable version
```

## 📝 API Design Principles

1. **RESTful** - Follows REST principles
2. **Stateless** - Each request contains all necessary information
3. **Resource-Oriented** - Resources are represented as nouns
4. **Consistent** - Uniform interface across all endpoints
5. **Documented** - Self-documenting with OpenAPI

## 🛠️ Development Workflow

### Git Hooks

Pre-commit hooks are set up to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function signatures
- Keep functions small and focused
- Write docstrings for all public functions
- Use absolute imports

### Branch Naming

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical production fixes
- `chore/` - Maintenance tasks
- `docs/` - Documentation updates

## 🤖 CI/CD Pipeline

The CI/CD pipeline includes:

1. **Linting** - Check code style and formatting
2. **Type Checking** - Static type analysis with mypy
3. **Testing** - Run unit and integration tests
4. **Coverage** - Ensure test coverage meets requirements
5. **Security** - Dependency vulnerability scanning
6. **Deployment** - Automated deployment to staging/production

## 📚 Additional Documentation

### Database Schema

```mermaid
erDiagram
    USER ||--o{ LINK : creates
    USER ||--o{ DOMAIN : owns
    LINK }|--|| DOMAIN : belongs_to
    LINK ||--o{ CLICK : has
    
    USER {
        uuid id PK
        string email
        string hashed_password
        bool is_active
        datetime created_at
        datetime updated_at
    }
    
    DOMAIN {
        uuid id PK
        string name
        uuid user_id FK
        bool is_verified
    }
    
    LINK {
        uuid id PK
        string original_url
        string short_code
        uuid user_id FK
        uuid domain_id FK
        string title
        string description
        bool is_active
        datetime expires_at
        datetime created_at
    }
    
    CLICK {
        uuid id PK
        uuid link_id FK
        string ip_address
        string user_agent
        string referrer
        string country
        datetime created_at
    }
```

### Error Handling

The API returns consistent error responses:

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### Rate Limiting

Rate limiting is implemented using Redis:
- Default: 100 requests per minute per IP
- Authenticated users: 1000 requests per minute
- Adjustable via `RATE_LIMIT` environment variable

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

## 📄 License

This project is [MIT](LICENSE) licensed.

---

<div align="center">
  Made with ❤️ by Your Name • [Website](https://yourwebsite.com) • [Twitter](https://twitter.com/yourhandle)
</div>
