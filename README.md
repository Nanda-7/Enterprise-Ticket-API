# Enterprise Ticket API Integration System

## Project Overview

A Python-based ticket management API project designed to practise REST APIs, HTTP communication, authentication, and enterprise integrations.

The project uses **FastAPI** to build a demo ticket server. The goal is to progressively add ticket creation, retrieval, updates, authentication, and webhooks.


### Step 1: Project Setup

Created a Python project with a virtual environment and installed the required dependencies.

```bash
python3 cd enterprise-ticket-api
python3 -m venv venv
source venv/bin/activate
python3 -m pip install fastapi uvicorn requests python-dotenv
```

**Dependencies**

* `fastapi` — builds API endpoints.
* `uvicorn` — runs the FastAPI application as a web server.
* `requests` — sends HTTP requests from Python clients.
* `python-dotenv` — loads configuration and secrets from a `.env` file.
* `Pydantic` — Validates incoming request data
* `SQLAlchemy` — ORM used to interact with the database through Python
* `SQLite` — Database that permanently stores ticket records
* `HTTPException` - is a FastAPI class used to stop a request and return an HTTP error status code with a message.
* `TicketDB` - database model used to store tickets
* `os` - Provides functions to access environment variables, such as your API key
* `secrets` - Provides secure functions for comparing secret values
* `dotenv` - Imports the function that loads variables from your .env file



### Step 2: Build the FastAPI Server


### Step 3: Run the Server

```bash
uvicorn server:app --reload
```
or if uvicorn setup is done in the server code run

python3 server.py

**Command breakdown**

* `uvicorn` — starts the web server.
* `server` — the Python filename, without `.py`.
* `app` — the FastAPI application object inside `server.py`.
* `--reload` — automatically restarts the server when code changes during development.

### Step 4: Test Using Swagger UI

Open these URLs in a browser:

* `http://127.0.0.1:8000/` — calls the home endpoint.
* `http://127.0.0.1:8000/docs` — opens FastAPI's interactive Swagger UI.
* `http://127.0.0.1:8000/tickets` — returns the current empty ticket list.

Swagger UI lets us test endpoints without writing a separate frontend or API client.

## Theory and Concepts Learned

### 1. What is an API?

An API (Application Programming Interface) allows two software applications to communicate through defined rules.

In this project, the Python client will communicate with the ticket server through HTTP requests.

### 2. What is FastAPI?

FastAPI is a Python framework used to build APIs. It maps HTTP requests to Python functions and can automatically validate data and generate API documentation.

### 3. What is a REST API?

A REST-style API exposes resources through URLs and uses HTTP methods to perform operations.

Examples:

* `GET` — retrieve data.
* `POST` — create data.
* `PUT` — replace existing data.
* `PATCH` — partially update data.
* `DELETE` — delete data.

### 4. What is an Endpoint?

An endpoint is a URL and HTTP method combination that clients can call.

For example:

```python
@app.get("/tickets")
def get_tickets():
    return {"tickets": []}
```

Here, `GET /tickets` is the endpoint, and `get_tickets()` is the Python function executed when it is called.

### 5. What Does the Decorator Do?

`@app.get("/")` registers the function below it as the handler for HTTP GET requests to `/`.

The function name (`home`, `health_check`, etc.) can change without changing the URL, provided the route registration remains the same.

### 6. What is Uvicorn?

Uvicorn is the ASGI server that runs the FastAPI application and receives HTTP requests.

FastAPI defines how requests are handled; Uvicorn runs the application as a server.

### 7. What is Swagger UI?

Swagger UI is an interactive API documentation and testing interface. FastAPI generates it automatically from the application's routes and schemas.

It is a development tool, not the frontend of the ticketing application.

### 8. What is a Virtual Environment?

A virtual environment isolates a project's Python packages from other projects, reducing dependency conflicts.

Activate it before installing dependencies or running the project.

### 9. Pydantic Model — Request Validation

from pydantic import BaseModel

class Ticket(BaseModel):
    title: str
    description: str
    priority: str
A Pydantic model defines the expected structure of incoming API data.

### 10. Database Configuration — database.py

DATABASE_URL: Specifies the database location and type.
create_engine(): Creates the SQLAlchemy engine used to communicate with the database.
engine: Manages database connectivity.
sessionmaker(): Creates a factory for database sessions.
SessionLocal: Used to create sessions for database operations.
Base: Parent class for defining SQLAlchemy database models.
check_same_thread=False: SQLite setting commonly used with FastAPI to permit connections across threads.

### 11. SQLAlchemy Model — models.py

This model defines the structure of the tickets table in SQLite.

Ticket (Pydantic model) validates API request data.
TicketDB (SQLAlchemy model) represents database records.

### 12. Creating the Database Table
from database import engine, Base
from models import TicketDB

Base.metadata.create_all(bind=engine)
Base.metadata: Contains information about registered SQLAlchemy models and their tables.
create_all(): Creates tables that don't already exist.
bind=engine: Specifies which database engine to use.
The tickets.db file and its tickets table are created when the application initializes if they don't already exist.

### 13. Database Dependency — Depends

This function provides a database session to an API endpoint.

### We also queried it directly using Python's built-in SQLite library:
python3 -c "import sqlite3; c=sqlite3.connect('tickets.db'); print(c.execute('SELECT * FROM tickets').fetchall()); c.close()"



