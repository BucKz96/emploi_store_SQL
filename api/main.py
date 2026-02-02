"""API REST avec FastAPI."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from emploi_store.models.database import create_tables, get_db
from emploi_store.models.schemas import (
    Offer,
    OfferSummary,
    SalaryStats,
    SkillStats,
)
from emploi_store.services.analysis import AnalysisService
from emploi_store.services.extraction import OfferService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    create_tables()
    yield
    # Shutdown


app = FastAPI(
    title="Emploi Store API",
    description="API pour l'analyse des offres d'emploi France Travail",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """Page d'accueil."""
    return {"message": "Emploi Store API", "version": "2.0.0", "docs": "/docs"}


@app.get("/health")
async def health_check() -> dict:
    """Vérification de santé."""
    return {"status": "ok"}


@app.get("/offers", response_model=list[OfferSummary])
async def list_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search_keyword: str | None = None,
    db: Session = Depends(get_db),
) -> list[OfferSummary]:
    """Liste les offres d'emploi."""
    service = OfferService(db)
    offers = service.get_offers(skip=skip, limit=limit, search_keyword=search_keyword)
    return [
        OfferSummary(
            id=o.id,  # type: ignore[arg-type]
            title=o.title,  # type: ignore[arg-type]
            company_name=o.company_name,  # type: ignore[arg-type]
            city=o.city,  # type: ignore[arg-type]
            contract_type=o.contract_type,  # type: ignore[arg-type]
        )
        for o in offers
    ]


@app.get("/offers/{offer_id}", response_model=Offer)
async def get_offer(offer_id: str, db: Session = Depends(get_db)) -> Offer:
    """Récupère une offre par son ID."""
    service = OfferService(db)
    offer = service.get_offer_by_id(offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return offer


@app.get("/stats/salaries", response_model=list[SalaryStats])
async def get_salary_stats(db: Session = Depends(get_db)) -> list[SalaryStats]:
    """Statistiques de salaire par département."""
    service = AnalysisService(db)
    return service.get_salary_stats_by_department()


@app.get("/stats/skills", response_model=list[SkillStats])
async def get_skills_stats(
    limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
) -> list[SkillStats]:
    """Top compétences demandées."""
    service = AnalysisService(db)
    return service.get_top_skills(limit=limit)


@app.get("/stats/offers-by-department")
async def get_offers_by_department(
    min_count: int = Query(5, ge=1), db: Session = Depends(get_db)
) -> list[dict]:
    """Nombre d'offres par département."""
    service = AnalysisService(db)
    return service.get_offers_by_department(min_count=min_count)


@app.get("/stats/contracts")
async def get_contracts_distribution(db: Session = Depends(get_db)) -> list[dict]:
    """Distribution des types de contrat."""
    service = AnalysisService(db)
    return service.get_contract_types_distribution()


@app.get("/stats/summary")
async def get_summary(db: Session = Depends(get_db)) -> dict:
    """Résumé global des statistiques."""
    service = AnalysisService(db)
    offer_service = OfferService(db)

    return {
        "total_offers": offer_service.count_offers(),
        "departments_with_offers": len(service.get_offers_by_department(min_count=1)),
        "avg_salary_by_dept": len(service.get_salary_stats_by_department()),
        "top_skills_count": len(service.get_top_skills(limit=10)),
    }
