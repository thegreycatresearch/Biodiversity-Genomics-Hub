document.addEventListener("DOMContentLoaded", () => {
  initMap();
  refreshRegistry();

  document.getElementById("species-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("species-input").value.trim();
    if (!name) return;
    await runSpeciesAnalysis(name);
  });

  document.getElementById("barcode-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const sequence = document.getElementById("barcode-input").value.trim();
    if (!sequence) return;
    await runBarcodeIdentification(sequence);
  });
});

async function runSpeciesAnalysis(name) {
  const occurrenceCountEl = document.getElementById("occurrence-count");
  const markerLabelEl = document.getElementById("marker-label");
  occurrenceCountEl.textContent = "buscando…";

  try {
    const summary = await fetchSpeciesSummary(name);
    occurrenceCountEl.textContent = `${summary.occurrence_count ?? 0} ocurrencias`;
    renderOccurrences(summary.occurrences);
    renderConservation(summary.conservation);
    renderDiversity(summary.diversity, markerLabelEl);
    refreshRegistry();
  } catch (err) {
    occurrenceCountEl.textContent = "error";
    document.getElementById("conservation-status").innerHTML = `<p class="empty-state">⚠ ${err.message}</p>`;
  }
}

async function runBarcodeIdentification(sequence) {
  const resultEl = document.getElementById("barcode-result");
  resultEl.innerHTML = `<p class="empty-state">Consultando BOLD Systems…</p>`;
  try {
    const result = await identifyBarcode(sequence);
    if (!result.best_match_name) {
      resultEl.innerHTML = `<p class="empty-state">Sin coincidencias claras en la base pública de BOLD.</p>`;
      return;
    }
    resultEl.innerHTML = `
      <div class="status-card">
        <div>
          <strong>${result.best_match_name}</strong><br/>
          <span class="marker-label">${result.similarity_percent ?? "—"}% similitud · ${result.source_database}</span>
        </div>
      </div>
    `;
  } catch (err) {
    resultEl.innerHTML = `<p class="empty-state">⚠ ${err.message}</p>`;
  }
}

async function refreshRegistry() {
  const rows = await fetchRegistry();
  renderRegistry(rows);
}
