"""Service d'analyse des données."""


from sqlalchemy import func
from sqlalchemy.orm import Session

from emploi_store.models.database import Offer, Salary, Skill
from emploi_store.models.schemas import SalaryStats, SkillStats


class AnalysisService:
    """Service pour analyser les données."""

    def __init__(self, db: Session):
        self.db = db

    def get_salary_stats_by_department(self) -> list[SalaryStats]:
        """Calcule les statistiques de salaire par département."""
        results = (
            self.db.query(
                Offer.department_code,
                func.avg(Salary.min_salary).label("avg_min"),
                func.avg(Salary.max_salary).label("avg_max"),
                func.count(Offer.id).label("count"),
            )
            .join(Salary, Offer.id == Salary.offer_id)
            .filter(Salary.min_salary.isnot(None))
            .group_by(Offer.department_code)
            .all()
        )

        return [
            SalaryStats(
                department_code=r.department_code,
                avg_min_salary=round(r.avg_min, 2) if r.avg_min else None,
                avg_max_salary=round(r.avg_max, 2) if r.avg_max else None,
                count=r.count,  # type: ignore[arg-type]
            )
            for r in results
            if r.department_code
        ]

    def get_top_skills(self, limit: int = 20) -> list[SkillStats]:
        """Récupère les compétences les plus demandées."""
        results = (
            self.db.query(Skill.name, func.count(Skill.id).label("count"))
            .filter(Skill.name.isnot(None))
            .group_by(Skill.name)
            .order_by(func.count(Skill.id).desc())
            .limit(limit)
            .all()
        )

        return [
            SkillStats(skill_name=r.name, count=r.count)  # type: ignore[arg-type]
            for r in results
        ]

    def get_offers_by_department(self, min_count: int = 5) -> list[dict]:
        """Compte les offres par département."""
        results = (
            self.db.query(Offer.department_code, func.count(Offer.id).label("count"))
            .filter(Offer.department_code.isnot(None))
            .group_by(Offer.department_code)
            .having(func.count(Offer.id) >= min_count)
            .all()
        )

        return [
            {"department_code": r.department_code, "count": r.count}  # type: ignore[dict-item]
            for r in results
        ]

    def get_contract_types_distribution(self) -> list[dict]:
        """Distribution des types de contrat."""
        results = (
            self.db.query(Offer.contract_type, func.count(Offer.id).label("count"))
            .filter(Offer.contract_type.isnot(None))
            .group_by(Offer.contract_type)
            .all()
        )

        return [
            {"contract_type": r.contract_type, "count": r.count}  # type: ignore[dict-item]
            for r in results
        ]
