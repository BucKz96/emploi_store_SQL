"""Modèles Pydantic pour la validation des données."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GeolocationBase(BaseModel):
    """Modèle de base pour la géolocalisation."""

    latitude: float | None = None
    longitude: float | None = None


class GeolocationCreate(GeolocationBase):
    """Modèle pour la création d'une géolocalisation."""

    pass


class Geolocation(GeolocationBase):
    """Modèle complet pour la géolocalisation."""

    offer_id: str

    model_config = ConfigDict(from_attributes=True)


class SalaryBase(BaseModel):
    """Modèle de base pour le salaire."""

    min_salary: int | None = None
    max_salary: int | None = None


class SalaryCreate(SalaryBase):
    """Modèle pour la création d'un salaire."""

    pass


class Salary(SalaryBase):
    """Modèle complet pour le salaire."""

    offer_id: str

    model_config = ConfigDict(from_attributes=True)


class SkillBase(BaseModel):
    """Modèle de base pour une compétence."""

    name: str | None = Field(None, alias="libelle")


class SkillCreate(SkillBase):
    """Modèle pour la création d'une compétence."""

    pass


class Skill(SkillBase):
    """Modèle complet pour une compétence."""

    id: int
    offer_id: str

    model_config = ConfigDict(from_attributes=True)


class OfferBase(BaseModel):
    """Modèle de base pour une offre."""

    search_keyword: str
    title: str
    department_code: int | None = None
    city_code: int | None = None
    city: str | None = None
    company_name: str | None = None
    description: str | None = None
    contract_type: str | None = None
    contact_email: str | None = None


class OfferCreate(OfferBase):
    """Modèle pour la création d'une offre."""

    id: str
    geolocation: GeolocationCreate | None = None
    salary: SalaryCreate | None = None
    skills: list[SkillCreate] = []


class Offer(OfferBase):
    """Modèle complet pour une offre."""

    id: str
    created_at: datetime
    updated_at: datetime | None = None
    geolocation: Geolocation | None = None
    salary: Salary | None = None
    skills: list[Skill] = []

    model_config = ConfigDict(from_attributes=True)


class OfferSummary(BaseModel):
    """Résumé d'une offre pour les listes."""

    id: str
    title: str
    company_name: str | None = None
    city: str | None = None
    contract_type: str | None = None


class SalaryStats(BaseModel):
    """Statistiques de salaire par département."""

    department_code: int
    avg_min_salary: float | None = None
    avg_max_salary: float | None = None
    count: int


class SkillStats(BaseModel):
    """Statistiques des compétences."""

    skill_name: str
    count: int
