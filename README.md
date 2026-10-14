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
* `Client ID`: Identifies the application requesting access.
* `Client secret`: A confidential credential used to authenticate the client.
* `Access token`: A temporary credential used to access a protected endpoint.
* `JWT`: A signed token containing claims such as the subject (sub) and expiration (exp).
* `Bearer token`: A token presented in the Authorization header.
* `HS256`: The signing algorithm used for the JWT.
* `Token expiry`: The demo token expires after 30 minutes.



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

### 14. OAuth2 Client Credentials Flow
Implemented a simplified OAuth2 client-credentials-style flow for service-to-service authentication.
Token generation
The client sends a form-encoded POST request to /token containing:
grant_type=client_credentials
client_id
client_secret
The server validates the credentials and generates a signed JWT access token.
Access token usage
The client sends the token when requesting protected data:
headers = {
    "Authorization": f"Bearer {access_token}"
}
The server decodes and validates the token, checks its subject, and verifies its expiry before returning ticket data.

### 15. Python API Client — client.py
The client communicates with the FastAPI server using the requests library.
Client workflow
Loads configuration and credentials from .env.
Sends a POST request to /token.
Extracts the JWT access token from the response.
Sends an authenticated GET request to /oauth/tickets.
Receives ticket records in JSON format.
Sends the ticket data to the webhook receiver.
Saves execution details to output.json.

### 16. Webhook Integration
Implemented a webhook receiver using Python's built-in http.server module.
The client sends ticket data to the receiver running on port 9000.
How it works
The client sends a POST request containing JSON ticket data.
The receiver's do_POST() method handles the request.
Content-Length determines how many bytes to read from the request body.
json.loads() parses the incoming JSON.
The receiver returns an HTTP success response.
Key concepts
Webhook: A mechanism for sending data to another service when an event or action occurs.
HTTP POST: Sends data to the receiving service.
Request body: Contains the ticket payload.
Webhook receiver: An HTTP server that accepts and processes incoming requests.
JSON serialization: Converts Python data into a format suitable for transmission.

### 17. Error Handling, Timeouts and Retries
Added error handling to make client requests more resilient.
requests.exceptions.Timeout handles requests that take too long.
requests.exceptions.HTTPError handles unsuccessful HTTP responses after raise_for_status().
requests.exceptions.RequestException handles other request-related errors.
timeout=10 prevents the client from waiting indefinitely.
HTTPAdapter and Retry configure retries for selected transient server errors.
The retry strategy allows up to three retries for GET requests receiving status codes 500, 502, 503, or 504, with a backoff delay between attempts.
Retries are restricted to GET requests to avoid accidentally repeating operations that create or modify data.

### 18. Execution Logging — output.json
After a successful integration run, the client writes execution details to output.json.
Example:
{
    "timestamp": "2026-10-12T22:28:26.613799",
    "status": "success",
    "tickets_sent": 3
}
timestamp records when the execution was logged.
status records the outcome.
tickets_sent records the number of tickets included in the payload.
The log supports basic execution tracking and troubleshooting. It is overwritten on each successful run rather than maintaining a history.

### 19. Environment Variables and Secret Management
Credentials and configuration are stored in a local .env file and loaded using python-dotenv.
Example variable names:
API_KEY=your_api_key
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
JWT_SECRET=your_long_random_secret
These are placeholders; use your actual local values in .env.
The .gitignore file excludes .env, the virtual environment, Python cache files, and other local artifacts.
Never commit real API keys, client secrets, or JWT signing secrets to GitHub.


### 20. Project Architecture
Python Client (client.py)
        |
        | 1. Request access token
        v
FastAPI Server (server3.py)
        |
        | 2. Validate client credentials
        | 3. Generate JWT
        v
Python Client
        |
        | 4. GET /oauth/tickets
        |    Authorization: Bearer <token>
        v
FastAPI Server
        |
        | 5. Validate JWT
        | 6. Query database
        v
SQLite Database (tickets.db)
        |
        | 7. Return ticket data as JSON
        v
Python Client
        |
        | 8. POST ticket data
        v
Webhook Receiver (webhook_receiver.py)
        |
        | 9. Return success response
        v
Execution Log (output.json)
The project demonstrates API development, database access, authentication, service-to-service communication, webhook handling, and basic operational logging.

### 21. How to Run the Project
Prerequisites
Python installed
Project dependencies installed
.env configured with the required credentials
Terminal 1 — Start the FastAPI server
source venv/bin/activate
python server3.py
Terminal 2 — Start the webhook receiver
source venv/bin/activate
python webhook_receiver.py
Terminal 3 — Run the client
source venv/bin/activate
python client.py
Expected output
Access token received!
Tickets fetched successfully: ...
Tickets sent to webhook successfully!
Results saved to output.json
Swagger UI is available at:
http://127.0.0.1:8000/docs

### Skills Demonstrated
Python programming and virtual environments
REST API development with FastAPI
HTTP requests and JSON data exchange
Pydantic request validation
SQLAlchemy ORM and SQLite
CRUD operations and database sessions
API-key authentication
JWT access tokens and OAuth2 concepts
Webhook implementation and integration
Error handling, timeouts, and retries
Environment variables and secret management
Git and GitHub version control


