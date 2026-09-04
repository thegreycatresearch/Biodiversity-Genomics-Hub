"""
Cálculo de métricas de diversidad genética a partir de un conjunto de
secuencias homólogas (típicamente el marcador COI descargado de NCBI).

Implementación propia y liviana (sin dependencias pesadas tipo DendroPy)
para mantener el proyecto fácil de instalar. Las fórmulas siguen la
definición estándar de diversidad nucleotídica de Nei (1987).
"""
from __future__ import annotations

from itertools import combinations

from Bio.Align import PairwiseAligner

_aligner = PairwiseAligner()
_aligner.mode = "global"
_aligner.match_score = 1
_aligner.mismatch_score = 0
_aligner.open_gap_score = -1
_aligner.extend_gap_score = -0.5


def _hamming_after_alignment(seq_a: str, seq_b: str) -> tuple[int, int]:
    """Alinea dos secuencias y devuelve (diferencias, longitud_alineada)."""
    alignment = _aligner.align(seq_a, seq_b)[0]
    a_aligned, b_aligned = str(alignment[0]), str(alignment[1])
    diffs = sum(1 for x, y in zip(a_aligned, b_aligned) if x != y and x != "-" and y != "-")
    length = len(a_aligned)
    return diffs, length


def _gc_content(sequences: list[str]) -> float:
    total, gc = 0, 0
    for seq in sequences:
        seq = seq.upper()
        total += len(seq)
        gc += seq.count("G") + seq.count("C")
    return round((gc / total) * 100, 2) if total else 0.0


def _segregating_sites(sequences: list[str]) -> int:
    """Cuenta posiciones variables entre secuencias ya alineadas a la misma
    longitud (aproximación: trunca a la longitud mínima común)."""
    if len(sequences) < 2:
        return 0
    min_len = min(len(s) for s in sequences)
    trimmed = [s[:min_len] for s in sequences]
    segregating = 0
    for i in range(min_len):
        bases = {s[i] for s in trimmed}
        if len(bases) > 1:
            segregating += 1
    return segregating


def calculate_diversity(sequences: list[str], gene_marker: str) -> dict:
    """Calcula pi (diversidad nucleotídica), diferencias promedio por par,
    contenido GC, sitios segregantes y una señal exploratoria de riesgo.

    Limita el n de pares comparados para mantener el tiempo de respuesta
    razonable si llegan muchas secuencias.
    """
    n = len(sequences)
    if n < 2:
        return {
            "sequences_analyzed": n,
            "gene_marker": gene_marker,
            "mean_pairwise_differences": 0.0,
            "nucleotide_diversity_pi": 0.0,
            "gc_content_percent": _gc_content(sequences),
            "segregating_sites": 0,
            "haplotype_count": n,
            "risk_flag": "datos_insuficientes",
        }

    pairs = list(combinations(range(n), 2))
    max_pairs = 60  # tope para no saturar el aligner con muestras grandes
    if len(pairs) > max_pairs:
        pairs = pairs[:max_pairs]

    diff_ratios = []
    for i, j in pairs:
        diffs, length = _hamming_after_alignment(sequences[i], sequences[j])
        if length:
            diff_ratios.append(diffs / length)

    mean_pairwise = sum(diff_ratios) / len(diff_ratios) if diff_ratios else 0.0
    haplotypes = len(set(sequences))

    if mean_pairwise < 0.001:
        risk = "baja_diversidad"
    elif mean_pairwise < 0.01:
        risk = "moderada"
    else:
        risk = "saludable"

    return {
        "sequences_analyzed": n,
        "gene_marker": gene_marker,
        "mean_pairwise_differences": round(mean_pairwise * 100, 4),
        "nucleotide_diversity_pi": round(mean_pairwise, 6),
        "gc_content_percent": _gc_content(sequences),
        "segregating_sites": _segregating_sites(sequences),
        "haplotype_count": haplotypes,
        "risk_flag": risk,
    }
