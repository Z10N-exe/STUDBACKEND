# School Management System - API Documentation

## Base URL
```
http://localhost:8000/api
```

## Endpoints

### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

---

### 2. Create Student
```
POST /students
Content-Type: application/json
```

**Request:**
```json
{
  "full_name": "John Doe",
  "age": 15,
  "class": "10A",
  "gender": "Male"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "John Doe",
  "age": 15,
  "class": "10A",
  "gender": "Male",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Age must be between 4 and 25",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "abc-123-def"
  }
}
```

---

### 3. List All Students
```
GET /students
```

**Query Parameters:**
- `skip` - Number of records to skip (default: 0)
- `limit` - Maximum records to return (default: 100)
- `full_name` - Filter by name (partial match)
- `age` - Filter by exact age
- `class` - Filter by class
- `gender` - Filter by gender
- `sort_by` - Field to sort by (default: created_at)
- `sort_order` - asc or desc (default: desc)

**Examples:**

Get first 10 students:
```
GET /students?skip=0&limit=10
```

Get students in class 10A:
```
GET /students?class=10A
```

Get students sorted by age:
```
GET /students?sort_by=age&sort_order=asc
```

**Response (200 OK):**
```json
{
  "students": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "John Doe",
      "age": 15,
      "class": "10A",
      "gender": "Male",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

### 4. Get Student by ID
```
GET /students/{id}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "John Doe",
  "age": 15,
  "class": "10A",
  "gender": "Male",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Student not found",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "abc-123-def"
  }
}
```

---

### 5. Update Student (Full Update)
```
PUT /students/{id}
Content-Type: application/json
```

**Request:**
```json
{
  "full_name": "Jane Doe",
  "age": 16,
  "class": "10B",
  "gender": "Female"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Jane Doe",
  "age": 16,
  "class": "10B",
  "gender": "Female",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### 6. Update Student (Partial Update)
```
PATCH /students/{id}
Content-Type: application/json
```

**Request:**
```json
{
  "age": 16
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "John Doe",
  "age": 16,
  "class": "10A",
  "gender": "Male",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### 7. Delete Student
```
DELETE /students/{id}
```

**Response (200 OK):**
```json
{
  "message": "Student deleted successfully",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Validation Rules

| Field | Rules |
|-------|-------|
| full_name | Required, 1-100 characters |
| age | Required, integer 4-25 |
| class | Required, 1-20 characters |
| gender | Required, one of: Male, Female, Other |

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 500 | Internal Server Error |

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
