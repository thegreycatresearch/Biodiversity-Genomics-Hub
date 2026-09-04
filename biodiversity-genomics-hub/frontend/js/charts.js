// Renderizado de las métricas de diversidad genética como tarjetas simples
// (evitamos una librería de charts pesada para mantener el proyecto liviano;
// se puede reemplazar por Chart.js/Plotly sin tocar el resto de la app).

const RISK_LABELS = {
  baja_diversidad: "Diversidad genética baja — señal de alerta",
  moderada: "Diversidad genética moderada",
  saludable: "Diversidad genética saludable",
  datos_insuficientes: "Datos insuficientes para estimar riesgo",
};

function renderDiversity(diversity, markerLabelEl) {
  const container = document.getElementById("diversity-metrics");

  if (!diversity) {
    container.innerHTML = `<p class="empty-state">No se encontraron secuencias públicas para esta especie con el marcador consultado.</p>`;
    markerLabelEl.textContent = "";
    return;
  }

  markerLabelEl.textContent = diversity.gene_marker;

  container.innerHTML = `
    <div class="metric-grid">
      <div class="metric">
        <div class="value">${diversity.nucleotide_diversity_pi}</div>
        <div class="label">Diversidad nucleotídica (π)</div>
      </div>
      <div class="metric">
        <div class="value">${diversity.sequences_analyzed}</div>
        <div class="label">Secuencias analizadas</div>
      </div>
      <div class="metric">
        <div class="value">${diversity.haplotype_count}</div>
        <div class="label">Haplotipos distintos</div>
      </div>
      <div class="metric">
        <div class="value">${diversity.gc_content_percent}%</div>
        <div class="label">Contenido GC</div>
      </div>
    </div>
    <div class="risk-note">
      <strong>${RISK_LABELS[diversity.risk_flag] || diversity.risk_flag}</strong><br/>
      ${diversity.disclaimer}
    </div>
  `;
}

function renderConservation(conservation) {
  const container = document.getElementById("conservation-status");
  if (!conservation || !conservation.category) {
    container.innerHTML = `<p class="empty-state">${
      conservation?.category_label || "Sin datos de estado de conservación."
    }</p>`;
    return;
  }
  const cssClass = `status-${conservation.category}`;
  container.innerHTML = `
    <div class="status-card">
      <span class="status-badge ${cssClass}">${conservation.category}</span>
      <div>
        <div>${conservation.category_label}</div>
        <div class="marker-label">${conservation.population_trend || "Tendencia poblacional no reportada"}</div>
      </div>
    </div>
  `;
}

function renderRegistry(rows) {
  const tbody = document.querySelector("#registry-table tbody");
  tbody.innerHTML = rows
    .map(
      (r) => `
      <tr>
        <td><em>${r.scientific_name}</em></td>
        <td>${r.iucn_category || "—"}</td>
        <td>${r.occurrence_count ?? "—"}</td>
        <td>${r.nucleotide_diversity ?? "—"}</td>
        <td>${r.sequences_analyzed ?? "—"}</td>
        <td>${r.updated_at ? new Date(r.updated_at).toLocaleDateString() : "—"}</td>
      </tr>`
    )
    .join("");
}
