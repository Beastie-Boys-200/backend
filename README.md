# Backend

Django REST Framework backend.

## Stack

- Django
- dj-rest-auth + django-allauth
- djangorestframework-simplejwt
- PostgreSQL
- Docker + docker-compose

## Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start containers
docker-compose up --build
```

## API Endpoints

### Authentication

- `POST /api/auth/registration/` - Register with email/password
  - Body: `{ email, first_name, last_name, password1, password2 }`
  - Returns: `{ access, refresh, user }`

- `POST /api/auth/login/` - Login with email/password
  - Body: `{ email, password }`
  - Returns: `{ access, refresh, user }`

- `POST /api/auth/google/` - Google OAuth2 login
  - Body: `{ code }` (authorization code from Google)
  - Returns: `{ access, refresh, user }`

- `POST /api/auth/logout/` - Logout (blacklist refresh token)
  - Headers: `Authorization: Bearer <access_token>`

- `GET /api/auth/user/` - Get current user info
  - Headers: `Authorization: Bearer <access_token>`
  - Returns: `{ pk, email, first_name, last_name }`

- `POST /api/auth/token/refresh/` - Refresh access token
  - Body: `{ refresh }`
  - Returns: `{ access, refresh }`

- `PATCH /api/auth/update-profile/` - Update user profile
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ first_name, last_name }`
  - Returns: `{ id, email, first_name, last_name, name, date_joined }`

- `POST /api/auth/change-password/` - Change password
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ old_password, new_password }`
  - Returns: `{ message: "Password updated successfully" }`

### Chat

**Conversations:**

- `GET /api/chat/conversations/` - List user's conversations
  - Headers: `Authorization: Bearer <access_token>`
  - Returns: Array of conversations

- `POST /api/chat/conversations/` - Create new conversation
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ title }` (optional)
  - Returns: Created conversation

- `GET /api/chat/conversations/{id}/` - Get conversation details
  - Headers: `Authorization: Bearer <access_token>`
  - Returns: Conversation with messages

- `PATCH /api/chat/conversations/{id}/` - Update conversation
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ title, archived }` (optional fields)

- `DELETE /api/chat/conversations/{id}/` - Delete conversation
  - Headers: `Authorization: Bearer <access_token>`

- `POST /api/chat/conversations/{id}/messages/` - Add message to conversation
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ role: "любая строка до 20 символов", content, metadata }` (metadata optional)
  - Note: role can be any string (user, assistant, system, tool, etc.)

**Messages:**

- `GET /api/chat/messages/` - List all user's messages
  - Headers: `Authorization: Bearer <access_token>`

- `GET /api/chat/messages/{id}/` - Get specific message
  - Headers: `Authorization: Bearer <access_token>`