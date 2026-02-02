"""Services d'extraction et de traitement des données."""

import logging
import re

from sqlalchemy.orm import Session

from emploi_store.api.client import FranceTravailClient
from emploi_store.models.database import Geolocation, Offer, Salary, Skill
from emploi_store.models.schemas import GeolocationCreate, OfferCreate, SalaryCreate, SkillCreate

logger = logging.getLogger(__name__)


def normalize_salary(min_salary: float | None, max_salary: float | None) -> tuple:
    """Normalise les salaires (convertit annuel en mensuel si nécessaire)."""
    # Valeurs aberrantes (SMIC horaire = 9.76)
    if min_salary == 9.76 or (min_salary is None and max_salary is None):
        return None, None

    # Conversion annuel → mensuel
    if min_salary and min_salary > 10000:
        min_salary = int(min_salary / 12)
    if max_salary and max_salary > 10000:
        max_salary = int(max_salary / 12)

    return min_salary, max_salary


def parse_offer_data(raw_offer: dict, search_keyword: str) -> OfferCreate | None:
    """Parse les données brutes de l'API en modèle OfferCreate."""
    try:
        offer_id = raw_offer.get("id", raw_offer.get("offerId"))
        if not offer_id:
            logger.warning("Offre sans ID ignorée")
            return None

        # Extraction des données de localisation
        lieu = raw_offer.get("lieuTravail", {})
        geolocation = None
        if "latitude" in lieu and "longitude" in lieu:
            geolocation = GeolocationCreate(latitude=lieu["latitude"], longitude=lieu["longitude"])

        # Extraction des données de salaire
        salaire = raw_offer.get("salaire", {})
        min_sal = salaire.get("libelle")
        max_sal = None

        # Tentative de parsing du salaire
        if min_sal and isinstance(min_sal, str):
            # Extraction des nombres
            numbers = re.findall(r"\d+", min_sal.replace(" ", ""))
            if numbers:
                try:
                    values = [int(n) for n in numbers if int(n) > 100]
                    if values:
                        min_sal = min(values)
                        max_sal = max(values) if len(values) > 1 else None
                    else:
                        min_sal = None
                except ValueError:
                    min_sal = None

        min_sal, max_sal = normalize_salary(
            float(min_sal) if isinstance(min_sal, (int, float)) else None,
            float(max_sal) if isinstance(max_sal, (int, float)) else None,
        )  # type: ignore[arg-type]

        # Extraction des compétences
        skills = []
        for competence in raw_offer.get("competences", []):
            if isinstance(competence, dict):
                skills.append(SkillCreate(libelle=competence.get("libelle", "")))
            elif isinstance(competence, str):
                skills.append(SkillCreate(libelle=competence))

        # Nettoyage de la description
        description = raw_offer.get("description", "")
        if description:
            description = description.replace("\n", " ").replace("\r", " ").strip()

        return OfferCreate(
            id=offer_id,
            search_keyword=search_keyword,
            title=raw_offer.get("intitule", "Sans titre"),
            department_code=lieu.get("codePostal", lieu.get("commune", ""))[:2]
            if lieu.get("codePostal")
            else None,
            city_code=int(lieu.get("codePostal", 0))
            if lieu.get("codePostal") and lieu.get("codePostal").isdigit()
            else None,
            city=lieu.get("libelle"),
            company_name=raw_offer.get("entreprise", {}).get("nom"),
            description=description,
            contract_type=raw_offer.get("typeContrat"),
            contact_email=raw_offer.get("contact", {}).get("coordonnees1"),
            geolocation=geolocation,
            salary=SalaryCreate(min_salary=min_sal, max_salary=max_sal)
            if min_sal or max_sal
            else None,
            skills=skills,
        )
    except Exception as e:
        logger.error(f"Erreur lors du parsing de l'offre: {e}")
        return None


class OfferService:
    """Service pour gérer les offres."""

    def __init__(self, db: Session):
        self.db = db

    def save_offer(self, offer_data: OfferCreate) -> Offer:
        """Sauvegarde ou met à jour une offre."""
        # Vérifier si l'offre existe déjà
        existing = self.db.query(Offer).filter(Offer.id == offer_data.id).first()

        if existing:
            # Mise à jour
            existing.title = offer_data.title  # type: ignore[assignment]
            existing.city = offer_data.city  # type: ignore[assignment]
            existing.company_name = offer_data.company_name  # type: ignore[assignment]
            existing.description = offer_data.description  # type: ignore[assignment]
            existing.contract_type = offer_data.contract_type  # type: ignore[assignment]
            existing.contact_email = offer_data.contact_email  # type: ignore[assignment]
            offer = existing
        else:
            # Création
            offer = Offer(
                id=offer_data.id,
                search_keyword=offer_data.search_keyword,
                title=offer_data.title,
                department_code=offer_data.department_code,
                city_code=offer_data.city_code,
                city=offer_data.city,
                company_name=offer_data.company_name,
                description=offer_data.description,
                contract_type=offer_data.contract_type,
                contact_email=offer_data.contact_email,
            )
            self.db.add(offer)

        self.db.flush()

        # Géolocalisation
        if offer_data.geolocation:
            geo = self.db.query(Geolocation).filter(Geolocation.offer_id == offer.id).first()
            if geo:
                geo.latitude = offer_data.geolocation.latitude  # type: ignore[assignment]
                geo.longitude = offer_data.geolocation.longitude  # type: ignore[assignment]
            else:
                geo = Geolocation(
                    offer_id=offer.id,
                    latitude=offer_data.geolocation.latitude,
                    longitude=offer_data.geolocation.longitude,
                )
                self.db.add(geo)

        # Salaire
        if offer_data.salary:
            sal = self.db.query(Salary).filter(Salary.offer_id == offer.id).first()
            if sal:
                sal.min_salary = offer_data.salary.min_salary  # type: ignore[assignment]
                sal.max_salary = offer_data.salary.max_salary  # type: ignore[assignment]
            else:
                sal = Salary(
                    offer_id=offer.id,
                    min_salary=offer_data.salary.min_salary,
                    max_salary=offer_data.salary.max_salary,
                )
                self.db.add(sal)

        # Compétences (suppression des anciennes)
        self.db.query(Skill).filter(Skill.offer_id == offer.id).delete()
        for skill_data in offer_data.skills:
            if skill_data.name:
                skill = Skill(offer_id=offer.id, name=skill_data.name)
                self.db.add(skill)

        self.db.commit()
        return offer

    def get_offers(
        self, skip: int = 0, limit: int = 100, search_keyword: str | None = None
    ) -> list[Offer]:
        """Récupère les offres avec pagination."""
        query = self.db.query(Offer)
        if search_keyword:
            query = query.filter(Offer.search_keyword == search_keyword)
        return query.offset(skip).limit(limit).all()

    def get_offer_by_id(self, offer_id: str) -> Offer | None:
        """Récupère une offre par son ID."""
        return self.db.query(Offer).filter(Offer.id == offer_id).first()

    def count_offers(self, search_keyword: str | None = None) -> int:
        """Compte le nombre d'offres."""
        query = self.db.query(Offer)
        if search_keyword:
            query = query.filter(Offer.search_keyword == search_keyword)
        return query.count()


class ExtractionService:
    """Service pour extraire les données de l'API."""

    DEPARTMENTS = [f"{i:02d}" for i in range(1, 96) if i != 20] + [
        "2A",
        "2B",
        "971",
        "972",
        "973",
        "974",
        "976",
    ]

    def __init__(self, db: Session):
        self.db = db
        self.offer_service = OfferService(db)

    async def extract_offers(self, keyword: str, max_departments: int | None = None) -> dict:
        """Extrait les offres pour un mot-clé."""
        departments = self.DEPARTMENTS[:max_departments] if max_departments else self.DEPARTMENTS

        logger.info(f"Extraction des offres pour '{keyword}' sur {len(departments)} départements")

        async with FranceTravailClient() as client:
            raw_offers = await client.search_all_departments(keyword, departments)

        logger.info(f"{len(raw_offers)} offres trouvées")

        # Parsing et sauvegarde
        saved_count = 0
        errors_count = 0

        for raw_offer in raw_offers:
            offer_data = parse_offer_data(raw_offer, keyword)
            if offer_data:
                try:
                    self.offer_service.save_offer(offer_data)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Erreur sauvegarde offre {offer_data.id}: {e}")
                    errors_count += 1
            else:
                errors_count += 1

        logger.info(f"Extraction terminée: {saved_count} sauvegardées, {errors_count} erreurs")

        return {
            "keyword": keyword,
            "total_found": len(raw_offers),
            "saved": saved_count,
            "errors": errors_count,
        }
