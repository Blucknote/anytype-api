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

## MCP Server

This project includes an **MCP (Model Context Protocol) server** implementation that exposes Anytype API operations as MCP tools, enabling integration with MCP-compatible clients.

### Features

- Create, retrieve, list, delete, and export objects
- Manage spaces and members
- Search within spaces or globally
- Manage object types and templates

#### Object Creation Tool

The MCP server exposes a `create_object` tool for creating new objects in Anytype.  
**Parameters:**
- `space_id` (str, required): ID of the space to create the object in.
- `name` (str, required): Name of the object.
- `object_type_unique_key` (str, required): Unique key of the object type.
- `template_id` (str, optional, default: `""`): Template ID to use for the object. Preferred to be `""` (empty string) if not using a template.
- `body` (str, optional): Markdown content for the object body. Supports markdown formatting.
- `description` (str, optional): Description of the object.
- `icon` (str, optional): Icon for the object.
- `source` (str, optional): Source for the object.

**Notes:**
- `template_id` should be set to `""` if you do not wish to use a template.
- The `body` field supports markdown content.

### Configuration

The MCP server uses the following environment variables (can be set in `.env` file):

- `ANYTYPE_API_URL` — Base URL of the Anytype API (e.g., `http://localhost:31009`)
- `ANYTYPE_SESSION_TOKEN` — Session token for API access
- `ANYTYPE_APP_KEY` — Application key for authentication

### Running the MCP Server

You can run the MCP server directly:

```bash
python app/anytype_mcp_server.py
```

or inside Docker (see below).

## Docker

You can build and run the application using Docker:

### Build the Docker image

```bash
docker build -t anytype-api .
```

### Run the Docker container

```bash
docker run --rm --env-file .env --network host anytype-api
```

This will start the API server with environment variables loaded from `.env` and network mode set to host.

## License

MIT License

## Credits

Based on the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype).
