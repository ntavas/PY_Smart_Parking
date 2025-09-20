from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="Available")
    last_updated = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    status_logs = relationship("SpotStatusLog", back_populates="spot")
    favorites = relationship("UserFavorites", back_populates="spot")
    reservations = relationship("Reservation", back_populates="spot")

class SpotStatusLog(Base):
    __tablename__ = "spot_status_log"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    status = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    spot = relationship("ParkingSpot", back_populates="status_logs")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    favorites = relationship("UserFavorites", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")

class UserFavorites(Base):
    __tablename__ = "user_favorites"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="favorites")
    spot = relationship("ParkingSpot", back_populates="favorites")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    start_time = Column(DateTime(timezone=False), nullable=False)
    end_time = Column(DateTime(timezone=False), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reservations")
    spot = relationship("ParkingSpot", back_populates="reservations")