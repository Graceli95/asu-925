# Test Suite Documentation

This directory contains the organized test suite for the Songs API application. The tests have been split into logical modules for better organization and maintainability.

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_database.py` - Database connection and setup tests
- `test_song_crud.py` - CRUD operations (Create, Read, Update, Delete) tests
- `test_search.py` - Song search functionality tests
- `test_user_isolation.py` - User isolation and data privacy tests
- `test_display.py` - Display utility function tests
- `test_service.py` - Service layer tests
- `test_file_handler.py` - File handling tests

## Running Tests

### Run All Tests
```bash
# From project root
python run_tests.py

# Or directly with pytest
python -m pytest test/ -v
```

### Run Specific Test Module
```bash
# From project root
python run_tests.py test_song_crud.py

# Or directly with pytest
python -m pytest test/test_song_crud.py -v
```

### Run Specific Test Class or Function
```bash
# Run specific test class
python -m pytest test/test_song_crud.py::TestSongCRUD -v

# Run specific test function
python -m pytest test/test_song_crud.py::TestSongCRUD::test_add_song_success -v
```

## Test Requirements

- MongoDB instance running (for database tests)
- All dependencies from `requirements-test.txt` installed
- Environment variables configured (see main README)

## Test Coverage

The test suite covers:
- Database connectivity and indexing
- Song CRUD operations
- Search functionality with case-insensitive matching
- User data isolation
- Display utility functions
- Service layer business logic
- File handling operations
- Error handling and edge cases

## API Testing

For API-specific tests, use the `test_api.py` script in the project root:

```bash
python test_api.py
```

This tests the FastAPI endpoints directly via HTTP requests.