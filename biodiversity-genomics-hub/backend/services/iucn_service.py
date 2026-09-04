"""
Cliente para la IUCN Red List API v4. Requiere una API key gratuita:
https://api.iucnredlist.org/  -> pedila y ponela en la variable de entorno
IUCN_API_TOKEN (ver .env.example).
"""
from __future__ import annotations

import os

import httpx

IUCN_BASE = "https://api.iucnredlist.org/api/v4"

CATEGORY_LABELS = {
    "EX": "Extinta",
    "EW": "Extinta en estado silvestre",
    "CR": "En peligro crítico",
    "EN": "En peligro",
    "VU": "Vulnerable",
    "NT": "Casi amenazada",
    "LC": "Preocupación menor",
    "DD": "Datos insuficientes",
    "NE": "No evaluada",
}


async def get_conservation_status(scientific_name: str) -> dict | None:
    token = os.getenv("IUCN_API_TOKEN")
    if not token:
        return {
            "category": None,
            "category_label": "IUCN_API_TOKEN no configurado",
            "population_trend": None,
        }

    headers = {"Authorization": token}
    async with httpx.AsyncClient(timeout=15, headers=headers) as client:
        resp = await client.get(f"{IUCN_BASE}/taxa/scientific_name", params={"genus_name": scientific_name.split(" ")[0], "species_name": scientific_name.split(" ")[-1]})
        if resp.status_code != 200:
            return None
        data = resp.json()
        assessments = data.get("assessments", [])
        if not assessments:
            return None
        latest = assessments[0]
        category = latest.get("red_list_category", {}).get("code")
        return {
            "category": category,
            "category_label": CATEGORY_LABELS.get(category, category),
            "population_trend": latest.get("population_trend", {}).get("description"),
        }
