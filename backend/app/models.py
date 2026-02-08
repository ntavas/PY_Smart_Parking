"""
models.py - SQLAlchemy Database Models

Defines all database tables and their relationships:
- ParkingSpot: Individual parking spaces with location and status
- SpotStatusLog: History of status changes for analytics
- User: Registered users who can reserve spots
- UserFavorites: User's saved favorite parking spots
- Reservation: Active parking reservations
- PaidParking: Pricing info for paid parking spots
"""

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, func, Numeric, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# =============================================================================
# Parking Spot Model
# =============================================================================

class ParkingSpot(Base):
    """
    Represents a single parking spot.
    Status can be: 'Available', 'Occupied', or 'Reserved'
    """
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(String(100), nullable=False)  # Human-readable address
    city = Column(String(50), nullable=True)
    area = Column(String(50), nullable=True)  # Neighborhood/district
    status = Column(String(20), nullable=False, default="Available")
    last_updated = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    paid_info = relationship("PaidParking", uselist=False, back_populates="spot")
    status_logs = relationship("SpotStatusLog", back_populates="spot")
    favorites = relationship("UserFavorites", back_populates="spot")
    reservations = relationship("Reservation", back_populates="spot")


# =============================================================================
# Spot Status Log Model
# =============================================================================

class SpotStatusLog(Base):
    """Tracks historical status changes for each spot (for analytics)."""
    __tablename__ = "spot_status_log"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    status = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=False), server_default=func.now())

    spot = relationship("ParkingSpot", back_populates="status_logs")


# =============================================================================
# User Model
# =============================================================================

class User(Base):
    """Registered user account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)  # Hashed password, never plain text
    full_name = Column(String(100), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    favorites = relationship("UserFavorites", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")


# =============================================================================
# User Favorites Model
# =============================================================================

class UserFavorites(Base):
    """Many-to-many relationship: users can favorite multiple spots."""
    __tablename__ = "user_favorites"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), primary_key=True)

    user = relationship("User", back_populates="favorites")
    spot = relationship("ParkingSpot", back_populates="favorites")


# =============================================================================
# Reservation Model
# =============================================================================

class Reservation(Base):
    """Active parking reservation made by a user."""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    start_time = Column(DateTime(timezone=False), nullable=False)
    end_time = Column(DateTime(timezone=False), nullable=True)  # Null = ongoing

    user = relationship("User", back_populates="reservations")
    spot = relationship("ParkingSpot", back_populates="reservations")


# =============================================================================
# Paid Parking Model
# =============================================================================

class PaidParking(Base):
    """
    Pricing information for paid parking spots.
    One-to-one relationship with ParkingSpot.
    """
    __tablename__ = "paid_parking"

    spot_id = Column(Integer, ForeignKey("parking_spots.id"), primary_key=True)
    price_per_hour = Column(Numeric(8, 2), nullable=False)

    spot = relationship("ParkingSpot", back_populates="paid_info")