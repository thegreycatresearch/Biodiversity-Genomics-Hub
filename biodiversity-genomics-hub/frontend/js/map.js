// Manejo del mapa Leaflet: se inicializa una sola vez y se van
// reemplazando los marcadores de ocurrencias en cada búsqueda.
let leafletMap = null;
let markersLayer = null;

function initMap() {
  leafletMap = L.map("map").setView([0, -60], 2);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 18,
  }).addTo(leafletMap);
  markersLayer = L.layerGroup().addTo(leafletMap);
}

function renderOccurrences(occurrences) {
  markersLayer.clearLayers();
  if (!occurrences || occurrences.length === 0) return;

  const bounds = [];
  occurrences.forEach((occ) => {
    const marker = L.circleMarker([occ.lat, occ.lon], {
      radius: 4,
      color: "#0E7C7B",
      fillColor: "#0E7C7B",
      fillOpacity: 0.6,
      weight: 1,
    });
    marker.bindPopup(
      `<strong>${occ.country || "Sin país"}</strong><br/>${occ.date || "Fecha desconocida"}<br/>${occ.basis || ""}`
    );
    marker.addTo(markersLayer);
    bounds.push([occ.lat, occ.lon]);
  });

  if (bounds.length) {
    leafletMap.fitBounds(bounds, { maxZoom: 6, padding: [20, 20] });
  }
}
