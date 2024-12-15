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

![Database scheme](./database_scheme.png)

## Set Up the Project

### 1. Prerequisites
- Python 3.10 or later
- PostgreSQL
- Docker & Docker Compose

### 2. Clone the Repository
```bash
git clone https://github.com/siaserb/airport-service.git
cd airport-service
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

---

### 1. **[Airplanes](http://localhost:8000/api/airport/airplanes/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access            |
|------------------------------|--------------------------------------------|------------------------------------------|-------------------|
| **GET**                     | `/api/airport/airplanes/`                 | Отримати список літаків                  | Authenticated users |
| **POST**                    | `/api/airport/airplanes/`                 | Додати новий літак                       | Admin only        |

---

### 2. **[Airplane Types](http://localhost:8000/api/airport/airplane-types/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access            |
|------------------------------|--------------------------------------------|------------------------------------------|-------------------|
| **GET**                     | `/api/airport/airplane-types/`            | Отримати список типів літаків            | Authenticated users |
| **POST**                    | `/api/airport/airplane-types/`            | Додати новий тип літака                  | Admin only        |
| **POST**                    | `/api/airport/airplane-types/{id}/upload-image/` | Завантажити зображення для типу літака   | Admin only        |

---

### 3. **[Airports](http://localhost:8000/api/airport/airports/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access            |
|------------------------------|--------------------------------------------|------------------------------------------|-------------------|
| **GET**                     | `/api/airport/airports/`                  | Отримати список аеропортів               | Authenticated users |
| **POST**                    | `/api/airport/airports/`                  | Додати новий аеропорт                    | Admin only        |
| **POST**                    | `/api/airport/airports/{id}/upload-image/` | Завантажити зображення для аеропорту     | Admin only        |

---

### 4. **[Crew](http://localhost:8000/api/airport/crew/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access            |
|------------------------------|--------------------------------------------|------------------------------------------|-------------------|
| **GET**                     | `/api/airport/crew/`                      | Отримати список членів екіпажу           | Authenticated users |
| **POST**                    | `/api/airport/crew/`                      | Додати нового члена екіпажу              | Admin only        |

---

### 5. **[Flights](http://localhost:8000/api/airport/flights/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access              |
|------------------------------|--------------------------------------------|------------------------------------------|---------------------|
| **GET**                     | `/api/airport/flights/`                   | Отримати список рейсів                   | Everyone            |
| **GET**                     | `/api/airport/flights/{id}/`              | Отримати детальну інформацію про рейс    | Everyone   |
| **POST**                    | `/api/airport/flights/`                   | Додати новий рейс                        | Admin only          |
| **PUT**                     | `/api/airport/flights/{id}/`              | Оновити дані рейсу                       | Admin only          |
| **PATCH**                   | `/api/airport/flights/{id}/`              | Частково оновити дані рейсу              | Admin only          |
| **DELETE**                  | `/api/airport/flights/{id}/`              | Видалити рейс                            | Admin only          |

---

### 6. **[Orders](http://localhost:8000/api/airport/orders/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access            |
|------------------------------|--------------------------------------------|------------------------------------------|-------------------|
| **GET**                     | `/api/airport/orders/`                    | Отримати список замовлень                | Authenticated users |
| **POST**                    | `/api/airport/orders/`                    | Додати нове замовлення                   | Authenticated users |

---

### 7. **[Routes](http://localhost:8000/api/airport/routes/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access            |
|------------------------------|--------------------------------------------|------------------------------------------|-------------------|
| **GET**                     | `/api/airport/routes/`                    | Отримати список маршрутів                | Authenticated users |
| **POST**                    | `/api/airport/routes/`                    | Додати новий маршрут                     | Admin only        |

---

### 8. **[User](http://localhost:8000/api/user/me/)**
| HTTP Method                  | Endpoint                                   | Description                              | Access            |
|------------------------------|--------------------------------------------|------------------------------------------|-------------------|
| **GET**                     | `/api/user/me/`                           | Отримати інформацію про поточного користувача | Authenticated users |
| **PUT**                     | `/api/user/me/`                           | Оновити дані поточного користувача       | Authenticated users |
| **PATCH**                   | `/api/user/me/`                           | Частково оновити дані користувача        | Authenticated users |
| **POST**                    | `/api/user/register/`                     | Зареєструвати нового користувача         | Public            |
| **POST**                    | `/api/user/token/`                        | Отримати токен доступу                   | Public            |
| **POST**                    | `/api/user/token/refresh/`                | Оновити токен доступу                    | Public            |
| **POST**                    | `/api/user/token/verify/`                 | Перевірити валідність токену             | Public            |

---