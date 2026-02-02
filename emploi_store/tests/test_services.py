"""Tests unitaires."""

from collections.abc import Generator
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from emploi_store.models.database import Base
from emploi_store.models.schemas import OfferCreate
from emploi_store.services.extraction import OfferService, parse_offer_data

# Base de données en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module(module: Any) -> None:
    """Setup pour tous les tests du module."""
    Base.metadata.create_all(bind=engine)


def teardown_module(module: Any) -> None:
    """Cleanup après tous les tests."""
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Fixture pour une session de DB."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


class TestOfferService:
    """Tests pour le service OfferService."""

    def test_save_offer(self, db_session: Session) -> None:
        """Test de sauvegarde d'une offre."""
        service = OfferService(db_session)

        offer_data = OfferCreate(
            id="TEST001",
            search_keyword="Développeur",
            title="Développeur Python",
            city="Paris",
            company_name="Test Corp",
        )

        offer = service.save_offer(offer_data)

        assert offer.id == "TEST001"  # type: ignore[comparison-overlap]
        assert offer.title == "Développeur Python"  # type: ignore[comparison-overlap]
        assert offer.search_keyword == "Développeur"  # type: ignore[comparison-overlap]

    def test_get_offer_by_id(self, db_session: Session) -> None:
        """Test de récupération d'une offre par ID."""
        service = OfferService(db_session)

        # Créer une offre
        offer_data = OfferCreate(
            id="TEST002", search_keyword="Développeur", title="Développeur JavaScript"
        )
        service.save_offer(offer_data)

        # Récupérer
        offer = service.get_offer_by_id("TEST002")

        assert offer is not None
        assert offer.title == "Développeur JavaScript"  # type: ignore[comparison-overlap]

    def test_get_offer_not_found(self, db_session: Session) -> None:
        """Test quand l'offre n'existe pas."""
        service = OfferService(db_session)

        offer = service.get_offer_by_id("NONEXISTENT")

        assert offer is None

    def test_count_offers(self, db_session: Session) -> None:
        """Test du comptage des offres."""
        service = OfferService(db_session)

        # Créer plusieurs offres
        for i in range(3):
            offer_data = OfferCreate(
                id=f"TEST{i + 10}", search_keyword="Python", title=f"Offre {i}"
            )
            service.save_offer(offer_data)

        count = service.count_offers(search_keyword="Python")

        assert count == 3


class TestParseOfferData:
    """Tests pour le parsing des offres."""

    def test_parse_simple_offer(self) -> None:
        """Test du parsing simple."""
        raw_data: dict[str, Any] = {
            "id": "OFF001",
            "intitule": "Développeur Web",
            "description": "Description de test",
            "lieuTravail": {"libelle": "Paris", "codePostal": "75001"},
            "entreprise": {"nom": "Test Company"},
            "typeContrat": "CDI",
        }

        result = parse_offer_data(raw_data, "Développeur")

        assert result is not None
        assert result.id == "OFF001"
        assert result.title == "Développeur Web"
        assert result.city == "Paris"

    def test_parse_with_skills(self) -> None:
        """Test du parsing avec compétences."""
        raw_data: dict[str, Any] = {
            "id": "OFF002",
            "intitule": "Développeur",
            "competences": [{"libelle": "Python"}, {"libelle": "SQL"}],
        }

        result = parse_offer_data(raw_data, "Dev")

        assert result is not None
        assert len(result.skills) == 2
        assert result.skills[0].name == "Python"

    def test_parse_without_id(self) -> None:
        """Test quand il manque l'ID."""
        raw_data: dict[str, Any] = {"intitule": "Offre sans ID"}

        result = parse_offer_data(raw_data, "Test")

        assert result is None


class TestNormalizeSalary:
    """Tests pour la normalisation des salaires."""

    def test_normalize_annual_to_monthly(self) -> None:
        """Test conversion annuel → mensuel."""
        from emploi_store.services.extraction import normalize_salary

        min_sal, max_sal = normalize_salary(60000, 80000)

        assert min_sal == 5000  # 60000 / 12
        assert max_sal == 6666  # 80000 / 12

    def test_normalize_smic(self) -> None:
        """Test que le SMIC horaire est ignoré."""
        from emploi_store.services.extraction import normalize_salary

        min_sal, max_sal = normalize_salary(9.76, None)

        assert min_sal is None
        assert max_sal is None

    def test_normalize_none(self) -> None:
        """Test avec valeurs None."""
        from emploi_store.services.extraction import normalize_salary

        min_sal, max_sal = normalize_salary(None, None)

        assert min_sal is None
        assert max_sal is None
