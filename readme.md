# Azure + M365 Change Collector

Lightweight local pipeline for collecting, normalizing and tracking
changes across Microsoft services.

## ✨ Features

-   Collects updates from multiple Microsoft sources
-   Detects meaningful changes via hashing (no noise)
-   Filters on GA releases and security relevance
-   Exposes clean JSON API for automation
-   Includes browser overview page on `/events/web`
-   Easy integration with n8n, dashboards and agents
-   Fully self-hosted

------------------------------------------------------------------------

## 📦 Supported Sources

-   Azure updates
-   Microsoft 365 roadmap
-   Microsoft Graph Message Center (Service Communications API)
-   Intune "What's New"
-   Defender "What's New"
-   Entra "What's New"

------------------------------------------------------------------------

## 🏗️ Architecture

### Collector (FastAPI)

-   Scheduled ingestion (cron)
-   Source-specific parsing (index + detail)
-   Stable `event_id`
-   `content_hash` for change detection
-   Tracks: `NEW`, `CHANGED`, `UNCHANGED`
-   GA filtering
-   Security tagging

### n8n Bridge

-   Webhook endpoint
-   Pulls `/digest`
-   Optional XLSX export
-   Can be used as OpenAI Action endpoint

### Storage

-   PostgreSQL (default via Docker Compose)
-   SQLite fallback when `DATABASE_URL` is not set
-   Tracks state per event

------------------------------------------------------------------------

## 📊 Data Model

Each event contains:

-   `event_id`
-   `content_hash`
-   `change_type` (`NEW | CHANGED | UNCHANGED`)
-   `source`
-   `release_stage` (`GA | Preview | Planned | Retirement | Unknown`)
-   `security_relevant`
-   `category`
-   `impact`
-   `recommended_action`

Only real content changes trigger updates.

------------------------------------------------------------------------

## 🚀 Getting Started

### 1. Configure

```bash
cp .env.example .env
```

Set:

```bash
GRAPH_TENANT_ID=
GRAPH_CLIENT_ID=
GRAPH_CLIENT_SECRET=
N8N_DIGEST_API_KEY=
DATABASE_URL=postgresql://collector:collector@postgres:5432/collector
```

### 2. Run

```bash
docker compose build --no-cache
docker compose up -d
```

### 3. Verify

Health:

    http://localhost:8088/health

Digest:

    http://localhost:8088/digest?hours=24&ga_only=true&security_only=true

Web overview:

    http://localhost:8088/events/web

------------------------------------------------------------------------

## 🔐 Microsoft Graph Permissions

Required application permission:

-   `ServiceMessage.Read.All`

Admin consent is required.

------------------------------------------------------------------------

## 🧠 Filtering Logic

**GA filtering**

-   M365 Roadmap → `Status == Launched`
-   Azure / Learn → text detection ("General Availability")
-   Message Center → heuristic detection

**Security tagging**

-   Keyword-based classification (identity, endpoint, networking, compliance)

------------------------------------------------------------------------

## 🔗 Integration

### n8n

Webhook endpoint:

    /webhook/azure-digest

### OpenAI / Agents

Use as Action endpoint:

    https://<your-n8n-domain>/webhook/azure-digest

Returns structured JSON digest.

------------------------------------------------------------------------

## 📌 Use Cases

-   Security change monitoring
-   Compliance tracking (NIS2 / ISO)
-   SOC enrichment pipelines
-   Internal change dashboards
-   Automated reporting

------------------------------------------------------------------------

## 🛣️ Roadmap

-   Improved impact/context (AI-assisted)
-   Optional Postgres backend
-   Performance optimizations
-   Cloudflare Access integration
