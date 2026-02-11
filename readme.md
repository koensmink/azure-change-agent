# Microsoft Azure + M365 Changes Collector

Enterprise-grade local change intelligence pipeline for:

-   Azure Updates
-   Microsoft 365 Roadmap
-   Microsoft Graph Message Center (Service Communications API)
-   Microsoft Intune "What's New"
-   Microsoft Defender "What's New"
-   Microsoft Entra "What's New"

This stack collects change announcements locally, normalizes them,
detects diffs via hashing, and exposes a clean API endpoint for
downstream automation (n8n, dashboards, OpenAI agents, reporting
pipelines).

------------------------------------------------------------------------

## Architecture Overview

### Components

**Collector (FastAPI)** - Scheduled ingestion via cron - Per-source
index + detail parsing - `event_id` (stable identifier) - `content_hash`
(change detection) - NEW / CHANGED detection - GA filtering - Security
relevance tagging

**n8n Bridge** - Secured webhook endpoint - Pulls `/digest` - Optional
XLSX export - Can be used as OpenAI Agent Action endpoint

**Storage** - SQLite (local persistent volume) - Change tracking per
event

------------------------------------------------------------------------

## Data Model

Each event contains:

-   `event_id`
-   `content_hash`
-   `change_type` (NEW \| CHANGED \| UNCHANGED)
-   `source`
-   `release_stage` (GA \| Preview \| Planned \| Retirement \| Unknown)
-   `security_relevant`
-   `category`
-   `impact`
-   `recommended_action`

Hashing ensures only meaningful content changes trigger updates.

------------------------------------------------------------------------

## Deployment

### 1. Configure Environment

Copy `.env.example` to `.env` and configure:

    GRAPH_TENANT_ID=
    GRAPH_CLIENT_ID=
    GRAPH_CLIENT_SECRET=
    N8N_DIGEST_API_KEY=

### 2. Build & Run

    docker compose build --no-cache
    docker compose up -d

### 3. Validate

Health endpoint:

    http://localhost:8088/health

Digest endpoint:

    http://localhost:8088/digest?hours=24&ga_only=true&security_only=true

------------------------------------------------------------------------

## Required Microsoft Graph Permissions

Application permission:

-   `ServiceMessage.Read.All`

Grant admin consent after assigning permission.

------------------------------------------------------------------------

## GA Filtering Logic

GA filtering uses:

-   M365 Roadmap: `Status == Launched`
-   Azure / Learn pages: textual detection of "General Availability"
-   Message Center: heuristic detection (where applicable)

------------------------------------------------------------------------

## Security Classification

Keyword-based classification detects identity, endpoint, networking,
compliance and security changes.

This enables downstream filtering and reporting.

------------------------------------------------------------------------

## n8n Webhook Usage

The bridge exposes:

    /webhook/azure-digest

Header required:

    x-api-key: <N8N_DIGEST_API_KEY>

------------------------------------------------------------------------

## Example OpenAI Agent Integration

Point your agent Action to:

    https://<your-n8n-domain>/webhook/azure-digest

Response format: structured JSON digest.

------------------------------------------------------------------------

## Recommended Hardening

-   Replace client secret with certificate authentication
-   Place n8n behind reverse proxy with TLS
-   Add rate limiting
-   Restrict webhook exposure (IP allowlist / Zero Trust access)

------------------------------------------------------------------------

## Maintenance Notes

-   Graph paging can be extended if volume increases
-   Detail parsing logic may require updates if Microsoft changes markup
-   Consider moving to PostgreSQL for higher scale environments

------------------------------------------------------------------------

## License

Internal enterprise tooling. Adjust as required.
