# API Usage Guide

## Setup

### Start the Server
```bash
python -m uvicorn src.main:app --reload
```

Server runs at: `http://localhost:8000`

### Import Postman Collection
1. Open Postman
2. Click "Import"
3. Select `postman_collection.json`
4. Set variables:
   - `base_url`: http://localhost:8000
   - `student_id`: (will be populated after creating a student)

---

## cURL Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Student
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "age": 15,
    "class": "10A",
    "gender": "Male"
  }'
```

### List All Students
```bash
curl http://localhost:8000/api/students
```

### List with Pagination
```bash
curl "http://localhost:8000/api/students?skip=0&limit=10"
```

### Filter by Class
```bash
curl "http://localhost:8000/api/students?class=10A"
```

### Filter by Gender
```bash
curl "http://localhost:8000/api/students?gender=Male"
```

### Sort by Age (Ascending)
```bash
curl "http://localhost:8000/api/students?sort_by=age&sort_order=asc"
```

### Sort by Name (Descending)
```bash
curl "http://localhost:8000/api/students?sort_by=full_name&sort_order=desc"
```

### Get Student by ID
```bash
curl http://localhost:8000/api/students/550e8400-e29b-41d4-a716-446655440000
```

### Update Student (Full)
```bash
curl -X PUT http://localhost:8000/api/students/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "age": 16,
    "class": "10B",
    "gender": "Female"
  }'
```

### Update Student (Partial)
```bash
curl -X PATCH http://localhost:8000/api/students/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "age": 17
  }'
```

### Delete Student
```bash
curl -X DELETE http://localhost:8000/api/students/550e8400-e29b-41d4-a716-446655440000
```

---

## Interactive Documentation

### Swagger UI
Visit: http://localhost:8000/docs

Features:
- Try out endpoints directly
- See request/response schemas
- View parameter descriptions

### ReDoc
Visit: http://localhost:8000/redoc

Features:
- Beautiful API documentation
- Organized by tags
- Full schema information

---

## Common Workflows

### Create Multiple Students
```bash
# Student 1
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Alice Smith", "age": 14, "class": "9A", "gender": "Female"}'

# Student 2
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Bob Johnson", "age": 15, "class": "10A", "gender": "Male"}'

# Student 3
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Charlie Brown", "age": 16, "class": "10B", "gender": "Male"}'
```

### Get All Students in a Class
```bash
curl "http://localhost:8000/api/students?class=10A"
```

### Get Students by Gender
```bash
curl "http://localhost:8000/api/students?gender=Female"
```

### Get Youngest Students
```bash
curl "http://localhost:8000/api/students?sort_by=age&sort_order=asc&limit=5"
```

### Get Oldest Students
```bash
curl "http://localhost:8000/api/students?sort_by=age&sort_order=desc&limit=5"
```

### Update Multiple Fields
```bash
curl -X PATCH http://localhost:8000/api/students/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "age": 17,
    "class": "11A"
  }'
```

---

## Error Handling

### Validation Error
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John", "age": 30, "class": "10A", "gender": "Male"}'
```

Response:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Age must be between 4 and 25",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "abc-123"
  }
}
```

### Not Found Error
```bash
curl http://localhost:8000/api/students/invalid-id
```

Response:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Student not found",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "abc-123"
  }
}
```

### Duplicate Error
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Doe", "age": 15, "class": "10A", "gender": "Male"}'
```

(If student already exists)

Response:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Student with name 'John Doe' in class '10A' already exists",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "abc-123"
  }
}
```

---

## Tips

1. **Use Postman for easier testing** - Import the collection and use the UI
2. **Check Swagger UI** - Visit /docs for interactive documentation
3. **Save student IDs** - After creating a student, save the ID for later operations
4. **Test validation** - Try invalid data to see error messages
5. **Use filters** - Combine multiple query parameters for complex queries

---

## Response Headers

All responses include:
- `X-Request-ID` - Unique request identifier for tracing
- `Content-Type: application/json`

Example:
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```
