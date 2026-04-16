# Azure + M365 Change Collector

Een lightweight, self-hosted collector die wijzigingen uit Microsoft-platformen ophaalt,
normaliseert, opslaat en beschikbaar maakt via een JSON API én een weboverzicht.

## Wat doet deze service?

- Haalt updates op uit meerdere Microsoft-bronnen.
- Zet ruwe data om naar één uniform event-model.
- Detecteert echte inhoudelijke wijzigingen via hashing (`NEW`, `CHANGED`, `UNCHANGED`).
- Slaat data op in database (PostgreSQL via Docker Compose, met SQLite fallback).
- Biedt API-endpoints voor automatisering (n8n, agents, dashboards).
- Biedt een browserpagina om events direct te bekijken (`/events/web`).

---

## Ondersteunde bronnen

- Azure Updates
- Microsoft 365 Roadmap
- Microsoft Graph Message Center (Service Communications API)
- Intune "What's New"
- Defender "What's New"
- Entra "What's New"

---

## Architectuur (kort)

### Collector (FastAPI)

- Draait ingest op basis van cron
- Verwerkt index + detail per bron
- Maakt stabiele `event_id`
- Gebruikt `content_hash` voor changedetection
- Labelt security-relevantie en release stage

### Opslag

- **Standaard in Compose:** PostgreSQL
- **Fallback:** SQLite (als `DATABASE_URL` niet is gezet)

### Exposed endpoints

- `GET /health` → health check
- `GET /events` → genormaliseerde events (filterbaar)
- `GET /digest` → samenvatting/digest
- `GET /events/web` → weboverzicht van events uit database

---

## Snel starten

### 1) Configureer

```bash
cp .env.example .env
```

Vul minimaal in:

```bash
GRAPH_TENANT_ID=
GRAPH_CLIENT_ID=
GRAPH_CLIENT_SECRET=
N8N_DIGEST_API_KEY=
DATABASE_URL=postgresql://collector:collector@postgres:5432/collector
```

> Laat je `DATABASE_URL` weg, dan valt de app terug op SQLite (`/app/data/events.db`).

### 2) Start de stack

```bash
docker compose build --no-cache
docker compose up -d
```

### 3) Controleer

- Health: <http://localhost:8088/health>
- Events API: <http://localhost:8088/events>
- Digest API: <http://localhost:8088/digest?hours=24&ga_only=true&security_only=true>
- Weboverzicht: <http://localhost:8088/events/web>

---

## Vereiste Microsoft Graph permissie

Application permission:

- `ServiceMessage.Read.All`

Vergeet niet **admin consent** te geven.

---

## Veelgebruikte use-cases

- Security monitoring van Microsoft platformwijzigingen
- Compliance/impact-overzichten
- Input voor SOC/SIEM enrichment
- Interne wijzigingsdashboards
- Geautomatiseerde rapportages via n8n of agents
