# Songs CLI CRUD Application

A Python command-line interface for managing songs with MongoDB backend. This application follows a layered architecture with service-based business logic for robust song management.

## Features

- **CRUD Operations**: Create, Read, Update, Delete songs
- **User Tracking**: Each operation is associated with a specific user
- **Search Functionality**: Search songs by title or artist with case-insensitive matching
- **User Statistics**: View analytics about your song collection
- **File Export**: Automatically creates .txt files in the assets folder for each song (format: "Artist - Title.txt")
- **Rich CLI Interface**: Beautiful command-line interface with tables and colors
- **Layered Architecture**: Clean separation between CLI, service, database, and model layers
- **Business Logic Validation**: Comprehensive input validation and error handling

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
   python songs_cli.py
   ```

## Usage

### Interactive Menu Interface

The application uses an interactive menu-driven interface. Simply run the main script:

```bash
python songs_cli.py
```

You'll be prompted to enter your username, then presented with a menu of options:

```
Available Commands:
1. add - Add a new song
2. list - List all songs
3. search - Search songs
4. play - Mark a song as played
5. update - Update a song
6. delete - Delete a song
7. stats - Show user statistics
8. quit - Exit the application
```


### Menu-Driven Operations

**1. Add Song**: Prompts for title, artist, genre (optional), and year (optional)
**2. List Songs**: Shows all songs for the current user
**3. Search Songs**: Prompts for search query with option to search across all users
**4. Play Song**: Prompts for song ID to mark as played
**5. Update Song**: Prompts for song ID, then allows editing of title, artist, genre, and year
**6. Delete Song**: Prompts for song ID with confirmation before deletion
**7. Stats**: Shows user statistics including top genres, artists, and years
**8. Quit**: Exit the application

### Example Session

```
$ python songs_cli.py
🎵 Songs CLI CRUD Application
Enter your username: Ted
Welcome, Ted!

Available Commands:
1. add - Add a new song
2. list - List all songs
3. search - Search songs
4. play - Mark a song as played
5. update - Update a song
6. delete - Delete a song
7. stats - Show user statistics
8. quit - Exit the application

Enter your choice [1/2/3/4/5/6/7/8]: 1
Enter song title: Bohemian Rhapsody
Enter artist name: Queen
Enter genre (optional): Rock
Enter year (optional): 1975
✓ Song 'Bohemian Rhapsody' by 'Queen' added successfully

Enter your choice [1/2/3/4/5/6/7/8]: 8
Goodbye!
```

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
CLI Layer (songs_cli.py)
    ↓
CLI Commands (songs_cli_commands.py)
    ↓
Service Layer (service/song_service.py) ← Business Logic
    ↓
Database Layer (db/songs_db.py)
    ↓
Model Layer (model/song.py)
```

## Project Structure

```
├── songs_cli.py              # Main CLI application (interactive menu)
├── assets/                   # Exported song files (.txt format)
├── service/                  # Service layer (business logic)
│   ├── __init__.py
│   └── song_service.py
├── db/                       # Database layer
│   └── songs_db.py
├── model/                    # Data models
│   ├── __init__.py
│   └── song.py
├── test/                     # Test suite
│   ├── conftest.py           # Test fixtures
│   ├── test_database.py      # Database tests
│   ├── test_song_crud.py     # CRUD operation tests
│   ├── test_search.py        # Search functionality tests
│   ├── test_user_isolation.py # User isolation tests
│   ├── test_display.py       # Display function tests
│   ├── test_service.py       # Service layer tests
│   ├── run_tests.py          # Test runner
│   └── README.md             # Test documentation
├── requirements.txt          # Dependencies
├── requirements-test.txt     # Test dependencies
└── README.md                 # This file
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
