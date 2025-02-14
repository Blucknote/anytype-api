# Anytype FastAPI Backend

A FastAPI-based backend service for interacting with Anytype. This is a Python port of the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype), providing RESTful API access to Anytype functionality.

## Features

- **Authentication**
  - Display code-based authentication
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

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the variables in `.env`:
  ```
  ANYTYPE_API_URL=http://localhost:31009/v1
  ANYTYPE_SESSION_TOKEN=your_session_token_here
  ANYTYPE_APP_KEY=your_app_key_here
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

## API Endpoints

### Authentication
- `POST /auth/display-code` - Get display code for authentication
- `POST /auth/token` - Get authentication token from display code
- `GET /auth/validate` - Validate authentication token

### Spaces
- `POST /space/create` - Create a new space
- `GET /space/list` - List all available spaces
- `GET /space/members` - Get members of a space

### Objects
- `POST /object/create` - Create a new object
- `GET /object/get/{space_id}/{object_id}` - Get object details
- `GET /object/list` - List objects with filtering
- `POST /object/delete` - Delete an object
- `POST /object/search` - Search objects in a space
- `POST /object/search/global` - Search across all spaces
- `POST /object/export/{space_id}/{object_id}` - Export object in specified format
- `GET /object/code/{space_id}/{object_id}` - Get display code for an object

### Types and Templates
- `GET /type/list` - Get available object types
- `GET /template/list` - Get available templates

## Project Structure
```
anytype-api/
├── app/
│   ├── main.py              # Main application file
│   └── helpers/
│       ├── __init__.py
│       ├── api.py           # API client and utilities
│       ├── constants.py     # System constants
│       ├── schemas.py       # Pydantic models
│       └── strings.py       # String formatting utilities
├── tests/
│   ├── conftest.py
│   ├── test_plan.md
│   └── unit/
│       └── helpers/
│           └── test_api.py
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
└── README.md
```

## Development Notes

### Models
- `SpaceDetails`: Space information including ID, name, and settings
- `ObjectDetails`: Detailed object information with metadata
- `TypeDetails`: Object type definitions and properties
- `TemplateDetails`: Template information and configuration
- `MemberDetails`: Space member information
- `SearchRequest`: Schema for space-specific search
- `GlobalSearchRequest`: Schema for cross-space search
- `ExportFormat`: Supported export formats (e.g., Markdown)

### API Client
The `AnytypeClient` class handles all communication with the Anytype API, including:
- Authentication and token management
- Request preparation and validation
- Error handling and response parsing
- Rate limiting and session management

### Helper Functions
- `format_object_name`: Sanitize and format object names
- `format_type_name`: Format type names according to system rules
- `format_source_link`: Process and validate source links
- `sanitize_query`: Clean and prepare search queries
- `validate_response`: Validate API responses

## Dependencies
- fastapi: Web framework for building APIs
- uvicorn: ASGI server implementation
- python-dotenv: Environment variable management
- httpx: HTTP client for async requests
- pydantic: Data validation using Python type annotations
- python-multipart: Multipart form data parsing

## License

MIT License

## Credits

Based on the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype).
