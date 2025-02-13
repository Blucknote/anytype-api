# Anytype FastAPI Backend

A FastAPI-based backend service for interacting with Anytype. This is a Python port of the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype), providing RESTful API access to Anytype functionality.

## Features

- **Spaces Management**
  - List all available spaces
  - Get space members
- **Object Operations**
  - Create new objects
  - Search objects globally
  - Filter by object types
- **Type Management**
  - Get available types for spaces
- **Advanced Search**
  - Full-text search across spaces
  - Type filtering
  - Customizable sort order
  - Pagination support

## Prerequisites

- Python 3.8+
- Anytype installed and running locally
- Access to Anytype API (typically running on localhost:3333)

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
  ANYTYPE_API_URL=http://localhost:3333
  ANYTYPE_API_KEY=your_api_key_here  # if required
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

### Spaces
- `GET /spaces` - List all available spaces
- `GET /spaces/{space_id}/types` - Get available types for a space
- `GET /spaces/{space_id}/members` - Get members of a space

### Objects
- `POST /objects` - Create a new object
- `POST /search` - Search for objects with filtering and sorting

### Search Parameters
The search endpoint supports:
- Text query
- Type filtering
- Sorting options:
  - Created date
  - Last modified date
  - Last opened date
- Pagination (limit/offset)

## Project Structure
```
anytype-api/
├── app/
│   └── main.py          # Main application file
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
├── .gitignore
└── README.md
```

## Development Notes

### Models
- `SpaceInfo`: Space information including name, description, and icon
- `TypeInfo`: Object type information
- `ObjectInfo`: Detailed object information
- `CreateObjectRequest`: Schema for creating new objects
- `SearchRequest`: Schema for search queries

### API Client
The `AnytypeClient` class handles all communication with the Anytype API, including:
- Authentication
- Request formatting
- Error handling
- Response parsing

## License

MIT License

## Credits

Based on the [Raycast Anytype Extension](https://github.com/raycast/extensions/tree/main/extensions/anytype).