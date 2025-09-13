# Task Manager API

A robust Django REST Framework API for task management with role-based access control and user authentication.

## Features

- **Custom User Authentication**: Email-based authentication with JWT tokens
- **Role-Based Access Control (RBAC)**: Admin and User roles with different permissions
- **Task Management**: Full CRUD operations for tasks
- **Comment System**: Users can comment on their assigned tasks
- **Soft Delete**: User deactivation that preserves data integrity
- **Filtering & Search**: Filter tasks by status/assignee, search by title/description
- **Pagination**: Built-in pagination for all list endpoints

## Technology Stack

- **Framework**: Django 5.2.6 + Django REST Framework 3.16.1
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (default) / PostgreSQL (production-ready)
- **Filtering**: django-filter
- **Python**: 3.12+

## Setup Instructions

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd task_manager
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "role": "User"
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Tasks

#### List Tasks
```http
GET /api/tasks/
Authorization: Bearer <access_token>

# Optional query parameters:
# ?status=ToDo&assigned_to=1&search=important&page=1
```

#### Create Task (Admin Only)
```http
POST /api/tasks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for the API",
  "status": "ToDo",
  "assigned_to_id": 2
}
```

#### Update Task
```http
PATCH /api/tasks/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "InProgress"
}
```

#### Delete Task (Admin Only)
```http
DELETE /api/tasks/1/
Authorization: Bearer <access_token>
```

### Comments

#### List Comments
```http
GET /api/comments/
Authorization: Bearer <access_token>

# Optional query parameters:
# ?task=1
```

#### Create Comment
```http
POST /api/comments/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "task": 1,
  "content": "This task is in progress"
}
```

### User Management (Admin Only)

#### List All Users
```http
GET /api/auth/users/
Authorization: Bearer <admin_access_token>
```

#### Soft Delete User
```http
PATCH /api/users/2/soft_delete/
Authorization: Bearer <admin_access_token>
```

## Permission Matrix

| Action | Admin | User |
|--------|-------|------|
| Register | ✅ | ✅ |
| Login | ✅ | ✅ |
| Create Task | ✅ | ❌ |
| View Tasks | All tasks | Only assigned tasks |
| Update Task | All tasks | Only assigned tasks |
| Delete Task | ✅ | ❌ |
| Create Comment | On any task | Only on assigned tasks |
| View Comments | All comments | Only on assigned tasks |
| List Users | ✅ | ❌ |
| Soft Delete User | ✅ | ❌ |

## Soft Delete Functionality

When a user is soft-deleted:

1. **Data Preservation**: All tasks assigned to the user and comments by the user remain in the database
2. **Login Prevention**: The user cannot obtain new JWT tokens
3. **API Access Denial**: Existing tokens become invalid due to `is_active=False` check
4. **Relationship Integrity**: All foreign key relationships remain intact

### Example Soft Delete

```http
PATCH /api/users/2/soft_delete/
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "message": "User user@example.com has been soft deleted"
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful GET, PATCH requests
- `201 Created` - Successful POST requests
- `204 No Content` - Successful DELETE requests
- `400 Bad Request` - Invalid data or soft-deleted user login
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found

## Testing

Run the test suite:

```bash
python manage.py test tests/
```

The tests cover:
- Authentication (including soft-deleted user login prevention)
- RBAC permissions
- Task access restrictions
- Comment permissions
- Data integrity after soft delete

## Development

### Running in Development Mode

```bash
python manage.py runserver
```

### Creating Sample Data

```python
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from tasks.models import Task, Comment

User = get_user_model()

# Create users
admin = User.objects.create_user('admin@example.com', 'Admin User', 'admin123', role='Admin')
user = User.objects.create_user('user@example.com', 'Regular User', 'user123', role='User')

# Create task
task = Task.objects.create(
    title='Sample Task',
    description='This is a sample task',
    assigned_to=user
)

# Create comment
Comment.objects.create(
    task=task,
    author=user,
    content='Working on this task'
)
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Validation**: Django's built-in password validators
- **RBAC**: Role-based access control prevents unauthorized actions
- **Soft Delete**: Data preservation while preventing access
- **Input Validation**: Comprehensive serializer validation

## Production Considerations

For production deployment:

1. **Environment Variables**: Use environment variables for `SECRET_KEY` and database credentials
2. **Database**: Switch to PostgreSQL
3. **HTTPS**: Enable SSL/TLS encryption
4. **CORS**: Configure CORS headers if needed for frontend
5. **Logging**: Implement comprehensive logging
6. **Monitoring**: Add health check endpoints

## Project Structure

```
task_manager/
├── manage.py
├── task_manager/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── tasks/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── urls.py
└── tests/
    └── test_api.py
```

## License

This project is licensed under the MIT License.