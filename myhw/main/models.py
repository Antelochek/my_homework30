from typing import Any, Dict

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint, create_engine)
from sqlalchemy.orm import Mapped, declarative_base, relationship, sessionmaker

from .app import db

engine = create_engine("sqlite:///park.db")
session_make = sessionmaker(engine)

Base = declarative_base()


class Client(db.Model):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    credit_card = Column(String(50))
    car_number = Column(String(10))

    parkings = relationship("ClientParking", back_populates="client")

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Parking(db.Model):
    __tablename__ = "parking"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(100), nullable=False)
    opened = Column(Boolean)
    count_places = Column(Integer, nullable=False)
    count_available_places = Column(Integer, nullable=False)

    clients = relationship("ClientParking", back_populates="parking")

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ClientParking(db.Model):
    __tablename__ = "client_parking"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client.id"))
    parking_id = Column(Integer, ForeignKey("parking.id"))
    time_in = Column(DateTime)
    time_out = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("client_id", "parking_id", name="unique_client_parking"),
    )

    client = relationship("Client", back_populates="parkings")
    parking = relationship("Parking", back_populates="clients")

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
