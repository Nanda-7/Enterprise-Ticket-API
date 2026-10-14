from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import TicketDB

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

@app.get("/")
def health_check():
    return {
        "message": "Enterprise Ticket API is running",
        "status": "healthy"
    }

#add tickets
@app.post("/tickets")
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
@app.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(TicketDB).all()
    return {"tickets": tickets}

#retrieve 1 ticket
@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketDB).filter(TicketDB.id == ticket_id).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket

#Update a ticket
@app.put("/tickets/{ticket_id}")
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
@app.delete("/tickets/{ticket_id}")
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
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


