"""Modèles SQLAlchemy pour la base de données."""

from collections.abc import Generator
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from emploi_store.config.settings import get_settings


class Base(DeclarativeBase):
    """Base déclarative SQLAlchemy."""

    pass


class Offer(Base):
    """Modèle pour les offres d'emploi."""

    __tablename__ = "offers"

    id = Column(String(45), primary_key=True)
    search_keyword = Column(String(100), nullable=False)
    title = Column(String(100), nullable=False)
    department_code = Column(Integer, nullable=True)
    city_code = Column(Integer, nullable=True)
    city = Column(String(100), nullable=True)
    company_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    contract_type = Column(String(45), nullable=True)
    contact_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relations
    geolocation = relationship("Geolocation", back_populates="offer", uselist=False)
    salary = relationship("Salary", back_populates="offer", uselist=False)
    skills = relationship("Skill", back_populates="offer")


class Geolocation(Base):
    """Modèle pour la géolocalisation des offres."""

    __tablename__ = "geolocations"

    offer_id = Column(String(45), ForeignKey("offers.id"), primary_key=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relations
    offer = relationship("Offer", back_populates="geolocation")


class Salary(Base):
    """Modèle pour les salaires des offres."""

    __tablename__ = "salaries"

    offer_id = Column(String(45), ForeignKey("offers.id"), primary_key=True)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)

    # Relations
    offer = relationship("Offer", back_populates="salary")


class Skill(Base):
    """Modèle pour les compétences des offres."""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    offer_id = Column(String(45), ForeignKey("offers.id"), nullable=False)

    # Relations
    offer = relationship("Offer", back_populates="skills")


# Configuration de la base de données
settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=settings.api_debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Crée toutes les tables dans la base de données."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Générateur de session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
