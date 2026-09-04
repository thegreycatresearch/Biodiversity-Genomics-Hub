"""
Cliente para la API pública de identificación de BOLD Systems (Barcode of
Life Data System). No requiere API key.
Documentación: https://v4.boldsystems.org/index.php/resources/api
"""
from __future__ import annotations

import httpx

BOLD_IDENTIFY_URL = "https://v4.boldsystems.org/index.php/Ids_xml"


async def identify_sequence(sequence: str, marker: str = "COI-5P") -> dict:
    """Envía una secuencia (FASTA crudo o solo bases) al identificador de
    BOLD y devuelve la(s) mejor(es) coincidencia(s) taxonómica(s)."""
    clean_seq = "".join(c for c in sequence.upper() if c in "ACGTN")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            BOLD_IDENTIFY_URL,
            params={"db": "COX1_SPECIES_PUBLIC", "sequence": clean_seq},
        )
        resp.raise_for_status()
        # BOLD responde en XML; lo parseamos de forma mínima sin dependencias extra.
        return _parse_bold_xml(resp.text, len(clean_seq))


def _parse_bold_xml(xml_text: str, query_length: int) -> dict:
    import xml.etree.ElementTree as ET

    matches = []
    try:
        root = ET.fromstring(xml_text)
        for match in root.findall(".//match"):
            matches.append(
                {
                    "name": _find_text(match, "taxonomicidentification"),
                    "similarity": _find_text(match, "similarity"),
                    "specimen_id": _find_text(match, "ID"),
                    "country": _find_text(match, "country"),
                }
            )
    except ET.ParseError:
        pass

    best = matches[0] if matches else None
    return {
        "query_length": query_length,
        "best_match_name": best["name"] if best else None,
        "similarity_percent": float(best["similarity"]) if best and best.get("similarity") else None,
        "source_database": "BOLD Systems (COX1_SPECIES_PUBLIC)",
        "matches": matches[:10],
    }


def _find_text(node, tag: str) -> str | None:
    el = node.find(tag)
    return el.text if el is not None else None
