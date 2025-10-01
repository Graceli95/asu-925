# Songs API Application

A FastAPI-based REST API for managing songs with MongoDB backend. This application follows a layered architecture with service-based business logic for robust song management.

## Features

- **RESTful API**: Full CRUD operations via HTTP endpoints (GET, POST, PUT, DELETE)
- **User Tracking**: Each operation is associated with a specific user
- **Search Functionality**: Search songs by title or artist with case-insensitive matching
- **User Statistics**: View analytics about your song collection
- **File Export**: Automatically creates .txt files in the assets folder for each song (format: "Artist - Title.txt")
- **Interactive API Documentation**: Auto-generated Swagger UI and ReDoc documentation
- **Layered Architecture**: Clean separation between API, service, database, and model layers
- **Business Logic Validation**: Comprehensive input validation and error handling
- **CORS Support**: Cross-origin resource sharing enabled for web applications

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

3. **Run the Application**:
   ```bash
   python run_api.py
   ```

## Usage

### API Server

Start the FastAPI server:

```bash
python run_api.py
```

The API will be available at `http://localhost:8000` with the following endpoints:

### API Endpoints

#### Songs Management
- **POST** `/api/v1/songs` - Create a new song
- **GET** `/api/v1/songs` - List all songs (with optional user filter)
- **GET** `/api/v1/songs/{song_id}` - Get a specific song
- **PUT** `/api/v1/songs/{song_id}` - Update a song
- **DELETE** `/api/v1/songs/{song_id}` - Delete a song

#### Search and Play
- **GET** `/api/v1/songs/search` - Search songs by title or artist
- **POST** `/api/v1/songs/{song_id}/play` - Mark a song as played

#### Statistics
- **GET** `/api/v1/users/{username}/stats` - Get user statistics

#### System
- **GET** `/` - API information
- **GET** `/health` - Health check
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation (ReDoc)


### Example API Usage

#### Create a Song
```bash
curl -X POST "http://localhost:8000/api/v1/songs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "user": "john_doe",
    "genre": "Rock",
    "year": 1975
  }'
```

#### Get All Songs
```bash
curl "http://localhost:8000/api/v1/songs?user=john_doe"
```

#### Search Songs
```bash
curl "http://localhost:8000/api/v1/songs/search?q=queen&user=john_doe"
```

#### Update a Song
```bash
curl -X PUT "http://localhost:8000/api/v1/songs/{song_id}?user=john_doe" \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "Progressive Rock"
  }'
```

#### Delete a Song
```bash
curl -X DELETE "http://localhost:8000/api/v1/songs/{song_id}?user=john_doe"
```

### Interactive Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation where you can test endpoints directly
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation format
- **Health Check**: `http://localhost:8000/health` - Verify the API is running and database is connected

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
API Layer (main.py, api/router.py)
    ↓
Service Layer (service/song_service.py) ← Business Logic
    ↓
Database Layer (db/songs_db.py)
    ↓
Model Layer (model/song.py)
```

## Project Structure

```
├── main.py                   # FastAPI application entry point
├── run_api.py               # API server startup script
├── assets/                  # Exported song files (.txt format)
├── src/
│   ├── api/                 # API layer
│   │   ├── __init__.py
│   │   ├── router.py        # FastAPI routes
│   │   └── schemas.py       # Pydantic models
│   ├── service/             # Service layer (business logic)
│   │   ├── __init__.py
│   │   ├── song_service.py
│   │   └── file_handler.py
│   ├── db/                  # Database layer
│   │   └── songs_db.py
│   └── model/               # Data models
│       ├── __init__.py
│       └── song.py
├── test/                    # Test suite
│   ├── conftest.py          # Test fixtures
│   ├── test_database.py     # Database tests
│   ├── test_song_crud.py    # CRUD operation tests
│   ├── test_search.py       # Search functionality tests
│   ├── test_user_isolation.py # User isolation tests
│   ├── test_display.py      # Display function tests
│   ├── test_service.py      # Service layer tests
│   ├── run_tests.py         # Test runner
│   └── README.md            # Test documentation
├── requirements.txt         # Dependencies
├── requirements-test.txt    # Test dependencies
└── README.md                # This file
```

## Requirements

- Python 3.8+
- MongoDB server
- Dependencies listed in `requirements.txt`

## Environment Variables

Configure the following environment variables in a `.env` file:

- **`project_db_url`** (required): MongoDB connection string
  - Example: `mongodb://localhost:27017/songs`
- **`project_db_name`** (optional): Database name to use
  - Default: `songs`
  - Example: `my_songs_db`
- **`API_HOST`** (optional): API server host
  - Default: `0.0.0.0`
- **`API_PORT`** (optional): API server port
  - Default: `8000`
- **`API_RELOAD`** (optional): Enable auto-reload for development
  - Default: `true`
- **`API_LOG_LEVEL`** (optional): Logging level
  - Default: `info`

## Testing

The application includes comprehensive test coverage for all functionality.

### Running Tests

#### Unit Tests
```bash
# Run all unit tests
python run_tests.py

# Run with pytest
python -m pytest test/ -v

# Run specific test module
python -m pytest test/test_song_crud.py -v
```

#### API Tests
```bash
# Test FastAPI endpoints
python test_api.py
```

### Test Coverage

The test suite covers:
- Database connectivity and indexing
- Song CRUD operations
- Search functionality with case-insensitive matching
- User data isolation
- Service layer business logic
- File handling operations
- Error handling and edge cases
- API endpoint functionality

### Test Requirements

- MongoDB instance running (for database tests)
- All dependencies from `requirements-test.txt` installed
- Environment variables configured

For detailed test documentation, see `test/README.md`.

## Error Handling

The API includes comprehensive error handling for:
- Database connection issues
- Invalid song IDs
- Duplicate songs
- Missing required parameters
- Validation errors
- HTTP status codes (400, 404, 500, etc.)
- CORS issues
