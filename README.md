# Anytype FastAPI Backend

A FastAPI-based backend service for interacting with Anytype. This is a Python port of the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype), providing RESTful API access to Anytype functionality.

## Prerequisites

- Python 3.8+
- Anytype installed and running locally

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

Once the application is running, you can access the interactive API documentation at:
- http://localhost:8000/docs

## Testing

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app
```

## MCP Server

This project includes an **MCP (Model Context Protocol) server** implementation that exposes Anytype API operations as MCP tools, enabling integration with MCP-compatible clients.

### Overview


### Configuration

The MCP server uses the following environment variables (can be set in `.env` file):

- `ANYTYPE_API_URL` — Base URL of the Anytype API (e.g., `http://localhost:31009`)
- `ANYTYPE_SESSION_TOKEN` — Session token for API access
- `ANYTYPE_APP_KEY` — Application key for authentication

Choose SSE type and http://localhost:8000/sse for endpoint

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
