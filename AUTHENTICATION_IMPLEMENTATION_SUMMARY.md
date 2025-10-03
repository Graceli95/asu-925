# JWT Authentication System Implementation Summary

## Overview

This document provides a comprehensive summary of the JWT authentication system implemented for the Songs API FastAPI application. The implementation includes secure password hashing, JWT token management with refresh token rotation, dependency-based route protection, HTTP-only cookie support for NextJS middleware, and a complete user management system with Swagger UI integration.

## Architecture Overview

### Layered Architecture

The authentication system follows a clean, layered architecture with a hybrid approach combining middleware for cross-cutting concerns and FastAPI dependencies for route-level authentication:

```
┌─────────────────────────────────────────────────────────────┐
│                    Middleware Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Request         │  │ CORS            │  │ OpenAPI     │ │
│  │ Logging         │  │ Security        │  │ Security    │ │
│  │ Middleware      │  │ Middleware      │  │ Configuration│ │
│  │                 │  │                 │  │             │ │
│  │ • Request/      │  │ • Security      │  │ • JWT       │ │
│  │   Response      │  │   Headers       │  │   Bearer    │ │
│  │   Logging       │  │ • XSS           │  │   Scheme    │ │
│  │ • Timing        │  │   Protection    │  │ • Swagger   │ │
│  │ • Audit Trail   │  │ • Content       │  │   UI        │ │
│  │                 │  │   Type Options  │  │   Integration│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Auth Router   │  │   Song Router   │  │ User Router │ │
│  │                 │  │                 │  │             │ │
│  │ • /auth/register│  │ • /songs/*      │  │ • /users/*  │ │
│  │ • /auth/login   │  │ • Protected     │  │ • Protected │ │
│  │ • /auth/me      │  │ • Dependency    │  │ • Dependency│ │
│  │ • /auth/logout  │  │   Auth          │  │   Auth      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dependency Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Auth            │  │ Database        │  │ Service     │ │
│  │ Dependencies    │  │ Dependencies    │  │ Dependencies│ │
│  │                 │  │                 │  │             │ │
│  │ • get_current_  │  │ • get_database  │  │ • get_song_ │ │
│  │   user          │  │ • Singleton     │  │   service   │ │
│  │ • HTTPBearer    │  │   Pattern       │  │ • Generator │ │
│  │ • Token         │  │                 │  │   Pattern   │ │
│  │   Validation    │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Auth Service    │  │ Song Service    │  │ User Service│ │
│  │                 │  │                 │  │             │ │
│  │ • Password      │  │ • Business      │  │ • User      │ │
│  │   Hashing       │  │   Logic         │  │   Management│ │
│  │ • Token         │  │ • Validation    │  │ • Stats     │ │
│  │   Creation      │  │ • CRUD          │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Songs Database  │  │ Users Database  │  │ MongoDB     │ │
│  │                 │  │                 │  │             │ │
│  │ • Song CRUD     │  │ • User CRUD     │  │ • Connection│ │
│  │ • Search        │  │ • Authentication│  │ • Indexes   │ │
│  │ • User          │  │ • Validation    │  │ • Queries   │ │
│  │   Filtering     │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Song Model      │  │ User Model      │  │ Schemas     │ │
│  │                 │  │                 │  │             │ │
│  │ • Pydantic      │  │ • Pydantic      │  │ • Request   │ │
│  │   BaseModel     │  │   BaseModel     │  │   Validation│ │
│  │ • Validation    │  │ • Password      │  │ • Response  │ │
│  │ • Serialization │  │   Hashing       │  │   Formatting│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Authentication Flow**

1. **Request arrives** → Middleware processes logging and security headers
2. **Route matching** → FastAPI routes to appropriate handler
3. **Dependency injection** → `get_current_user()` validates JWT token
4. **Route execution** → Handler receives authenticated user context
5. **Response processing** → Middleware adds security headers and logs response

## Components Implemented

### 1. Authentication Core (`src/auth.py`)

**Purpose**: Core authentication utilities and JWT token management

**Key Features**:
- JWT token creation and validation with versioning support
- Password hashing with bcrypt
- Token expiration management (access: 30min, refresh: 7 days)
- User authentication verification
- Refresh token rotation and invalidation
- Token version tracking for security

**Key Functions**:
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str
def verify_token(token: str) -> TokenData  # Now includes version validation
def authenticate_user(username: str, password: str, user) -> Union[bool, dict]
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData
async def get_current_user_from_request(request: Request) -> TokenData
```

### 2. Middleware System (`src/middleware.py`)

**Purpose**: Cross-cutting concerns including request logging and security headers. JWT authentication is handled via FastAPI dependencies for better Swagger UI integration.

**Components**:

#### Request Logging Middleware
- Logs all incoming requests and responses
- Tracks processing time for performance monitoring
- Provides comprehensive audit trail
- Records request method, path, and response status

#### CORS Security Middleware
- Adds essential security headers to all responses
- XSS protection via `X-XSS-Protection` header
- Content type validation via `X-Content-Type-Options`
- Frame options via `X-Frame-Options` to prevent clickjacking
- Referrer policy for privacy protection

**Note**: JWT Auth Middleware was removed in favor of FastAPI dependency injection for better compatibility with Swagger UI and more granular control over authentication.

### 3. User Model (`src/model/user.py`)

**Purpose**: User entity with Pydantic validation and password security

**Key Features**:
- Pydantic BaseModel with validation
- Password hashing with bcrypt
- Email validation
- Field aliases for flexible input
- Secure password storage (excluded from API responses)
- Refresh token version tracking for security

**Key Methods**:
```python
@staticmethod
def hash_password(password: str) -> str
def verify_password(self, password: str) -> bool
def to_dict(self) -> Dict[str, Any]
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'User'
```

**New Fields**:
- `refresh_token_version: int = 0` - Tracks token versions for rotation security

### 4. Authentication Schemas (`src/schemas.py`)

**Purpose**: Request/response validation for authentication operations

**Schemas**:
- `UserRegister`: User registration with password validation
- `UserLogin`: Login credentials
- `Token`: JWT token response (includes refresh_token)
- `TokenData`: JWT payload data (includes version for rotation)
- `RefreshTokenRequest`: Refresh token exchange request
- `UserResponse`: User data (excludes password)

**Updated Schemas**:
- `Token` now includes `refresh_token` field for response body
- `TokenData` now includes `version` field for token rotation

### 5. Authentication Router (`src/routers/auth_router.py`)

**Purpose**: Authentication endpoints

**Endpoints**:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (sets HTTP-only cookies + returns tokens)
- `POST /auth/login-form` - OAuth2 form login (Swagger UI compatible)
- `POST /auth/refresh` - Refresh access token with rotation
- `GET /auth/me` - Current user information
- `POST /auth/logout` - Logout confirmation

**New Features**:
- **Token Rotation**: Old refresh tokens are invalidated on each refresh
- **HTTP-only Cookies**: Set for NextJS middleware compatibility
- **Dual Response**: Tokens in response body (Swagger UI) + cookies (NextJS)
- **Version Tracking**: Refresh tokens include version for security

### 6. Database Integration (`src/db/song_db.py`)

**Purpose**: User data persistence

**User Operations**:
- `add_user(user: User) -> Optional[User]`
- `get_user_by_id(user_id: str) -> Optional[User]`
- `get_user_by_username(username: str) -> Optional[User]`
- `get_user_by_email(email: str) -> Optional[User]`
- `update_user(user: User) -> bool`
- `delete_user(user_id: str) -> bool`

**Token Version Management**:
- User model includes `refresh_token_version` field
- Version incremented on each token refresh
- Old tokens invalidated automatically

## Security Features

### 1. Password Security
- **bcrypt hashing**: Industry-standard password hashing
- **Password complexity**: 8+ characters, uppercase, lowercase, digit
- **Never store plain text**: Passwords are always hashed
- **Salt included**: bcrypt automatically includes salt

### 2. JWT Security
- **Configurable secret**: Environment variable for JWT secret
- **Token expiration**: Access tokens (30 minutes), Refresh tokens (7 days)
- **Algorithm specification**: HS256 algorithm
- **Token rotation**: Refresh tokens invalidated on each use
- **Version tracking**: Prevents token replay attacks
- **Secure storage**: HTTP-only cookies + response body for flexibility

### 3. Route Protection
- **Dependency-based**: FastAPI dependency injection for route-level authentication
- **Bearer token format**: Enforces proper Authorization header format via HTTPBearer
- **User context**: Authenticated user available as function parameter
- **Error handling**: Clear error messages for authentication failures
- **Swagger UI integration**: "Authorize" button for easy token testing
- **Token validation**: Version checking for refresh token security

### 4. Input Validation
- **Pydantic validation**: Strong typing and validation
- **Email validation**: Basic email format checking
- **Field sanitization**: Automatic whitespace trimming
- **SQL injection prevention**: Parameterized queries

### 5. Token Rotation Security
- **Single-use refresh tokens**: Each refresh invalidates the previous token
- **Version tracking**: Prevents token replay and reuse attacks
- **Automatic invalidation**: Old tokens become unusable immediately
- **Compromise protection**: Stolen tokens have limited window of use

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=songs_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secure-secret-key-here-32-chars-min
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=True
```

### Dependencies

The following packages were added to `requirements.txt`:

```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

## Usage Guide

### 1. User Registration

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response**:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null,
  "last_login": null,
  "is_active": true
}
```

### 2. User Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Note**: Tokens are also set as HTTP-only cookies for NextJS middleware compatibility.

### 3. Accessing Protected Routes

```bash
# Get current user info
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Create a song
curl -X POST "http://localhost:8000/songs" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "genre": "Rock",
    "year": 1975
  }'

# List songs
curl -X GET "http://localhost:8000/songs" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Token Refresh

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Security Note**: The old refresh token is automatically invalidated when a new one is issued.

### 5. How Authentication Works

The authentication system uses FastAPI dependency injection for route-level protection:

1. **Request arrives** → Middleware processes logging and security headers
2. **Route matching** → FastAPI routes to appropriate handler
3. **Dependency injection** → `get_current_user()` validates JWT token
4. **Token validation** → Extracts and validates `Authorization: Bearer <token>`
5. **User context** → Returns authenticated user data to route handler
6. **Route execution** → Handler receives user as function parameter
7. **Response processing** → Middleware adds security headers and logs response

### 6. Route Protection

Protected routes (require authentication via `Depends(get_current_user)`):
- `/songs/*` - All song operations
- `/users/*` - All user operations  
- `/auth/me` - Current user information

Public routes (no authentication required):
- `/` - Root endpoint
- `/docs`, `/redoc`, `/openapi.json` - API documentation
- `/auth/register`, `/auth/login`, `/auth/login-form` - Authentication endpoints

### 7. Swagger UI Integration

The FastAPI application includes OpenAPI security configuration:
- **Authorize button** appears in Swagger UI
- **Bearer token input** for JWT authentication
- **Automatic token inclusion** in protected endpoint requests
- **Token validation** happens via FastAPI dependency injection

## Best Practices Implemented

### 1. Security Best Practices
- **Never log passwords**: Passwords are excluded from logs and responses
- **Secure password hashing**: bcrypt with salt
- **Token expiration**: Short-lived access tokens (30 minutes), longer refresh tokens (7 days)
- **Token rotation**: Refresh tokens invalidated on each use
- **Version tracking**: Prevents token replay attacks
- **HTTP-only cookies**: XSS protection for NextJS middleware
- **Input validation**: Comprehensive validation on all inputs
- **Error handling**: Clear error messages without information leakage

### 2. Architecture Best Practices
- **Separation of concerns**: Clear layer separation
- **Dependency injection**: Loose coupling between components
- **Single responsibility**: Each component has a single purpose
- **Interface segregation**: Clean interfaces between layers

### 3. Code Quality Best Practices
- **Type hints**: Comprehensive type annotations
- **Documentation**: Detailed docstrings and comments
- **Error handling**: Proper exception handling
- **Validation**: Input validation at multiple levels

## Error Handling

### Authentication Errors

**Missing Authorization Header**:
```json
{
  "detail": "Authorization header missing",
  "error": "authentication_required"
}
```

**Invalid Token Format**:
```json
{
  "detail": "Invalid authorization header format. Expected 'Bearer <token>'",
  "error": "invalid_auth_format"
}
```

**Invalid/Expired Token**:
```json
{
  "detail": "Could not validate credentials",
  "error": "invalid_token"
}
```

### Validation Errors

**Password Requirements**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "input": "weak"
    }
  ]
}
```

## Testing

### Manual Testing

1. **Start the application**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Test registration**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "TestPass123"}'
   ```

3. **Test login**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "TestPass123"}'
   ```

4. **Test protected route**:
   ```bash
   curl -X GET "http://localhost:8000/songs" \
     -H "Authorization: Bearer <your-token>"
   ```

### Automated Testing

The system is designed to be easily testable with:
- Dependency injection for mocking
- Clear separation of concerns
- Comprehensive error handling
- Type hints for better IDE support

## Future Enhancements

### 1. Advanced Security
- **Refresh tokens**: Implement refresh token rotation
- **Rate limiting**: Add rate limiting for authentication endpoints
- **Account lockout**: Implement account lockout after failed attempts
- **Two-factor authentication**: Add 2FA support

### 2. User Management
- **Password reset**: Implement password reset functionality
- **Email verification**: Add email verification for new accounts
- **User roles**: Implement role-based access control
- **Profile management**: Add user profile update endpoints

### 3. Monitoring and Logging
- **Structured logging**: Implement structured logging with correlation IDs
- **Metrics**: Add authentication metrics and monitoring
- **Audit trail**: Enhanced audit trail for security events
- **Health checks**: Add health check endpoints

## Troubleshooting

### Common Issues

1. **"Could not validate credentials"**
   - Check if token is expired
   - Verify JWT_SECRET_KEY matches
   - Ensure token format is correct

2. **"Authorization header missing"**
   - Add Authorization header with Bearer token
   - Check if route requires authentication

3. **"Invalid email format"**
   - Ensure email contains @ and domain
   - Check for valid email structure

4. **"Password must be at least 8 characters long"**
   - Ensure password meets complexity requirements
   - Check for uppercase, lowercase, and digit

5. **"Refresh token has been revoked"**
   - Token was used after a new refresh token was issued
   - Get a new refresh token by logging in again
   - This is expected behavior for token rotation security

6. **"Invalid token type"**
   - Ensure you're using a refresh token for the refresh endpoint
   - Access tokens cannot be used for token refresh

### Debug Mode

Enable debug mode by setting `DEBUG=True` in environment variables for detailed error messages.

## Recent Changes and Improvements

### Migration from Middleware to Dependency-Based Authentication

**Problem**: The original JWT middleware was intercepting requests before FastAPI's dependency injection could process them, preventing Swagger UI from properly supplying JWT tokens to protected endpoints.

**Solution**: Migrated from middleware-based authentication to FastAPI dependency injection:

1. **Removed JWT Auth Middleware** from `main.py`
2. **Updated all protected routes** to use `current_user = Depends(get_current_user)`
3. **Maintained security** while improving Swagger UI compatibility
4. **Kept useful middleware** for logging and security headers

### Benefits of the New Approach

- **Swagger UI Integration**: "Authorize" button now works correctly
- **Better Error Handling**: More granular control over authentication errors
- **Improved Testing**: Easier to mock authentication in tests
- **Maintained Security**: Same JWT validation logic, better execution point
- **Stateless**: Still maintains RESTful stateless principles

### Files Modified

- `main.py`: Removed JWT middleware, kept logging and security middleware
- `src/routers/song_router.py`: Updated all endpoints to use `Depends(get_current_user)`
- `src/routers/auth_router.py`: Updated `/auth/me` endpoint, added refresh token endpoint
- `src/middleware.py`: JWT middleware code preserved but not used

### Token Rotation and Cookie Implementation

**Problem**: Need to support NextJS middleware while maintaining Swagger UI compatibility and implementing secure token rotation.

**Solution**: Implemented comprehensive token management:

1. **Added refresh token endpoint** (`POST /auth/refresh`) with token rotation
2. **Implemented HTTP-only cookies** for NextJS middleware compatibility
3. **Added token versioning** to prevent token replay attacks
4. **Updated all login endpoints** to set cookies and return tokens
5. **Enhanced security** with automatic token invalidation

### Benefits of Token Rotation

- **Enhanced Security**: Old refresh tokens are invalidated on each use
- **Replay Attack Prevention**: Version tracking prevents token reuse
- **Compromise Protection**: Stolen tokens have limited window of use
- **NextJS Compatibility**: HTTP-only cookies for middleware integration
- **Swagger UI Support**: Tokens still returned in response body

## Chat History Log

### User Messages During Implementation

1. **Initial Request**:
   ```
   I need you to create an auth middleware for this application that leverages JWTs and a secret from the .env "secret_key". Please also in the chat generate me a secret key that would be secure. Also, make sure for user auth their passwords are infact being hashed for security. Please make sure to reference best practices when implementating this authentication pattern
   ```

2. **Middleware Clarification**:
   ```
   good but where is the middleware that handles checking requests for the JWT being provided?
   ```

3. **Summary Request**:
   ```
   great, finally I'ld like you to generate a summary markdown file of everything you just implemented, the architecture behind it all, any useful knowledge, how to utilize it and protect routes, finally I want you to include a log of each message I sent in regards to this implementation
   ```

4. **Architecture Question**:
   ```
   doesn't the middleware technically come before the application layer?
   ```

5. **Dependency Issue**:
   ```
   ModuleNotFoundError: No module named 'passlib'
   ```

6. **Swagger UI Issue**:
   ```
   Why can't I add my JWT token in the swagger docs so I can verify who I am to make a request? otherwise everything is coming back as unauthorized
   ```

7. **Swagger UI Fix Request**:
   ```
   Let's add the Authorize Button to swagger please
   ```

8. **Token Supply Issue**:
   ```
   Authorize button has been added but the token isn't being supplied to the endpoints requiring the token
   ```

9. **Final Clarification**:
   ```
   Is there any point to this file then if we've removed from main? also don't I want a middleware anyway? isn't there security risks? also are we storing a session on the middleware by knowing who's logged in therefore breaking RESTful's stateless principle?
   ```

10. **Documentation Update Request**:
    ```
    fantastic, can you make the updates necessary to this file based on the changes we had to do to get the auth operational and include any details for each of the sections necessary
    ```

11. **NextJS Middleware Question**:
    ```
    should a JWT token be supplied in the response body or header information or some other means back to the user when they login?
    ```

12. **NextJS Middleware Implementation**:
    ```
    what if we plan to have a middleware in NextJS that intercepts all outgoing HTTP requests to our backend server to append the token to the endpoints requiring authorization?
    ```

13. **Token Rotation Security**:
    ```
    should a refresh_token invalidate the old jwt token associated with it?
    ```

14. **Token Rotation Implementation**:
    ```
    let's go option 1
    ```

15. **Final Documentation Update**:
    ```
    fantastic, now otherwise update this file like you've done in the past to make sure to include any relevant information to each section as it relates to all the changes for auth
    ```

## Conclusion

The JWT authentication system provides a robust, secure, and scalable foundation for the Songs API. It follows industry best practices for security, implements proper separation of concerns, and provides comprehensive error handling. The dependency-based authentication approach ensures consistent authentication across all protected routes while maintaining flexibility for future enhancements and full compatibility with Swagger UI.

The hybrid approach combining middleware for cross-cutting concerns (logging, security headers) with FastAPI dependencies for route-level authentication provides the best of both worlds: comprehensive security coverage and excellent developer experience.

### Key Security Enhancements

The implementation now includes advanced security features:

- **Token Rotation**: Refresh tokens are automatically invalidated on each use, preventing replay attacks
- **Version Tracking**: Token versioning ensures only the most recent refresh token is valid
- **HTTP-only Cookies**: Secure token storage for NextJS middleware integration
- **Dual Response Format**: Tokens in response body (Swagger UI) and cookies (NextJS)
- **Comprehensive Error Handling**: Clear error messages for all authentication scenarios

### Production Readiness

The system is production-ready with:
- Secure password hashing (bcrypt)
- JWT token management with rotation
- CORS and security headers
- Request logging and monitoring
- Comprehensive input validation
- Error handling and troubleshooting guides

The system can be easily extended with additional security features, user management capabilities, and monitoring tools as needed.
