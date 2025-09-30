# Songs API - FastAPI Documentation

## Overview
A RESTful API for managing songs with MongoDB backend. This API provides CRUD operations for songs with user-based access control.

## Setup

### Prerequisites
- Python 3.8+
- MongoDB instance
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

## API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Create a Song
**POST** `/songs`

Create a new song.

**Request Body:**
```json
{
  "title": "Bohemian Rhapsody",
  "artist": "Queen",
  "user": "john_doe",
  "genre": "Rock",
  "year": 1975
}
```

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Bohemian Rhapsody",
  "artist": "Queen",
  "user": "john_doe",
  "genre": "Rock",
  "year": 1975,
  "created_at": "2025-09-30T12:00:00",
  "updated_at": null
}
```

### 2. List All Songs
**GET** `/songs?user={username}`

List all songs, optionally filtered by user.

**Query Parameters:**
- `user` (optional): Filter songs by username

**Response:** `200 OK`
```json
{
  "songs": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Bohemian Rhapsody",
      "artist": "Queen",
      "user": "john_doe",
      "genre": "Rock",
      "year": 1975,
      "created_at": "2025-09-30T12:00:00",
      "updated_at": null
    }
  ],
  "count": 1
}
```

### 3. Get a Specific Song
**GET** `/songs/{song_id}?user={username}`

Get a specific song by ID.

**Path Parameters:**
- `song_id`: The song's ID

**Query Parameters:**
- `user`: Username for authorization

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Bohemian Rhapsody",
  "artist": "Queen",
  "user": "john_doe",
  "genre": "Rock",
  "year": 1975,
  "created_at": "2025-09-30T12:00:00",
  "updated_at": null
}
```

### 4. Search Songs
**GET** `/songs/search?query={search_term}&user={username}`

Search songs by title or artist.

**Query Parameters:**
- `query`: Search term for title or artist
- `user` (optional): Filter by username

**Response:** `200 OK`
```json
{
  "results": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Bohemian Rhapsody",
      "artist": "Queen",
      "user": "john_doe",
      "genre": "Rock",
      "year": 1975,
      "created_at": "2025-09-30T12:00:00",
      "updated_at": null
    }
  ],
  "count": 1,
  "message": "Found 1 song(s) matching 'Bohemian'"
}
```

### 5. Update a Song
**PUT** `/songs/{song_id}?user={username}`

Update a song's details.

**Path Parameters:**
- `song_id`: The song's ID

**Query Parameters:**
- `user`: Username for authorization

**Request Body:**
```json
{
  "title": "Bohemian Rhapsody (Remastered)",
  "year": 2011
}
```

**Response:** `200 OK`
```json
{
  "message": "Song updated successfully",
  "success": true
}
```

### 6. Delete a Song
**DELETE** `/songs/{song_id}?user={username}`

Delete a song.

**Path Parameters:**
- `song_id`: The song's ID

**Query Parameters:**
- `user`: Username for authorization

**Response:** `200 OK`
```json
{
  "message": "Song 'Bohemian Rhapsody' by 'Queen' deleted successfully",
  "success": true
}
```

### 7. Play a Song
**POST** `/songs/{song_id}/play?user={username}`

Mark a song as played.

**Path Parameters:**
- `song_id`: The song's ID

**Query Parameters:**
- `user`: Username for authorization

**Response:** `200 OK`
```json
{
  "message": "Now playing: 'Bohemian Rhapsody' by 'Queen'",
  "success": true
}
```

### 8. Get User Statistics
**GET** `/users/{user}/stats`

Get statistics for a user's song collection.

**Path Parameters:**
- `user`: Username

**Response:** `200 OK`
```json
{
  "user": "john_doe",
  "total_songs": 10,
  "genres": {
    "Rock": 5,
    "Pop": 3,
    "Jazz": 2
  },
  "years": {
    "1975": 2,
    "1980": 3,
    "2000": 5
  },
  "artists": {
    "Queen": 3,
    "The Beatles": 4,
    "Miles Davis": 3
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Title cannot be empty"
}
```

### 404 Not Found
```json
{
  "detail": "Song not found or you don't have permission to access it"
}
```

## Features

- ✅ Full CRUD operations for songs
- ✅ User-based access control
- ✅ Search functionality by title or artist
- ✅ Statistics endpoint for user's song collection
- ✅ File system integration (creates .txt files for each song)
- ✅ Input validation with Pydantic
- ✅ MongoDB integration
- ✅ RESTful API design
- ✅ Interactive API documentation (Swagger/ReDoc)
- ✅ CORS enabled for frontend integration

## Testing

To run the tests:
```bash
python run_tests.py
```

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── db/
│   │   └── songs_db.py    # Database operations
│   ├── model/
│   │   ├── __init__.py
│   │   └── song.py        # Song model
│   ├── service/
│   │   ├── __init__.py
│   │   ├── song_service.py    # Business logic
│   │   └── file_handler.py    # File operations
│   └── schemas.py         # Pydantic schemas for validation
└── test/                  # Test files
```

## Migration from CLI

If you were previously using the CLI version (`songs_cli.py`), you can now use HTTP requests instead:

| CLI Command | API Endpoint |
|------------|--------------|
| `add` | POST `/songs` |
| `list` | GET `/songs?user={user}` |
| `search` | GET `/songs/search?query={query}&user={user}` |
| `play` | POST `/songs/{song_id}/play?user={user}` |
| `update` | PUT `/songs/{song_id}?user={user}` |
| `delete` | DELETE `/songs/{song_id}?user={user}` |
| `stats` | GET `/users/{user}/stats` |

## Example cURL Commands

### Create a song:
```bash
curl -X POST "http://localhost:8000/songs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Stairway to Heaven",
    "artist": "Led Zeppelin",
    "user": "john_doe",
    "genre": "Rock",
    "year": 1971
  }'
```

### List songs for a user:
```bash
curl "http://localhost:8000/songs?user=john_doe"
```

### Search songs:
```bash
curl "http://localhost:8000/songs/search?query=Stairway&user=john_doe"
```

### Update a song:
```bash
curl -X PUT "http://localhost:8000/songs/507f1f77bcf86cd799439011?user=john_doe" \
  -H "Content-Type: application/json" \
  -d '{
    "year": 1972
  }'
```

### Delete a song:
```bash
curl -X DELETE "http://localhost:8000/songs/507f1f77bcf86cd799439011?user=john_doe"
```
