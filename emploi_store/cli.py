"""Interface en ligne de commande."""

import asyncio
import logging

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session
from uvicorn import run as uvicorn_run

from emploi_store import __version__
from emploi_store.config.settings import get_settings
from emploi_store.models.database import SessionLocal, create_tables
from emploi_store.services.analysis import AnalysisService
from emploi_store.services.extraction import ExtractionService

app = typer.Typer(help="Emploi Store - Analyse d'offres d'emploi", rich_markup_mode="rich")
console = Console()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_db_session() -> Session:
    """Crée une session de base de données."""
    return SessionLocal()


@app.command()
def init() -> None:
    """Initialise la base de données."""
    from pathlib import Path

    rprint("[bold blue]Initialisation de la base de données...[/bold blue]")

    settings = get_settings()

    # Création du dossier data si nécessaire
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)

    # Création des tables
    create_tables()

    rprint(f"[bold green]✅ Base de données initialisée: {settings.database_path}[/bold green]")


@app.command()
def extract(
    keyword: str = typer.Argument(..., help="Mot-clé de recherche"),
    max_departments: int | None = typer.Option(
        None, "--max-depts", "-d", help="Nombre maximum de départements à parcourir (défaut: tous)"
    ),
) -> None:
    """Extrait les offres d'emploi depuis l'API France Travail."""
    rprint(f"[bold blue]Extraction des offres pour: {keyword}[/bold blue]")

    db = get_db_session()
    try:
        service = ExtractionService(db)
        result = asyncio.run(service.extract_offers(keyword, max_departments))

        rprint("[bold green]✅ Extraction terminée![/bold green]")
        rprint(f"  • Offres trouvées: {result['total_found']}")
        rprint(f"  • Sauvegardées: {result['saved']}")
        rprint(f"  • Erreurs: {result['errors']}")
    finally:
        db.close()


@app.command()
def stats(
    keyword: str | None = typer.Option(
        None, "--keyword", "-k", help="Filtrer par mot-clé de recherche"
    ),
) -> None:
    """Affiche les statistiques."""
    db = get_db_session()
    try:
        analysis = AnalysisService(db)

        # Tableau des offres par département
        table = Table(title="Offres par département")
        table.add_column("Département", style="cyan")
        table.add_column("Nombre d'offres", justify="right", style="green")

        dept_stats = analysis.get_offers_by_department(min_count=1)
        for stat in sorted(dept_stats, key=lambda x: x["count"], reverse=True)[:10]:
            table.add_row(str(stat["department_code"]), str(stat["count"]))

        console.print(table)

        # Tableau des top compétences
        skills_table = Table(title="Top 10 compétences")
        skills_table.add_column("Compétence", style="cyan")
        skills_table.add_column("Nombre d'offres", justify="right", style="green")

        top_skills = analysis.get_top_skills(limit=10)
        for skill in top_skills:
            skills_table.add_row(skill.skill_name, str(skill.count))

        console.print(skills_table)

    finally:
        db.close()


@app.command()
def api(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Hôte de l'API"),
    port: int = typer.Option(8000, "--port", "-p", help="Port de l'API"),
    reload: bool = typer.Option(False, "--reload", help="Rechargement auto (dev)"),
) -> None:
    """Lance l'API REST."""
    rprint(f"[bold blue]Démarrage de l'API sur http://{host}:{port}[/bold blue]")
    rprint(f"[dim]Documentation: http://{host}:{port}/docs[/dim]")

    uvicorn_run("api.main:app", host=host, port=port, reload=reload)


@app.command()
def dashboard(port: int = typer.Option(8501, "--port", "-p", help="Port du dashboard")) -> None:
    """Lance le dashboard Streamlit."""
    import subprocess

    rprint(f"[bold blue]Démarrage du dashboard sur http://localhost:{port}[/bold blue]")

    subprocess.run(["streamlit", "run", "dashboard/app.py", "--server.port", str(port)], check=True)


@app.command()
def version() -> None:
    """Affiche la version."""
    rprint(f"[bold blue]Emploi Store v{__version__}[/bold blue]")


def main() -> None:
    """Point d'entrée principal."""
    app()


if __name__ == "__main__":
    main()
