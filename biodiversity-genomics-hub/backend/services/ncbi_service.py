"""
Cliente para NCBI Entrez (GenBank) usando Biopython. Se recomienda setear
NCBI_EMAIL y opcionalmente NCBI_API_KEY (sube el límite de 3 a 10 req/seg)
en las variables de entorno. Ver .env.example.
"""
from __future__ import annotations

import os

from Bio import Entrez, SeqIO

Entrez.email = os.getenv("NCBI_EMAIL", "anonymous@example.com")
if os.getenv("NCBI_API_KEY"):
    Entrez.api_key = os.getenv("NCBI_API_KEY")

DEFAULT_MARKER = "COI[Gene] OR COX1[Gene]"


async def fetch_sequences(scientific_name: str, gene_marker: str = DEFAULT_MARKER, max_records: int = 20) -> list[str]:
    """Busca y descarga secuencias de un marcador genético (por defecto COI,
    el estándar de barcoding animal) para una especie dada. Corre en un
    hilo aparte porque Biopython/Entrez es bloqueante."""
    import asyncio

    def _run() -> list[str]:
        query = f'"{scientific_name}"[Organism] AND ({gene_marker})'
        handle = Entrez.esearch(db="nucleotide", term=query, retmax=max_records)
        record = Entrez.read(handle)
        handle.close()
        ids = record.get("IdList", [])
        if not ids:
            return []

        handle = Entrez.efetch(db="nucleotide", id=ids, rettype="fasta", retmode="text")
        sequences = [str(rec.seq) for rec in SeqIO.parse(handle, "fasta")]
        handle.close()
        return sequences

    return await asyncio.to_thread(_run)
