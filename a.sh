#!/bin/bash

echo "Creating microservice files..."

# 1. User Service
cat > user_service.py <<EOF
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    id: Optional[int] = None
    name: str
    email: str

    class Config:
        orm_mode = True

@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user

@app.get("/users/", response_model=List[UserCreate])
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    return users
EOF

# 2. Flight Service
cat > flight_service.py <<EOF
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()
DATABASE_URL = "sqlite:///./flights.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Flight(Base):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String, unique=True)
    origin = Column(String)
    destination = Column(String)
    available_tickets = Column(Integer)

Base.metadata.create_all(bind=engine)

class FlightCreate(BaseModel):
    id: Optional[int] = None
    flight_number: str
    origin: str
    destination: str
    available_tickets: int

    class Config:
        orm_mode = True

@app.post("/flights/", response_model=FlightCreate)
def create_flight(flight: FlightCreate):
    db = SessionLocal()
    db_flight = Flight(**flight.dict())
    db.add(db_flight)
    db.commit()
    return flight

@app.get("/flights/", response_model=List[FlightCreate])
def get_flights():
    db = SessionLocal()
    return db.query(Flight).all()
EOF

# 3. Booking Service
cat > booking_service.py <<EOF
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
from .models import BookingDB, User, Flight
from .database import SessionLocal

app = FastAPI()

class Booking(BaseModel):
    user_id: int
    flight_id: int

    class Config:
        orm_mode = True

@app.post("/book/")
def book_flight(booking: Booking):
    db = SessionLocal()

    # Check if the user exists in the database
    user = db.query(User).get(booking.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the flight exists and has available tickets
    flight = db.query(Flight).get(booking.flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    if flight.available_tickets < 1:
        raise HTTPException(status_code=400, detail="Not enough available tickets")

    # Store the booking in the database
    db_booking = BookingDB(user_id=booking.user_id, flight_id=booking.flight_id)
    db.add(db_booking)
    db.commit()

    # Update the available tickets for the flight
    flight.available_tickets -= 1
    db.commit()

    return {
        "message": "Booking successful",
        "user_id": booking.user_id,
        "flight_id": booking.flight_id
    }

@app.get("/bookings/{user_id}", response_model=List[Booking])
def get_user_bookings(user_id: int):
    db = SessionLocal()

    # Get all bookings for the specified user
    bookings = db.query(BookingDB).filter(BookingDB.user_id == user_id).all()

    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user")

    return bookings
EOF

# 4. Cancel Booking Service
cat > cancel_booking_service.py <<EOF
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models import BookingDB, Flight
from .database import SessionLocal

app = FastAPI()

class CancelBooking(BaseModel):
    booking_id: int

    class Config:
        orm_mode = True

@app.post("/cancel/")
def cancel_booking(cancel_booking: CancelBooking):
    db = SessionLocal()

    # Fetch the booking to be canceled
    booking = db.query(BookingDB).get(cancel_booking.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Fetch the flight associated with the booking
    flight = db.query(Flight).get(booking.flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # Remove the booking from the database
    db.delete(booking)
    db.commit()

    # Return the ticket to the flight
    flight.available_tickets += 1
    db.commit()

    return {
        "message": f"Booking {cancel_booking.booking_id} canceled successfully",
        "flight_id": flight.id
    }
EOF

echo "✅ All microservice files created!"
echo "You can now run each one with uvicorn, like this:"
echo "uvicorn user_service:app --reload --port 8000"
echo "uvicorn flight_service:app --reload --port 8001"
echo "uvicorn booking_service:app --reload --port 8002"
echo "uvicorn cancel_booking_service:app --reload --port 8003"
