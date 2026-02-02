"""Client API France Travail avec support async."""

import asyncio
from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from emploi_store.config.settings import Settings, get_settings


class FranceTravailAPIError(Exception):
    """Exception pour les erreurs API France Travail."""

    pass


class FranceTravailClient:
    """Client async pour l'API France Travail."""

    AUTH_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
    API_BASE_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2"

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.token: str | None = None
        self.session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> "FranceTravailClient":
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any
    ) -> None:
        await self.close()

    async def connect(self) -> None:
        """Initialise la session HTTP et récupère le token."""
        timeout = ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        await self._authenticate()

    async def close(self) -> None:
        """Ferme la session HTTP."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _authenticate(self) -> None:
        """Authentifie et récupère le token OAuth2."""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        data = {
            "grant_type": "client_credentials",
            "client_id": self.settings.francetravail_client_id,
            "client_secret": self.settings.francetravail_client_secret,
            "scope": "api_offresdemploiv2 o2dsoffre",
            "realm": "partenaire",
        }

        try:
            if not self.session:
                raise FranceTravailAPIError("Session HTTP non initialisée")
            async with self.session.post(self.AUTH_URL, headers=headers, data=data) as response:
                response.raise_for_status()
                result = await response.json()
                self.token = result["access_token"]
        except aiohttp.ClientError as e:
            raise FranceTravailAPIError(f"Erreur d'authentification: {e}") from e

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Effectue une requête authentifiée."""
        if not self.token:
            await self._authenticate()

        if not self.session:
            raise FranceTravailAPIError("Session HTTP non initialisée")

        url = f"{self.API_BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            **kwargs.pop("headers", {}),
        }

        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                if response.status == 401:
                    # Token expiré, réauthentification
                    await self._authenticate()
                    headers["Authorization"] = f"Bearer {self.token}"
                    if not self.session:
                        raise FranceTravailAPIError("Session HTTP non initialisée")
                    async with self.session.request(
                        method, url, headers=headers, **kwargs
                    ) as retry_response:
                        retry_response.raise_for_status()
                        retry_result: dict[str, Any] = await retry_response.json()
                        return retry_result

                response.raise_for_status()
                response_result: dict[str, Any] = await response.json()
                return response_result
        except aiohttp.ClientError as e:
            raise FranceTravailAPIError(f"Erreur API: {e}") from e

    async def search_offers(
        self, keyword: str, department_code: str | None = None, page: int = 1, per_page: int = 50
    ) -> list[dict[str, Any]]:
        """Recherche des offres d'emploi."""
        params = {
            "motsCles": keyword,
            "page": page,
            "range": f"{(page - 1) * per_page}-{page * per_page - 1}",
        }

        if department_code:
            params["departement"] = department_code

        result = await self._request("GET", "offres/search", params=params)
        offers: list[dict[str, Any]] = result.get("resultats", [])
        return offers

    async def get_offer_details(self, offer_id: str) -> dict[str, Any]:
        """Récupère les détails d'une offre."""
        return await self._request("GET", f"offres/{offer_id}")

    async def search_all_departments(
        self, keyword: str, departments: list[str], delay: float = 0.5
    ) -> list[dict[str, Any]]:
        """Recherche des offres dans tous les départements."""
        all_offers: list[dict[str, Any]] = []

        for dept in departments:
            try:
                offers = await self.search_offers(keyword, department_code=dept)
                all_offers.extend(offers)
                await asyncio.sleep(delay)
            except FranceTravailAPIError as e:
                import logging

                logging.getLogger(__name__).warning(f"Erreur pour le département {dept}: {e}")
                continue

        return all_offers
