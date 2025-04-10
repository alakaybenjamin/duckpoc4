# Microservices Search Platform

A microservices-based search platform using Azure AI Search.

## Architecture

The platform is split into three microservices:

1. **Orchestrator Service**
   - Acts as API Gateway and coordinates workflows between services
   - Manages cross-service operations like search + history recording
   - Entry point for frontend applications

2. **Search Service**
   - Handles all search operations
   - Integrates with Azure AI Search
   - Provides abstraction over search providers

3. **User & History Service**
   - Manages user accounts
   - Records search history
   - Provides saved searches functionality

### Component Diagram

```
┌────────────────┐      ┌─────────────────┐
│                │      │                 │
│ Frontend App   │──────► Orchestrator    │
│                │      │ Service         │
└────────────────┘      └────────┬────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │                           │
           ┌───────▼──────┐           ┌────────▼─────────┐
           │              │           │                  │
           │ Search       │           │ User & History   │
           │ Service      │           │ Service          │
           │              │           │                  │
           └───────┬──────┘           └──────────────────┘
                   │                             │
           ┌───────▼──────┐           ┌──────────▼─────────┐
           │              │           │                    │
           │ Azure AI     │           │ SQLite Database    │
           │ Search       │           │                    │
           └──────────────┘           └────────────────────┘
```

## Technologies

- **FastAPI**: High-performance API framework
- **Azure AI Search**: Cloud search service
- **SQLAlchemy/Databases**: Database ORM
- **Docker**: Containerization
- **Pydantic**: Data validation and settings management

## Project Structure

Each microservice follows a clean, extensible architecture with proper separation of concerns:

```
service-name/
  ├── app/
  │    ├── __init__.py
  │    ├── api/
  │    │    ├── __init__.py
  │    │    └── routes.py
  │    ├── core/
  │    │    ├── __init__.py
  │    │    ├── config.py
  │    │    └── exceptions.py
  │    ├── services/
  │    │    ├── __init__.py
  │    │    └── service.py
  │    └── models/
  │         ├── __init__.py
  │         └── schemas.py
  ├── Dockerfile
  ├── requirements.txt
  └── main.py
```

## Running the Application

1. Set up your environment variables in `.env`:

```
SEARCH_SERVICE_ENDPOINT=https://your-search-service.search.windows.net
INDEX_NAME=hotels
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

2. Run with Docker Compose:

```bash
docker-compose up -d
```

## API Endpoints

### Orchestrator Service (http://localhost:5000)

- `POST /api/search`: Execute a search
- `POST /api/search/save`: Save a search
- `GET /api/history/{user_id}`: Get user's search history

### Search Service (http://localhost:5001)

- `POST /api/search`: Execute a search

### User & History Service (http://localhost:5002)

- `POST /api/users`: Create user
- `GET /api/users/{user_id}`: Get user
- `POST /api/history`: Record search
- `POST /api/history/save`: Save search
- `GET /api/history/user/{user_id}`: Get user's search history

## Common Issues & Solutions

### Database Connection Issues

1. **Can't connect to PostgreSQL**
   - Check if PostgreSQL is running: `pg_isready`
   - Verify database exists: `psql -l`
   - Ensure DATABASE_URL in .env is correct

2. **Permission Issues**
   - Check PostgreSQL user permissions: `psql -l`
   - If needed, grant permissions: `psql -c "GRANT ALL PRIVILEGES ON DATABASE biomed_search TO your_username;"`

### OAuth Configuration Issues

1. **redirect_uri_mismatch Error**
   - Verify the redirect URI in Google Cloud Console matches exactly:
     - Development: `http://localhost:5000/auth/callback`
     - Production: `https://your-domain.com/auth/callback`
   - Check that the OAUTH_* environment variables are correctly set
   - Ensure your Google OAuth credentials are properly configured

2. **Authentication Failed**
   - Check Google Cloud Console for error logs
   - Verify that the required scopes (openid, profile, email) are enabled
   - Ensure your OAuth application is properly configured and enabled

### Port Already in Use

If port 5000 is already in use:
1. Find the process: `lsof -i :5000`
2. Stop the process: `kill -9 <PID>`

## Support

For issues and questions, please create an issue in the repository or contact the development team.