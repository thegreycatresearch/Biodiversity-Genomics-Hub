"""
Biodiversity Genomics Hub — API principal.

Panel unificado que conecta:
- GBIF          -> ocurrencias geográficas de especies
- NCBI/GenBank  -> secuencias genéticas (marcador COI por defecto)
- BOLD Systems  -> identificación de especies por código de barras de ADN
- IUCN Red List -> estado de conservación

Correr localmente:
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db, SessionLocal, SpeciesRecord
from models.schemas import SpeciesSummary, ConservationStatus, DiversityMetrics, BarcodeMatch
from services import gbif_service, iucn_service, ncbi_service, genetics_service, bold_service

from sqlalchemy import select


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Biodiversity Genomics Hub",
    description="Panel unificado de conservación de biodiversidad basado en datos genéticos y geográficos abiertos.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustar en producción
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/species/{scientific_name}", response_model=SpeciesSummary)
async def get_species_summary(
    scientific_name: str,
    gene_marker: str = Query(default=ncbi_service.DEFAULT_MARKER, description="Filtro de gen para NCBI, ej. 'COI[Gene]'"),
    max_sequences: int = Query(default=15, ge=2, le=40),
    refresh: bool = Query(default=False, description="Ignora la caché y vuelve a consultar todo"),
):
    """Endpoint central: devuelve taxonomía + mapa de ocurrencias + estado
    de conservación + métricas de diversidad genética para una especie."""

    async with SessionLocal() as session:
        cached = None
        if not refresh:
            result = await session.execute(
                select(SpeciesRecord).where(SpeciesRecord.scientific_name == scientific_name)
            )
            cached = result.scalar_one_or_none()

        # 1. Taxonomía + ocurrencias (GBIF)
        match = await gbif_service.match_species(scientific_name)
        if not match or "usageKey" not in match:
            raise HTTPException(status_code=404, detail=f"No se encontró '{scientific_name}' en GBIF")

        gbif_key = str(match["usageKey"])
        raw_occ = await gbif_service.get_occurrences(gbif_key)
        occurrences = gbif_service.parse_occurrences(raw_occ)

        # 2. Estado de conservación (IUCN)
        iucn_data = await iucn_service.get_conservation_status(scientific_name)

        # 3. Secuencias (NCBI) + diversidad genética
        sequences = await ncbi_service.fetch_sequences(scientific_name, gene_marker, max_sequences)
        diversity_data = genetics_service.calculate_diversity(sequences, gene_marker) if sequences else None

        # Persistir/actualizar caché
        if cached is None:
            cached = SpeciesRecord(scientific_name=scientific_name)
            session.add(cached)
        cached.gbif_key = gbif_key
        cached.iucn_category = iucn_data.get("category") if iucn_data else None
        cached.occurrence_count = raw_occ.get("count")
        if diversity_data:
            cached.nucleotide_diversity = diversity_data["nucleotide_diversity_pi"]
            cached.gc_content = diversity_data["gc_content_percent"]
            cached.sequences_analyzed = diversity_data["sequences_analyzed"]
        await session.commit()

        return SpeciesSummary(
            scientific_name=scientific_name,
            gbif_key=gbif_key,
            occurrence_count=raw_occ.get("count"),
            occurrences=occurrences,
            conservation=ConservationStatus(**iucn_data) if iucn_data else None,
            diversity=DiversityMetrics(**diversity_data) if diversity_data else None,
        )


class BarcodeRequest(BaseModel):
    sequence: str
    marker: str = "COI-5P"


@app.post("/api/barcode/identify", response_model=BarcodeMatch)
async def identify_barcode(payload: BarcodeRequest):
    """Identifica una especie a partir de una secuencia de ADN (barcoding)
    contra la base pública de BOLD Systems."""
    if len(payload.sequence.strip()) < 50:
        raise HTTPException(status_code=400, detail="La secuencia es demasiado corta para identificar de forma confiable (mínimo ~50 pb).")
    result = await bold_service.identify_sequence(payload.sequence, payload.marker)
    return BarcodeMatch(**result)


@app.get("/api/species-cache", response_model=list[dict])
async def list_cached_species():
    """Lista las especies ya consultadas (para el dashboard del laboratorio)."""
    async with SessionLocal() as session:
        result = await session.execute(select(SpeciesRecord))
        rows = result.scalars().all()
        return [
            {
                "scientific_name": r.scientific_name,
                "iucn_category": r.iucn_category,
                "occurrence_count": r.occurrence_count,
                "nucleotide_diversity": r.nucleotide_diversity,
                "gc_content": r.gc_content,
                "sequences_analyzed": r.sequences_analyzed,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in rows
        ]
