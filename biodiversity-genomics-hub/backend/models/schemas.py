from __future__ import annotations

from pydantic import BaseModel, Field


class OccurrencePoint(BaseModel):
    lat: float
    lon: float
    date: str | None = None
    country: str | None = None
    basis: str | None = None


class ConservationStatus(BaseModel):
    category: str | None = Field(None, description="Categoría IUCN, ej. 'EN', 'VU', 'LC'")
    category_label: str | None = None
    population_trend: str | None = None
    source: str = "IUCN Red List"


class DiversityMetrics(BaseModel):
    sequences_analyzed: int
    gene_marker: str
    mean_pairwise_differences: float
    nucleotide_diversity_pi: float
    gc_content_percent: float
    segregating_sites: int
    haplotype_count: int
    risk_flag: str = Field(
        description="Señal exploratoria de riesgo genético: 'baja_diversidad', 'moderada' o 'saludable'"
    )
    disclaimer: str = (
        "Métrica exploratoria calculada a partir de secuencias públicas disponibles. "
        "No sustituye un análisis poblacional dedicado ni un panel de marcadores curado."
    )


class BarcodeMatch(BaseModel):
    query_length: int
    best_match_name: str | None = None
    similarity_percent: float | None = None
    source_database: str
    matches: list[dict] = []


class SpeciesSummary(BaseModel):
    scientific_name: str
    gbif_key: str | None = None
    occurrence_count: int | None = None
    occurrences: list[OccurrencePoint] = []
    conservation: ConservationStatus | None = None
    diversity: DiversityMetrics | None = None
