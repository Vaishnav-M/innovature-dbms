# Multi-Tenant Product Management API

A Django REST API for product management with multi-tenancy support. Each company's data is stored in a separate SQLite database for complete isolation.

## Features

- **Multi-Tenant Architecture**: Each company has its own isolated database
- **JWT Authentication**: Secure token-based authentication with company info embedded
- **RESTful API**: Full CRUD operations for products
- **Image Upload**: Support for multiple product images
- **Role-Based Access Control**: Admin, Manager, and User roles
- **Auto Database Routing**: Requests automatically routed to correct tenant database

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                            │
├─────────────────────────────────────────────────────────────┤
│              Tenant Middleware (JWT + DB Routing)           │
├─────────────────────────────────────────────────────────────┤
│                    Django REST APIs                         │
├──────────┬──────────┬──────────┬───────────────────────────┤
│ Default  │Company A │Company B │ Company N...              │
│   DB     │   DB     │   DB     │    DB                     │
│(Auth)    │(Products)│(Products)│ (Products)                │
└──────────┴──────────┴──────────┴───────────────────────────┘
```

## Quick Start

### 1. Create Virtual Environment

```bash
cd product_management
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings if needed
```

### 4. Run Migrations

```bash
python manage.py makemigrations authentication
python manage.py makemigrations products
python manage.py migrate
```

### 5. Seed Sample Data (Optional)

```bash
python scripts/seed_data.py
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The API is now available at `http://localhost:8000`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user (+ optional company) |
| POST | `/api/auth/login/` | Login and get JWT tokens |
| POST | `/api/auth/logout/` | Logout (blacklist refresh token) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/profile/` | Get current user profile |
| PUT | `/api/auth/profile/` | Update user profile |
| POST | `/api/auth/password/change/` | Change password |
| GET | `/api/auth/companies/` | List available companies |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| POST | `/api/products/` | Create new product |
| GET | `/api/products/{id}/` | Get product details |
| PUT | `/api/products/{id}/` | Update product |
| PATCH | `/api/products/{id}/` | Partial update product |
| DELETE | `/api/products/{id}/` | Delete product |
| GET | `/api/products/{id}/images/` | List product images |
| POST | `/api/products/{id}/images/` | Upload product images |
| PUT | `/api/products/images/{id}/` | Update image details |
| DELETE | `/api/products/images/{id}/` | Delete image |

## Usage Examples

### Register a New Company & User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@newcompany.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "New Company LLC"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@newcompany.com",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "refresh": "eyJ...",
    "access": "eyJ...",
    "user": {
      "id": "uuid",
      "email": "admin@newcompany.com",
      "company": {...}
    }
  }
}
```

### Create a Product (with Images)

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <access_token>" \
  -F "name=New Product" \
  -F "description=Product description" \
  -F "price=99.99" \
  -F "quantity=100" \
  -F "status=active" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

### List Products

```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <access_token>"
```

### Filter Products

```bash
# By status
curl -X GET "http://localhost:8000/api/products/?status=active" \
  -H "Authorization: Bearer <access_token>"

# Featured products
curl -X GET "http://localhost:8000/api/products/?featured=true" \
  -H "Authorization: Bearer <access_token>"

# Search by name
curl -X GET "http://localhost:8000/api/products/?search=keyboard" \
  -H "Authorization: Bearer <access_token>"
```

## Database Structure

### Default Database (Shared)
- `companies` - Company/tenant information
- `users` - User accounts with company associations
- Token blacklist tables

### Tenant Databases (Isolated per Company)
- `products` - Product catalog
- `product_images` - Product images

## Roles & Permissions

| Role | Products Read | Products Write |
|------|--------------|----------------|
| Admin | ✅ | ✅ |
| Manager | ✅ | ✅ |
| User | ✅ | ❌ |

## Project Structure

```
product_management/
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/
│   │   ├── db_router.py      # Multi-DB routing
│   │   ├── middleware.py     # Tenant middleware
│   │   ├── permissions.py    # Custom permissions
│   │   └── exceptions.py     # Error handling
│   ├── authentication/
│   │   ├── models.py         # Company, User
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── products/
│       ├── models.py         # Product, ProductImage
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── scripts/
│   ├── create_tenant_db.py   # Tenant DB management
│   └── seed_data.py          # Sample data
└── migrations/
    ├── default_db_migration.sql
    └── tenant_db_migration.sql
```

## Sample Test Credentials

After running `seed_data.py`:

| Company | Email | Password | Role |
|---------|-------|----------|------|
| Acme Corporation | admin@acmecorporation.com | admin123 | Admin |
| Acme Corporation | manager@acmecorporation.com | manager123 | Manager |
| Acme Corporation | user@acmecorporation.com | user123 | User |
| Tech Solutions Inc | admin@techsolutionsinc.com | admin123 | Admin |
| Django Admin | superadmin@productmanagement.local | superadmin123 | Superuser |

## License

MIT License
