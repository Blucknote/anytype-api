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
uv venv  # Creates a virtual environment in .venv directory
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
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


## MCP Server

This project includes an **MCP (Model Context Protocol) server** implementation that exposes Anytype API operations as MCP tools, enabling integration with MCP-compatible clients.


### Configuration

The MCP server uses the following environment variables (should be set in `.env` file):

- `ANYTYPE_API_URL` — Base URL of the Anytype API (e.g., `http://localhost:31009`)
- `ANYTYPE_API_KEY` — API key for authentication

### Obtaining API Key

You can obtain an API key using either of these methods:

#### Method 1: Using the Utility Script (Recommended)

Run the included utility script:
```bash
uv run get_api_key.py
```

This interactive script will guide you through the process of obtaining your API key.

#### Method 2: Manual Process

- Open Anytype it should be running in whole process and also should be launched whenever requests is expected
- run uv run uvicorn app.main:app --port 8081 (or other port)
- open http://localhost:8081/docs
- <img width="497" alt="image" src="https://github.com/user-attachments/assets/9e002297-d425-4a57-a916-dd1e1ac430db" />
- /auth/challenge will show display code and return challenge_id
- both of that goes to /auth/api_key which will return api_key
- <img width="588" alt="image" src="https://github.com/user-attachments/assets/a202caef-25e7-4bf7-994f-6854f3c11a0a" />
- paste "API Key" to `.env` file


### Running the MCP Server

You can run the MCP server directly:

```bash
uv run app/anytype_mcp_server.py
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

In target MCP client choose SSE type and http://localhost:8000/sse for endpoint

## License

MIT License

## Credits

Based on the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype).
