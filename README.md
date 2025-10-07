# Songs API - FastAPI Application

## Overview
A modern, layered RESTful API for managing songs with a MongoDB backend. This project demonstrates best practices in Python, FastAPI, Pydantic, and clean architecture.

---

## Features
- **RESTful API**: Full HTTP-based CRUD operations (GET, POST, PUT, DELETE)
- **User Tracking**: Each operation is associated with a specific user
- **Search Functionality**: Search songs by title or artist
- **User Statistics**: Analytics endpoint for user song collections
- **File Export**: Creates .txt files for each song in the assets folder
- **Interactive API Docs**: Swagger UI and ReDoc
- **Layered Architecture**: Clean separation between API, service, database, and model layers
- **Input Validation**: Pydantic schemas for request/response validation
- **CORS Enabled**: Ready for frontend integration

---

## Setup

### Prerequisites
- Python 3.8+
- MongoDB instance (local or Atlas)
- Virtual environment (recommended)

### Installation
1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with your MongoDB connection string:
   ```
   project_db_url=mongodb+srv://your-connection-string
   project_db_name=songs
   ```

### Running the API
Start the FastAPI server:
```bash
python main.py
```
Or using uvicorn directly:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

---

## API Usage

### Quick Start with cURL
- **Create a song:**
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
- **List songs for a user:**
  ```bash
  curl "http://localhost:8000/songs?user=john_doe"
  ```
- **Search songs:**
  ```bash
  curl "http://localhost:8000/songs/search?query=Bohemian&user=john_doe"
  ```
- **Update a song:**
  ```bash
  curl -X PUT "http://localhost:8000/songs/{song_id}?user=john_doe" \
    -H "Content-Type: application/json" \
    -d '{"year": 1976}'
  ```
- **Delete a song:**
  ```bash
  curl -X DELETE "http://localhost:8000/songs/{song_id}?user=john_doe"
  ```
- **Get user statistics:**
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

### Error Responses
- **400 Bad Request**
  ```json
  { "detail": "Title cannot be empty" }
  ```
- **404 Not Found**
  ```json
  { "detail": "Song not found or you don't have permission to access it" }
  ```

---

## Layered Architecture (n-Layered, RESTful)

This project uses a clean, n-layered architecture for maintainability and scalability:

```
API Layer (main.py, src/routers/) ← FastAPI endpoints
    ↓
Dependency Layer (src/dependencies.py) ← Dependency injection
    ↓
Service Layer (src/service/) ← Business Logic
    ↓
Database Layer (src/db/) ← Data access
    ↓
Model Layer (src/model/) ← Pydantic models/entities
    ↓
Schema Layer (src/schemas.py) ← Pydantic request/response schemas
```

- **API Layer:** Handles HTTP requests, validation, and routing.
- **Dependency Layer:** Provides singleton database/service instances to routers.
- **Service Layer:** Contains business logic and orchestration.
- **Database Layer:** Handles all direct database operations.
- **Model Layer:** Defines data structures and validation logic.
- **Schema Layer:** Defines request/response schemas for API endpoints.

---

## Field Aliasing (Flexible API Input)

The Song model supports field aliases for flexible API input. You can use either the primary field name or its alias when creating/updating songs.

| Field      | Primary Name | Alias         |
|------------|--------------|---------------|
| title      | `title`      | `song_title`  |
| artist     | `artist`     | `artist_name` |
| user       | `user`       | `username`    |
| genre      | `genre`      | `music_genre` |
| year       | `year`       | `release_year`|
| created_at | `created_at` | `date_created`|
| updated_at | `updated_at` | `date_updated`|
| id         | `id`         | `song_id`     |

**Example:**
```json
{
  "song_title": "Bohemian Rhapsody",
  "artist_name": "Queen",
  "username": "john_doe",
  "music_genre": "Rock",
  "release_year": 1975
}
```

---

## Pydantic & Validation Best Practices
- All models use Pydantic v2+ for validation and serialization
- Field constraints (min/max length, regex, etc.) are enforced
- Custom validators for business rules (e.g., year not in future)
- Field aliases for flexible input
- Automatic OpenAPI/Swagger documentation
- See `src/model/song.py` for implementation details

---

## Testing
To run the tests:
```bash
python run_tests.py
```

---

## Project Structure
```
├── main.py                   # FastAPI application entry point
├── start_api.py              # API server startup script
├── assets/                   # Exported song files (.txt format)
├── src/
│   ├── dependencies.py       # Dependency injection
│   ├── schemas.py            # Pydantic schemas for validation
│   ├── db/
│   │   └── songs_db.py       # Database layer
│   ├── model/
│   │   ├── __init__.py
│   │   ├── song.py           # Song model
│   │   └── user.py           # User model
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── songs.py          # Song routes
│   │   └── users.py          # User routes
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
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

---

## Contribution & Legacy Notes
- This project was migrated from a CLI-based application (`songs_cli.py`) to a modern FastAPI RESTful API.
- All legacy files are retained for reference but are no longer maintained.
- Please follow the layered architecture and naming conventions for all new code.

---

## License
MIT License
