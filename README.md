# Songs API - FastAPI Application

A RESTful API for managing songs with MongoDB backend. This application follows a layered architecture with service-based business logic for robust song management.

> **Note**: This application has been migrated from CLI to FastAPI. For CLI documentation, see the legacy `songs_cli.py` file.

## Features

- **RESTful API**: Full HTTP-based CRUD operations (GET, POST, PUT, DELETE)
- **CRUD Operations**: Create, Read, Update, Delete songs
- **User Tracking**: Each operation is associated with a specific user
- **Search Functionality**: Search songs by title or artist with case-insensitive matching
- **User Statistics**: View analytics about your song collection via API endpoint
- **File Export**: Automatically creates .txt files in the assets folder for each song (format: "Artist - Title.txt")
- **Interactive API Docs**: Built-in Swagger UI and ReDoc documentation
- **Layered Architecture**: Clean separation between API, service, database, and model layers
- **Input Validation**: Pydantic schemas for request/response validation
- **CORS Enabled**: Ready for frontend integration

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create a `.env` file in the project root with your MongoDB configuration:
   ```
   project_db_url=mongodb://localhost:27017/songs
   project_db_name=songs
   ```

3. **Run the API Server**:
   ```bash
   python start_api.py
   ```
   
   Or directly with uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API**:
   - API Base URL: `http://localhost:8000`
   - Interactive Docs (Swagger): `http://localhost:8000/docs`
   - Alternative Docs (ReDoc): `http://localhost:8000/redoc`

## API Usage

### Quick Start with cURL

**Create a song:**
```bash
curl -X POST "http://localhost:8000/songs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "user": "john_doe",
    "genre": "Rock",
    "year": 1975
  }'
```

**List songs for a user:**
```bash
curl "http://localhost:8000/songs?user=john_doe"
```

**Search songs:**
```bash
curl "http://localhost:8000/songs/search?query=Bohemian&user=john_doe"
```

**Update a song:**
```bash
curl -X PUT "http://localhost:8000/songs/{song_id}?user=john_doe" \
  -H "Content-Type: application/json" \
  -d '{"year": 1976}'
```

**Delete a song:**
```bash
curl -X DELETE "http://localhost:8000/songs/{song_id}?user=john_doe"
```

**Get user statistics:**
```bash
curl "http://localhost:8000/users/john_doe/stats"
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| POST | `/songs` | Create a new song |
| GET | `/songs` | List all songs (optional user filter) |
| GET | `/songs/search` | Search songs by title/artist |
| GET | `/songs/{song_id}` | Get a specific song |
| PUT | `/songs/{song_id}` | Update a song |
| DELETE | `/songs/{song_id}` | Delete a song |
| POST | `/songs/{song_id}/play` | Mark song as played |
| GET | `/users/{user}/stats` | Get user statistics |

For detailed API documentation with request/response schemas, visit `http://localhost:8000/docs` after starting the server.

## Database Schema

**Database Name**: Configurable via `project_db_name` environment variable (default: `songs`)

### Songs Collection
- `_id`: MongoDB ObjectId
- `title`: Song title
- `artist`: Artist name
- `user`: Username who added the song
- `genre`: Song genre (optional)
- `year`: Release year (optional)
- `created_at`: Timestamp when song was added
- `updated_at`: Timestamp when song was last updated

## Business Rules

### Song Validation
- **Title**: Required, cannot be empty
- **Artist**: Required, cannot be empty
- **Genre**: Optional, any string value
- **Year**: Optional, must not be in the future (any year ≤ current year is valid)

### User Data Isolation
- Users can only view, modify, and delete their own songs
- Search operations are user-scoped by default (with option for global search)

## Environment Variables

The application uses the following environment variables:

- **`project_db_url`** (required): MongoDB connection string
  - Example: `mongodb://localhost:27017/songs`
- **`project_db_name`** (optional): Database name to use
  - Default: `songs`
  - Example: `my_songs_db`

## Architecture

The application follows a clean layered architecture:

```
API Layer (main.py) ← FastAPI endpoints
    ↓
Schemas Layer (src/schemas.py) ← Pydantic validation
    ↓
Service Layer (src/service/song_service.py) ← Business Logic
    ↓
Database Layer (src/db/songs_db.py)
    ↓
Model Layer (src/model/song.py)
```

## Project Structure

```
├── main.py                   # FastAPI application entry point
├── start_api.py              # API server startup script
├── API_README.md             # Detailed API documentation
├── assets/                   # Exported song files (.txt format)
├── src/
│   ├── schemas.py            # Pydantic schemas for validation
│   ├── db/
│   │   └── songs_db.py       # Database layer
│   ├── model/
│   │   ├── __init__.py
│   │   └── song.py           # Song model
│   └── service/
│       ├── __init__.py
│       ├── song_service.py   # Business logic
│       └── file_handler.py   # File operations
├── test/                     # Test suite
│   ├── conftest.py           # Test fixtures
│   ├── test_database.py      # Database tests
│   ├── test_song_crud.py     # CRUD operation tests
│   ├── test_search.py        # Search functionality tests
│   ├── test_user_isolation.py # User isolation tests
│   ├── test_display.py       # Display function tests
│   ├── test_service.py       # Service layer tests
│   └── README.md             # Test documentation
├── requirements.txt          # Dependencies
├── requirements-test.txt     # Test dependencies
└── README.md                 # This file

Legacy Files (deprecated):
├── songs_cli.py              # Old CLI application
```

## Requirements

- Python 3.7+
- MongoDB server
- Dependencies listed in `requirements.txt`

## Error Handling

The application includes comprehensive error handling for:
- Database connection issues
- Invalid song IDs
- Duplicate songs
- Missing required parameters
- User confirmation for destructive operations
