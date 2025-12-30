from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    rolle = Column(String)

class Maschine(Base):
    __tablename__ = 'maschinen'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    standort = Column(String)
    bereich = Column(String)
    status = Column(String, default="OK")
    tickets = relationship("Ticket", back_populates="maschine")

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    beschreibung = Column(Text)
    prio = Column(String)
    status = Column(String, default="NEU")
    
    # NEU: Hier speichert der Instandhalter seinen Bericht
    loesung = Column(Text, nullable=True) 
    
    erstellt_am = Column(DateTime, default=datetime.now)
    maschine_id = Column(Integer, ForeignKey('maschinen.id'))
    maschine = relationship("Maschine", back_populates="tickets")
    melder_id = Column(Integer, ForeignKey('users.id'))
    melder = relationship("User") 

engine = create_engine('sqlite:///fabrik.db', echo=False)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("DB Update: Ticket mit Lösungsfeld.")