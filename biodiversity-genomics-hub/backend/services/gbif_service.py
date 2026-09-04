"""
Cliente para la API pública de GBIF (Global Biodiversity Information Facility).
No requiere API key. Documentación: https://www.gbif.org/developer/summary
"""
from __future__ import annotations

import httpx

GBIF_BASE = "https://api.gbif.org/v1"


async def match_species(scientific_name: str) -> dict | None:
    """Resuelve un nombre científico al 'usageKey' taxonómico de GBIF."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{GBIF_BASE}/species/match", params={"name": scientific_name})
        resp.raise_for_status()
        data = resp.json()
        if data.get("matchType") == "NONE":
            return None
        return data


async def get_occurrences(gbif_key: str, limit: int = 300) -> dict:
    """Trae ocurrencias georreferenciadas para una especie (para el mapa)."""
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            f"{GBIF_BASE}/occurrence/search",
            params={
                "taxonKey": gbif_key,
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "limit": limit,
            },
        )
        resp.raise_for_status()
        return resp.json()


def parse_occurrences(raw: dict) -> list[dict]:
    points = []
    for rec in raw.get("results", []):
        lat, lon = rec.get("decimalLatitude"), rec.get("decimalLongitude")
        if lat is None or lon is None:
            continue
        points.append(
            {
                "lat": lat,
                "lon": lon,
                "date": rec.get("eventDate"),
                "country": rec.get("country"),
                "basis": rec.get("basisOfRecord"),
            }
        )
    return points
