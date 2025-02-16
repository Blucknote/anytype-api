# Anytype FastAPI Backend

A FastAPI-based backend service for interacting with Anytype. This is a Python port of the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype), providing RESTful API access to Anytype functionality.

## Features

- **Authentication**
  - Display code-based authentication
  - Bearer token authentication
  - Token validation and management
  - Session token handling
- **Spaces Management**
  - List all available spaces
  - Create new spaces
  - Get space members
- **Object Operations**
  - Create new objects
  - Get object details
  - Delete objects
  - Export objects (Markdown format)
- **Search Capabilities**
  - Space-specific search
  - Global search across all spaces
  - Advanced filtering and sorting
  - Pagination support
- **Type Management**
  - Get available types for spaces
  - Template management
  - System type handling

## Prerequisites

- Python 3.8+
- Anytype installed and running locally
- Access to Anytype API (typically running on localhost:31009)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd anytype-api
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
uv pip install -e .[dev]
```

## Running the Application

Development mode:
```bash
uvicorn app.main:app --reload
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app
```

## Project Structure
```
anytype-api/
├── app/
│   ├── main.py              # Main application file
│   ├── clients/             # API client implementations
│   ├── core/                # Core functionality
│   ├── helpers/             # Utility modules
│   └── routers/             # API endpoints
├── tests/                   # Test files
├── pyproject.toml          # Project configuration
└── README.md
```

## License

MIT License

## Credits

Based on the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype).
