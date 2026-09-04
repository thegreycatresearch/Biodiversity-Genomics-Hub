# 🧬 Biodiversity Genomics Hub

Panel unificado de código abierto para la conservación de biodiversidad,
que conecta **datos genéticos** y **bases de datos geográficas/taxonómicas**
públicas en un solo dashboard, pensado para laboratorios, ONGs de
conservación y equipos de investigación.

## Qué hace

Al buscar una especie por su nombre científico, el sistema:

1. **Ubica sus ocurrencias geográficas** (mapa interactivo) vía [GBIF](https://www.gbif.org/).
2. **Consulta su estado de conservación** actual vía [IUCN Red List](https://www.iucnredlist.org/).
3. **Descarga secuencias genéticas públicas** (marcador COI por defecto) desde [NCBI/GenBank](https://www.ncbi.nlm.nih.gov/genbank/) y calcula métricas reales de **diversidad genética**: diversidad nucleotídica (π), sitios segregantes, número de haplotipos y una señal exploratoria de riesgo por baja diversidad.
4. Permite **identificar una muestra por código de barras de ADN** contra la base pública de [BOLD Systems](https://boldsystems.org/), útil para trabajo de campo o control de tráfico de especies.
5. Mantiene un **registro/caché** de las especies ya consultadas por el equipo.

Todas las fuentes son APIs públicas y (mayormente) gratuitas — el proyecto
es funcional de entrada, no una maqueta.

## Arquitectura

```
biodiversity-genomics-hub/
├── backend/            FastAPI (Python) — orquesta las 4 APIs externas
│   ├── main.py
│   ├── services/        gbif_service, ncbi_service, bold_service, iucn_service, genetics_service
│   ├── models/schemas.py
│   └── database.py       caché en SQLite (o Postgres si configurás DATABASE_URL)
├── frontend/            HTML/CSS/JS estático, sin paso de build (Leaflet para el mapa)
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Cómo correrlo

### Opción A — Docker (recomendado)

```bash
cp .env.example .env
# completá NCBI_EMAIL y, si querés estado IUCN, IUCN_API_TOKEN
docker compose up --build
```

- Backend: http://localhost:8000 (docs interactivas en `/docs`)
- Frontend: http://localhost:5500

### Opción B — Manual

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # completar variables
uvicorn main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend
python -m http.server 5500
```

Abrí `http://localhost:5500` en el navegador.

## Credenciales necesarias

| Servicio | Requiere key | Dónde conseguirla |
|---|---|---|
| GBIF | No | — |
| NCBI/GenBank | Solo email (key opcional) | https://www.ncbi.nlm.nih.gov/account/settings/ |
| BOLD Systems | No | — |
| IUCN Red List | Sí (gratis) | https://api.iucnredlist.org/ |

Sin `IUCN_API_TOKEN` el panel sigue funcionando, solo que sin estado de conservación.

## Endpoints principales

- `GET /api/species/{scientific_name}` — resumen completo (mapa + IUCN + diversidad genética)
- `POST /api/barcode/identify` — identifica una secuencia de ADN
- `GET /api/species-cache` — historial de especies consultadas

Documentación interactiva automática en `/docs` (Swagger UI) al correr el backend.

## Roadmap sugerido

- [ ] Autenticación por laboratorio/usuario
- [ ] Exportar reportes en PDF por especie
- [ ] Mapa de conectividad genética entre poblaciones fragmentadas
- [ ] Soporte para subir tus propias secuencias (FASTA) además de NCBI
- [ ] Panel de alertas automáticas cuando π cae por debajo de un umbral

## Importante — alcance de las métricas genéticas

Las métricas de diversidad genética que calcula este proyecto son
**exploratorias**, basadas en las secuencias públicas disponibles en NCBI
para el marcador elegido. No reemplazan un estudio poblacional dedicado
con muestreo propio, ni un panel de marcadores curado por un laboratorio
de genética de la conservación. Están pensadas como una primera señal
rápida y accesible, no como conclusión final.

## Licencia

MIT — ver [LICENSE](./LICENSE).
