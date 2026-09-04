// Cliente mínimo para hablar con el backend FastAPI.
// Cambiá API_BASE si desplegás el backend en otra URL/dominio.
const API_BASE = window.API_BASE || "http://localhost:8000";

async function fetchSpeciesSummary(scientificName) {
  const url = `${API_BASE}/api/species/${encodeURIComponent(scientificName)}`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Error consultando la especie");
  }
  return res.json();
}

async function identifyBarcode(sequence, marker = "COI-5P") {
  const res = await fetch(`${API_BASE}/api/barcode/identify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sequence, marker }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Error identificando la secuencia");
  }
  return res.json();
}

async function fetchRegistry() {
  const res = await fetch(`${API_BASE}/api/species-cache`);
  if (!res.ok) return [];
  return res.json();
}
