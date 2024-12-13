# Airport Service

### Project Description

The **Airport Service API** is a RESTful service designed to manage airports, routes, flights, airplanes, and orders. It provides robust functionality for managing aviation-related operations, including user authentication and comprehensive API documentation. The system is containerized for ease of deployment and uses PostgreSQL as its database backend.

---

### Key Features

- **CRUD Operations**: Create, read, update, and delete entities such as airports, routes, flights, and orders.
- **JWT Authentication**: Secure access with token-based authentication.
- **Role-Based Access Control**: Differentiated access levels for administrators and regular users.
- **Image Upload**: Supports uploading images for airports and airplane types.
- **Filtering**: Query data based on parameters such as routes, airplane types, and crew.
- **Swagger Integration**: Detailed API documentation and testing interface.
- **Pagination**: Customizable pagination for efficient data retrieval.
- **Dockerized Deployment**: Simplified setup and scalability with Docker.
- **Sample Data Loading**: Populate the database with predefined data for testing.
- **Admin Panel**: Easy management of system resources through a web interface.


## Set Up the Project

### 1. Prerequisites
- Python 3.10 or later
- PostgreSQL
- Docker & Docker Compose

### 2. Clone the Repository
```bash
git clone <repository-url>
cd airport-management-system
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory with the following content (modify if necessary):
```dotenv
POSTGRES_PASSWORD=airport
POSTGRES_USER=airport
POSTGRES_DB=airport
POSTGRES_HOST=db
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data
```

### 4. Install Dependencies
If you are running the project locally (outside Docker), install the Python dependencies:
```bash
pip install -r requirements.txt
```

### 5. Start the Project
Use Docker Compose to build and start the services:
```bash
docker-compose up -d
```

### 6. Open a New Terminal Window and Access the Container

Check the running containers:
```bash
docker ps
```
Find the name of your application container (it should contain `airport` in its name). Then, execute the following command:
```bash
docker exec -it <airport_container_name> bash
```

### 7. Populate the Database with Sample Data
To test the project, you can load the database with sample data:
```bash
python manage.py loaddata data.json
```

### 8. Create a Superuser
To access admin functionality, create a superuser:
```bash
python manage.py createsuperuser
```

### 9. Access the Application

Open the following link in your browser:  
[http://127.0.0.1:8000/api/airport/flights/](http://127.0.0.1:8000/api/airport/flights/)

If everything is set up correctly, you should see a list of flights or an empty array if there are no flights in the database.

### 10. Authenticate as an Admin

Go to the login page:  
[http://localhost:8000/api/user/token/](http://localhost:8000/api/user/token/)  

Enter your superuser credentials and send the POST request. You will receive two tokens:
- **Access token** (valid for 15 minutes)
- **Refresh token** (valid for 7 days)

To use the API, include the access token in the `Authorization` header of your requests, with the prefix `Bearer`. Example:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5...
```

When the access token expires, you can refresh it at:  
[http://localhost:8000/api/user/token/refresh/](http://localhost:8000/api/user/token/refresh/)

Provide the refresh token to get a new access token.

### 11. Use Swagger Documentation for Better Navigation

Swagger provides an interactive interface for exploring and testing the API.  
Visit: [http://localhost:8000/api/doc/swagger/](http://localhost:8000/api/doc/swagger/)

You can log in directly through the Swagger interface using your superuser credentials.

---

### Notes:
1. Ensure that `docker-compose.yml` correctly maps the database and application containers as expected.
2. Verify that `data.json` exists in the project directory and contains valid sample data before running `loaddata`.
3. Double-check that the Docker container names and endpoints match your setup. Use `docker ps` to confirm container names.
4. Ensure that your environment variables are correctly configured in the `.env` file for Docker Compose.


## Available Methods and User Access for Entities

### 1. **Airport**
| HTTP Method | Description                              | Access            |
|-------------|------------------------------------------|-------------------|
| GET         | Retrieve a list of airports             | Authenticated users |
| POST        | Add a new airport                       | Admin only        |
| POST `/upload-image/` | Upload an image for an airport    | Admin only        |

---

### 2. **AirplaneType**
| HTTP Method | Description                              | Access            |
|-------------|------------------------------------------|-------------------|
| GET         | Retrieve a list of airplane types       | Authenticated users|
| POST        | Add a new airplane type                 | Admin only        |
| POST `/upload-image/` | Upload an image for an airplane type | Admin only        |

---

### 3. **Airplane**
| HTTP Method | Description                              | Access            |
|-------------|------------------------------------------|-------------------|
| GET         | Retrieve a list of airplanes            | Authenticated users |
| POST        | Add a new airplane                      | Admin only        |

**Filters:**
- `airplane_type`: Filter by airplane type (ID).
- `airplane_name`: Filter by airplane name.

---

### 4. **Route**
| HTTP Method | Description                              | Access            |
|-------------|------------------------------------------|-------------------|
| GET         | Retrieve a list of routes               | Authenticated users |
| POST        | Add a new route                         | Admin only        |

**Filters:**
- `source`: Filter by source (ID).
- `destination`: Filter by destination (ID).

---

### 5. **Crew**
| HTTP Method | Description                              | Access            |
|-------------|------------------------------------------|-------------------|
| GET         | Retrieve a list of crews                | Authenticated users |
| POST        | Add a new crew                          | Admin only        |

---

### 6. **Flight**
| HTTP Method | Description                              | Access            |
|-------------|------------------------------------------|-------------------|
| GET         | Retrieve a list of flights              | All users (read-only) |
| GET (detail)| Retrieve flight details                 | All users (read-only) |
| POST        | Add a new flight                        | Admin only        |

**Filters:**
- `route`: Filter by route (ID).
- `airplane`: Filter by airplane (ID).
- `date`: Filter by flight date.
- `crew`: Filter by crew (list of IDs).

---

### 7. **Order**
| HTTP Method | Description                              | Access            |
|-------------|------------------------------------------|-------------------|
| GET         | Retrieve a list of orders               | Authenticated users (own orders only) |
| POST        | Add a new order                         | Authenticated users |

