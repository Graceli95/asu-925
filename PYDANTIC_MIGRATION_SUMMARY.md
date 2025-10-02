# Pydantic Migration Summary - Song Model

## Overview
Migrated the Song model from Python `dataclass` to Pydantic `BaseModel` to leverage Pydantic's best practices for validation, serialization, and integration with FastAPI.

---

## Key Changes

### 1. **Model Definition**
**Before (Dataclass):**
```python
from dataclasses import dataclass, field

@dataclass
class Song:
    title: str
    artist: str
    user: str
    genre: Optional[str] = None
    year: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
```

**After (Pydantic):**
```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

class Song(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    artist: str = Field(..., min_length=1, max_length=200)
    user: str = Field(..., min_length=1, max_length=100)
    genre: Optional[str] = Field(default=None, max_length=50)
    year: Optional[int] = Field(default=None, ge=1000, le=9999)
    created_at: datetime = Field(default_factory=datetime.now)
```

---

## Pydantic Best Practices Implemented

### ✅ 1. **Model Configuration (`ConfigDict`)**
```python
model_config = ConfigDict(
    arbitrary_types_allowed=True,      # Allow ObjectId
    populate_by_name=True,             # Allow field name or alias
    str_strip_whitespace=True,         # Auto-strip whitespace
    validate_assignment=True,          # Validate on assignment
    json_encoders={                    # Custom JSON encoders
        ObjectId: str,
        datetime: lambda v: v.isoformat()
    }
)
```

**Benefits:**
- Automatic validation on field assignment
- Custom JSON serialization for ObjectId and datetime
- Automatic whitespace stripping from strings

---

### ✅ 2. **Field Validation with `Field()`**
```python
title: str = Field(
    ...,                          # Required field
    min_length=1,                 # Minimum length
    max_length=200,               # Maximum length
    description="Song title",     # API docs description
    examples=["Bohemian Rhapsody"] # Example values
)

year: Optional[int] = Field(
    default=None,                 # Optional with default
    ge=1000,                      # Greater than or equal
    le=9999,                      # Less than or equal
    description="Release year",
    examples=[1975, 2024]
)
```

**Benefits:**
- Built-in validation (no manual checks needed)
- Automatic API documentation generation
- Clear constraints and examples

---

### ✅ 3. **Custom Field Validators**
```python
@field_validator('title', 'artist', 'user')
@classmethod
def validate_not_empty(cls, v: str) -> str:
    """Ensure required string fields are not empty or only whitespace"""
    if not v or not v.strip():
        raise ValueError('Field cannot be empty or only whitespace')
    return v.strip()

@field_validator('year')
@classmethod
def validate_year_not_future(cls, v: Optional[int]) -> Optional[int]:
    """Ensure year is not in the future"""
    if v is not None and v > datetime.now().year:
        raise ValueError(f'Year cannot be in the future')
    return v
```

**Benefits:**
- Custom business logic validation
- Automatic error messages
- Applied before data reaches the model

---

### ✅ 4. **Field Aliases**
```python
_id: Optional[ObjectId] = Field(
    default=None,
    alias="id",  # Use "id" in API, "_id" in code
    description="MongoDB ObjectId"
)
```

**Benefits:**
- Clean API responses (use `id` instead of `_id`)
- Maintain MongoDB compatibility internally
- Flexible serialization

---

### ✅ 5. **Type Safety and Auto-completion**
- Full IDE support with type hints
- Pydantic validates types automatically
- Better error messages for type mismatches

---

### ✅ 6. **Documentation Generation**
- Field descriptions appear in OpenAPI/Swagger docs
- Examples show up in interactive documentation
- Automatic JSON schema generation

---

## Method Changes

### Renamed: `update()` → `update_fields()`
**Reason:** Avoid conflicts with Pydantic's internal `update()` method

**Before:**
```python
song.update(title="New Title", year=2024)
```

**After:**
```python
song.update_fields(title="New Title", year=2024)
```

---

## Validation Examples

### Automatic Validation
```python
# ❌ This will raise ValidationError
song = Song(
    title="",           # Empty string not allowed
    artist="Queen",
    user="john"
)

# ❌ This will raise ValidationError
song = Song(
    title="Song",
    artist="Artist",
    user="john",
    year=2030           # Future year not allowed
)

# ✅ This is valid
song = Song(
    title="  Bohemian Rhapsody  ",  # Whitespace auto-stripped
    artist="Queen",
    user="john_doe",
    genre="Rock",
    year=1975
)
```

---

## Integration Benefits

### 1. **FastAPI Integration**
- Automatic request validation
- Automatic response serialization
- Automatic API documentation
- Built-in error handling

### 2. **Type Safety**
- Runtime type checking
- IDE auto-completion
- Mypy compatibility

### 3. **Data Consistency**
- Validation on creation
- Validation on assignment
- Consistent data format

### 4. **Developer Experience**
- Clear error messages
- Self-documenting code
- Reduced boilerplate

---

## Migration Checklist

- ✅ Convert from `@dataclass` to `BaseModel`
- ✅ Add `model_config` with appropriate settings
- ✅ Add `Field()` definitions with constraints
- ✅ Implement custom `@field_validator` methods
- ✅ Add field aliases where needed
- ✅ Rename conflicting methods (`update` → `update_fields`)
- ✅ Add descriptions and examples to fields
- ✅ Configure JSON encoders for special types
- ✅ Test validation behavior
- ✅ Verify no linter errors

---

## Next Steps

### Consider for User Model:
Apply the same Pydantic best practices to `src/model/user.py`:
- Convert to Pydantic BaseModel
- Add field validation
- Add email validation using `EmailStr`
- Add password field with validation
- Add custom validators for business logic

---

## Performance Notes

**Pydantic v2 Performance:**
- Written in Rust for ~5-50x faster validation
- Minimal overhead compared to dataclasses
- Efficient for high-throughput APIs

---

## Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI + Pydantic Best Practices](https://fastapi.tiangolo.com/tutorial/body/)
- [Pydantic Field Types](https://docs.pydantic.dev/latest/api/fields/)
- [Custom Validators](https://docs.pydantic.dev/latest/concepts/validators/)

