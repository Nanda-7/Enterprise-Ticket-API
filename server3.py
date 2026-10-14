from fastapi import FastAPI, Depends, HTTPException, Header, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import TicketDB
import os
import secrets
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer


load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
JWT_SECRET = os.getenv("JWT_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

if not CLIENT_ID or not CLIENT_SECRET or not JWT_SECRET:
    raise RuntimeError("Missing OAuth environment variables")

def verify_api_key(
    api_key: str | None = Header(default=None, alias="X-API-Key")
):
    expected_key = os.getenv("API_KEY")

    if (
        not expected_key
        or not api_key
        or not secrets.compare_digest(api_key, expected_key)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

#implementation of Oauth2.0 authentication
def verify_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
        )

        if payload.get("sub") != CLIENT_ID:
            raise HTTPException(
                status_code=401,
                detail="Invalid token subject"
            )

        return payload

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )

app = FastAPI(title="Enterprise Ticket API")


# Create database tables
Base.metadata.create_all(bind=engine)

class Ticket(BaseModel): 
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=5)
    priority: str = Field(pattern="^(Low|Medium|High)$")

# Provide a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/oauth/tickets")
def get_tickets_oauth(
    payload: dict = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    return {"tickets": db.query(TicketDB).all()}

@app.post("/token")
def create_token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="Invalid grant type")

    if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    payload = {
        "sub": client_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 1800
    }

@app.get("/")
def health_check():
    return {
        "message": "Enterprise Ticket API is running",
        "status": "healthy"
    }

#add tickets
@app.post("/tickets", dependencies=[Depends(verify_api_key)])
def create_ticket(ticket: Ticket, db: Session = Depends(get_db)):
    new_ticket = TicketDB(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority
    )

    try:
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        return {
            "message": "Ticket created successfully",
            "ticket": {
                "id": new_ticket.id,
                "title": new_ticket.title,
                "description": new_ticket.description,
                "priority": new_ticket.priority
            }
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create ticket"
        )

#retrieve all tickets
@app.get("/tickets", dependencies=[Depends(verify_api_key)])
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(TicketDB).all()
    return {"tickets": tickets}

#retrieve 1 ticket
@app.get("/tickets/{ticket_id}", dependencies=[Depends(verify_api_key)])
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket

#Update a ticket
@app.put("/tickets/{ticket_id}", dependencies=[Depends(verify_api_key)])
def update_ticket(
    ticket_id: int,
    ticket_data: Ticket,
    db: Session = Depends(get_db)
):
    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.title = ticket_data.title
    ticket.description = ticket_data.description
    ticket.priority = ticket_data.priority

    db.commit()
    db.refresh(ticket)

    return ticket

#Delete a ticket
@app.delete("/tickets/{ticket_id}", dependencies=[Depends(verify_api_key)])
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted successfully"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server3:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
