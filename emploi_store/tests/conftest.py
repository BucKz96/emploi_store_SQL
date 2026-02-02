"""Configuration pytest."""

import os
import sys
from pathlib import Path

# Ajout du chemin parent pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configuration des variables d'environnement pour les tests
os.environ.setdefault("FRANCETRAVAIL_CLIENT_ID", "test_client_id")
os.environ.setdefault("FRANCETRAVAIL_CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
