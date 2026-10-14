# VAYU-COP — AI Decision Support for Dynamic Air Operations & Resource Optimisation

> **SIH 2026 · Problem Statement ID 26250 — "Air Power: Dynamic Air Operations & Resource Optimisation"**
> Ministry of Defence (MoD) · Defence Services Staff College · Category: Software · Theme: Transportation & Logistics
>
> This file is the **single source of truth** for building the prototype. It is written to be executed **phase by phase by an AI coding agent in the VS Code terminal** (Claude Code, Codex CLI, Gemini CLI, Copilot agent, etc.). Every phase has tasks, deliverables, acceptance criteria and a ready-to-paste agent prompt.

---

## Table of contents

0. [How to build with this file (read first)](#0-how-to-build-with-this-file-read-first)
1. [Problem → solution mapping](#1-problem--solution-mapping)
2. [Scope, assumptions & guardrails](#2-scope-assumptions--guardrails)
3. [Tech stack](#3-tech-stack)
4. [System architecture](#4-system-architecture)
5. [Repository layout](#5-repository-layout)
6. [Domain model](#6-domain-model)
7. [Synthetic data & exercise scenario](#7-synthetic-data--exercise-scenario)
8. [Multi-source data fusion](#8-multi-source-data-fusion)
9. [Optimisation engine](#9-optimisation-engine)
10. [Dynamic retasking](#10-dynamic-retasking)
11. [Predictive analytics](#11-predictive-analytics)
12. [API & WebSocket contract](#12-api--websocket-contract)
13. [UI specification (from the reference image)](#13-ui-specification-from-the-reference-image)
14. [Alerts & conflict-detection rules](#14-alerts--conflict-detection-rules)
15. [Phase-wise implementation plan](#15-phase-wise-implementation-plan)
16. [Demo script for judges](#16-demo-script-for-judges)
17. [KPIs & evaluation](#17-kpis--evaluation)
18. [Testing & performance targets](#18-testing--performance-targets)
19. [Security, offline deployment & ops](#19-security-offline-deployment--ops)
20. [AGENTS.md / CLAUDE.md (agent rules)](#20-agentsmd--claudemd-agent-rules)
21. [PROGRESS.md template](#21-progressmd-template)
22. [Glossary](#22-glossary)

---

## 0. How to build with this file (read first)

### 0.1 Workflow with an AI CLI agent

1. Create the repo folder `vayu-cop/` and open it in VS Code.
2. Save the UI reference image as **`docs/ui-reference.png`** (the agent should look at it for every UI phase).
3. Put this file at the repo root as `IMPLEMENTATION.md`.
4. Create `AGENTS.md` from §20 and copy it to `CLAUDE.md`, so whichever agent you use picks up the rules.
5. Create `PROGRESS.md` from §21.
6. Run **one phase per agent session** with this prompt template:

```text
Read IMPLEMENTATION.md fully, then AGENTS.md and PROGRESS.md.
We are on Phase <N>: <phase name>.
Implement EVERY task in Phase <N> and nothing from later phases.
Follow the tech stack (§3), repo layout (§5), data model (§6), API contract (§12)
and UI spec (§13) exactly. For UI work, look at docs/ui-reference.png for visual fidelity.
When finished: run the phase's verification commands, fix every failure,
tick the Phase <N> checkboxes in PROGRESS.md, and give me a short summary
of what was built and how to see it running.
```

7. After each phase, run the app yourself, check the acceptance criteria, then commit:
   `git add -A && git commit -m "phase-<N>: <name>"`.
8. When an agent session gets long, start a fresh one. `PROGRESS.md` carries the state forward.

### 0.2 Priority labels

| Label | Meaning |
|---|---|
| **P0** | Must exist for the demo |
| **P1** | Strong differentiator; build before the finale |
| **P2** | Polish; build if time permits |

**Internal hackathon MVP = Phases 0–10. Grand finale = Phases 0–16.**

### 0.3 Global Definition of Done (applies to every phase)

- [ ] Runs with one command (`make dev` locally, or `docker compose up --build`).
- [ ] **No hard-coded UI numbers.** Every value on screen comes from the backend.
- [ ] TypeScript `strict: true`; Python fully type-hinted; Pydantic models on every endpoint.
- [ ] Tests for the phase pass (`make test`); lint passes (`make lint`).
- [ ] Every AI output is a **proposal**. Only a user with the right role can approve it.
- [ ] All data is synthetic, and the UI shows an **"EXERCISE — SYNTHETIC DATA"** banner.
- [ ] No `TODO`/placeholder logic left in code delivered for the phase.

---

## 1. Problem → solution mapping

| Pain point in the problem statement | VAYU-COP answer | Phase |
|---|---|---|
| Aircraft availability, crew status, weapon loads, airspace, weather, threats and priorities sit in **multiple systems** | 8 simulated source systems with **deliberately different formats**, fused into one canonical COP with provenance, confidence and staleness | 3 |
| No **common, real-time decision-support framework** | One web COP: live map, KPI strip, AI panel, Gantt timeline, WebSocket updates | 4, 5, 8 |
| **Long planning timelines** | CP-SAT optimiser builds a complete allocation in seconds; timed against a manual baseline | 7 |
| **Sub-optimal allocation** of scarce airpower | Priority-weighted optimisation with range, fuel, crew-duty, maintenance, stores, weather and threat constraints; 3 alternative plans with trade-offs | 7 |
| **Contested, rapidly changing environment / dynamic retasking** | Event-driven impact analysis, then a warm-start re-solve with a stability penalty; plan diff and one-click commander approval | 9 |
| **Predictive analytics** | Serviceability forecast, crew fatigue, weather go/no-go, mission risk, sortie-generation capacity | 11 |
| **AI-enabled decision support** | Explainable recommendations ("why this, why not that"), what-if simulator, natural-language COP assistant, human-in-the-loop | 7, 12, 14 |

---

## 2. Scope, assumptions & guardrails

- **Exercise theatre:** the fictional **"Exercise VAYU SHIELD"** (Blueland vs Redland), confined to the inland box **lat 17.5°N–25.5°N, lon 74.0°E–84.0°E**. Bases *Alpha, Bravo, Charlie, Delta* are fictional.
- **Illustrative data only:** aircraft performance values are rounded, illustrative numbers used for simulation, not real performance data.
- **Threats are abstract:** threat zones are fictional rings (level HIGH/MED/LOW, radius, confidence). No real threat systems or parameters are modelled.
- **Weapon loads = generic "store configurations":** category, compatible aircraft types and counts per base, i.e. logistics availability only. The system allocates **aircraft, crew, time slots and store configurations** to **mission requests created by humans**. Target selection and weapon effects are out of scope.
- **Human in the loop:** the optimiser only proposes; a Commander approves; every decision is written to a tamper-evident audit log.
- **Map compliance (important for MoD judges):** external tile sets may not show India's official boundaries. Lock the map's `maxBounds` to the inland theatre and set `minZoom = 6`, so no international boundary ever renders. If a country-level view is ever needed, use Survey of India / Bhuvan-sourced layers.
- **Air-gap ready:** every external dependency (map tiles, weather API, LLM) has a local fallback, so the prototype runs fully offline.

---

## 3. Tech stack

Pin these **major versions** and don't upgrade mid-build.

### 3.1 Frontend

| Concern | Choice |
|---|---|
| Framework | **React 18.3 + Vite 5 + TypeScript 5** (strict) |
| Styling | **Tailwind CSS 3.4** + **shadcn/ui** (Radix primitives) + CSS variables for theming |
| Map | **Leaflet 1.9 + react-leaflet 4.2**; CARTO Positron (light) / Dark Matter (dark) tiles with an offline fallback |
| Charts | **Recharts 2** |
| Gantt timeline | **Custom component** (CSS grid + absolutely positioned bars) for exact fidelity to the reference |
| Tables | **TanStack Table v8** |
| Server state | **TanStack Query v5** |
| Client state | **Zustand** (COP live state, UI state, sim clock) |
| Routing | **React Router 6** |
| Forms & validation | **react-hook-form + zod** |
| Icons / toasts / motion | **lucide-react**, **sonner**, **framer-motion** |
| Dates | **date-fns + date-fns-tz** (all times displayed in Zulu/UTC) |
| Fonts (self-hosted, offline) | `@fontsource/rajdhani` (labels/headings), `@fontsource/jetbrains-mono` (numbers/time), `@fontsource/inter` (body) |
| API types | **openapi-typescript**, generated from FastAPI's OpenAPI schema |
| Tests | **Vitest + React Testing Library**, **Playwright** (e2e) |
| Lint/format | ESLint + Prettier |

### 3.2 Backend

| Concern | Choice |
|---|---|
| Language / framework | **Python 3.11 + FastAPI + Uvicorn** |
| Validation / settings | **Pydantic v2 + pydantic-settings** |
| ORM / migrations | **SQLAlchemy 2.0 + Alembic** |
| Database | **PostgreSQL 16** (Docker), with a **SQLite** fallback for zero-setup dev. Geometry stored as GeoJSON in JSON columns (no PostGIS needed) |
| Optimisation | **Google OR-Tools (CP-SAT)** |
| Machine learning | **scikit-learn, pandas, numpy, joblib** |
| Geometry | **shapely 2** + custom haversine/great-circle helpers |
| Real-time | FastAPI **WebSockets** + in-process **asyncio event bus** |
| Auth | **PyJWT** + **bcrypt**; role-based access control |
| Weather | **Open-Meteo** forecast API (free, no key) with a synthetic fallback |
| Reports | **ReportLab** (PDF) |
| LLM assistant (optional) | Provider abstraction: `none` / `anthropic` / `openai` / `ollama` (local), plus a rule-based fallback |
| HTTP client | **httpx** |
| Tests | **pytest, pytest-asyncio, httpx TestClient** |
| Lint/format | **ruff** (lint + format) |

### 3.3 DevOps

**Docker Compose** (db, backend, frontend) · **Makefile** · `.env` via `.env.example` · optional GitHub Actions running lint and tests.

---

## 4. System architecture

```text
┌──────────────────────────── SIMULATED SOURCE SYSTEMS (adapters) ─────────────────────────────┐
│ Maint-MIS │ Crew Roster │ Stores Inventory │ Met Feed │ Airspace/NOTAM │ Threat Intel A & B │ Track Feed │ Tasking │
└──────┬─────────┬───────────────┬───────────────┬────────────┬──────────────────┬──────────────┬────────┘
       ▼   raw records in heterogeneous formats (CSV rows, JSON, METAR/NOTAM-like text, IST times…)
┌──────────────────────────────────── FUSION ENGINE ───────────────────────────────────────────┐
│ normalise → ID crosswalk → entity resolution → conflict resolution → staleness → provenance   │
│                     ⇒ canonical COP state (DB + in-memory snapshot)                           │
└───────────────┬──────────────────────────────────────────────────────────────────────────────┘
                ▼  typed domain events (asyncio pub/sub bus)
 ┌──────────────┬───────────────┬───────────────┬────────────────┬────────────────┬───────────┐
 │ Alert engine │ Retask manager│ Optimiser     │ Predictive     │ Sim clock &    │ Audit     │
 │ (rules)      │ (impact anal.)│ (CP-SAT, 2-st)│ (ML + models)  │ event injector │ ledger    │
 └──────┬───────┴───────┬───────┴───────┬───────┴────────┬───────┴────────┬───────┴─────┬─────┘
        ▼               ▼               ▼                ▼                ▼             ▼
                     FastAPI REST  /api/v1/*      +      WebSocket  /ws
                                          ▼
   React SPA: KPI strip · COP map · AI allocation panel · Mission Gantt · pages · mobile field view
```

### 4.1 Key flows

**A. Plan generation:** a Planner clicks *Generate plan* → `POST /plans/generate` → feasibility matrix → CP-SAT stage A (aircraft + timing) → stage B (crew) → explanations + confidence → 3 alternatives → `plan.proposed` over WS → the AI panel shows the plan → the Commander clicks *APPROVE PLAN* → plan `APPROVED`, missions `APPROVED`, audit entry written.

**B. Dynamic retasking:** a source event (e.g. aircraft goes unserviceable) → fusion updates the COP → retask manager finds affected assignments → warm-start re-solve with a stability penalty → `retask.proposed` with a diff → Commander approves → new plan version; the previous one becomes `SUPERSEDED`.

**C. Manual override:** a Planner drags a Gantt bar or changes an assignment → `PATCH` → `validate_plan()` → violations are shown inline → accept or revert → audit entry written.

---

## 5. Repository layout

```text
vayu-cop/
├─ IMPLEMENTATION.md  AGENTS.md  CLAUDE.md  PROGRESS.md  README.md
├─ Makefile  docker-compose.yml  .env.example  .gitignore  .editorconfig
├─ docs/
│  ├─ ui-reference.png
│  ├─ architecture.md
│  └─ demo-script.md
├─ backend/
│  ├─ pyproject.toml            # deps + ruff + pytest config
│  ├─ alembic.ini  alembic/
│  ├─ data/
│  │  ├─ history/               # generated ML training CSVs
│  │  └─ models/                # trained joblib models
│  ├─ app/
│  │  ├─ main.py                # FastAPI app, lifespan (start bus, adapters, sim)
│  │  ├─ core/                  # config.py, db.py, security.py, rbac.py, events.py (bus), logging.py, errors.py
│  │  ├─ models/                # SQLAlchemy models (one file per aggregate)
│  │  ├─ schemas/               # Pydantic schemas
│  │  ├─ api/
│  │  │  ├─ deps.py
│  │  │  └─ routes/             # auth, cop, bases, aircraft, crew, stores, missions, airspace, threats,
│  │  │                         # weather, plans, retask, sim, whatif, analytics, alerts, audit,
│  │  │                         # reports, fusion, assistant, ws
│  │  ├─ services/
│  │  │  ├─ fusion/             # adapters/*.py, normaliser.py, crosswalk.py, resolver.py, staleness.py, engine.py
│  │  │  ├─ geo/                # geometry.py, routing.py, risk.py
│  │  │  ├─ optimizer/          # feasibility.py, stage_a.py, stage_b.py, profiles.py, alternatives.py,
│  │  │  │                      # explain.py, confidence.py, validate.py, service.py
│  │  │  ├─ retask/             # impact.py, manager.py, diff.py
│  │  │  ├─ predictive/         # serviceability.py, fatigue.py, weather_impact.py, mission_risk.py,
│  │  │  │                      # capacity.py, train.py
│  │  │  ├─ sim/                # clock.py, engine.py, executor.py (mission state machine), injector.py
│  │  │  ├─ whatif/             # sandbox.py, perturbations.py
│  │  │  ├─ alerts/             # rules.py, engine.py
│  │  │  ├─ audit/              # ledger.py
│  │  │  ├─ reports/            # aar.py, pdf.py
│  │  │  └─ assistant/          # provider.py, tools.py, intents.py (offline fallback)
│  │  └─ seed/
│  │     ├─ __main__.py         # python -m app.seed --reset
│  │     ├─ generator.py
│  │     ├─ history.py          # ML history CSV generator
│  │     └─ scenarios/vayu_shield.json
│  └─ tests/                    # mirrors services/ and api/
└─ frontend/
   ├─ package.json  vite.config.ts  tailwind.config.ts  tsconfig.json  index.html
   ├─ public/geo/               # offline fallback geometry (theatre outline, graticule)
   └─ src/
      ├─ main.tsx  App.tsx  routes.tsx
      ├─ styles/                # tokens.css (themes), globals.css, patterns.css (hatching)
      ├─ lib/                   # api.ts, api-types.ts (generated), ws.ts, auth.ts, time.ts, format.ts, geo.ts
      ├─ store/                 # copStore.ts, uiStore.ts, simStore.ts, alertStore.ts
      ├─ components/
      │  ├─ layout/             # AppLayout, TopBar, KpiStrip, KpiChip, ZuluClock, ThemeToggle,
      │  │                      # SideNav, ExerciseBanner, ConnectionDot
      │  ├─ map/                # CopMap, BaseLayer, AircraftLayer, RouteLayer, ThreatLayer, AirspaceLayer,
      │  │                      # WeatherLayer, Graticule, CompassRose, ScaleBar, LayerToggle,
      │  │                      # CoordReadout, RangeRingTool, EntityDrawer
      │  ├─ planner/            # AiPlanPanel, PlanCard, TradeoffBar, ConfidenceDonut, AssignmentList,
      │  │                      # UnassignedList, AlternativesDrawer, PlanDiffModal, RetaskBanner
      │  ├─ gantt/              # MissionGantt, GanttHeader, GanttRow, GanttBar, DutyBlock, NowLine, GanttLegend
      │  ├─ alerts/             # ConflictAlertsPanel, AlertItem, AlertCenter
      │  ├─ resources/          # AircraftTable, CrewTable, StoresTable, BasesTable, ProvenanceTip, RagChip
      │  ├─ missions/           # MissionQueue, MissionForm, AreaPicker
      │  ├─ analytics/          # AvailabilityForecast, ReliabilityTable, FatigueHeatmap, WeatherGoNoGo,
      │  │                      # MissionRiskBreakdown, ModelCard
      │  ├─ simulation/         # SimControls, InjectPanel, WhatIfBuilder, WhatIfCompare
      │  ├─ audit/              # AuditTable, ChainVerifyBadge
      │  ├─ reports/            # AarView
      │  └─ assistant/          # AskCopDrawer, MessageBubble, EntityChip
      ├─ pages/                 # LoginPage, CopPage, ResourcesPage, AiQueuePage, AnalyticsPage,
      │                         # SimulationPage, AuditPage, ReportsPage, SettingsPage
      └─ mobile/                # MobileShell, CrewHome, MaintenanceHome, CommanderHome
```

---

## 6. Domain model

### 6.1 Enums (shared by backend and frontend)

```text
MissionType    = CAP | RECCE | STRIKE | AIRLIFT | TANKER | AEW | SAR | HADR
Priority       = P1_FLASH | P2_IMMEDIATE | P3_PRIORITY | P4_ROUTINE
AircraftStatus = READY | TASKED | AIRBORNE | TURNAROUND | MAINTENANCE | UNSERVICEABLE
CrewRole       = PILOT | WSO | NAVIGATOR | LOADMASTER | FLIGHT_ENGINEER | MISSION_SYSTEMS_OP
CrewStatus     = AVAILABLE | ON_DUTY | AIRBORNE | RESTING | LEAVE | MEDICAL
BaseStatus     = OPEN | RESTRICTED | CLOSED
MissionStatus  = REQUESTED | PLANNED | APPROVED | AIRBORNE | ON_STATION | RTB | COMPLETED
               | CANCELLED | UNCOVERED | AT_RISK
PlanStatus     = DRAFT | PROPOSED | APPROVED | REJECTED | SUPERSEDED
PlanProfile    = BALANCED | LOW_RISK | FASTEST | RESOURCE_SAVER
AlertSeverity  = CRITICAL | WARNING | INFO
UserRole       = COMMANDER | PLANNER | MAINTENANCE | MET | INTEL | AIRCREW | ADMIN
StoreCategory  = AD_STD | RECCE_POD | GA_GENERIC | CARGO_PALLET | TANKER_PODS | AEW_NIL | SAR_KIT | HADR_KIT
ReasonCode     = ROLE_MISMATCH | NOT_READY | MAINT_DUE | BASE_CLOSED | WX_BELOW_MINIMA | OUT_OF_RANGE
               | NO_STORES | NO_QUALIFIED_CREW | TIME_CONFLICT | HIGHER_RISK | SLOWER | LOW_RELIABILITY
```

### 6.2 Provenance mixin (on every fused entity)

`source: str`, `source_ts: datetime`, `fused_ts: datetime`, `confidence: float (0–1)`, `stale: bool`

### 6.3 Entities

| Entity | Key fields |
|---|---|
| **Base** | id, name, code, lat, lon, status, runways, runway_capacity_per_15min, parking_capacity, fuel_stock_kl, closures `[{from,to,reason}]` |
| **AircraftType** | code, name, roles `[MissionType]`, cruise_kts, range_km, endurance_h, turnaround_min, crew_required `{CrewRole:int}`, compatible_stores `[StoreCategory]`, wx_minima `{ceiling_ft, visibility_km, crosswind_kt}` |
| **Aircraft** | id, tail_number, callsign, type_code, base_id, status, fuel_pct, airframe_hours, hours_since_maint, hours_to_next_maint, store_config, lat, lon, heading_deg, alt_ft, speed_kts, current_assignment_id, p_unserviceable_24h + provenance |
| **CrewMember** | id, name, rank, role, base_id, qualified_types `[code]`, currency_expiry `{type_code: date}`, status, duty_start, duty_hours_24h, duty_hours_7d, last_rest_end, fatigue_score + provenance |
| **StoreInventory** | id, base_id, category, available, reserved |
| **Mission** | id, code (e.g. `OP THUNDERBIRD`), type, priority, area_geojson, area_name (sector), earliest_start, latest_start, on_station_min, required_aircraft, required_store, requester_id, status, parent_id (for CAP relay slots), notes |
| **Airspace** | id, name (e.g. `OSCAR`), kind (`RESTRICTED`/`DANGER`/`CORRIDOR`/`MOA`), polygon_geojson, floor_ft, ceiling_ft, active_from, active_to, status (`ACTIVE`/`CLOSED`/`OPEN`) + provenance |
| **ThreatZone** | id, label (`T-1`), level, center_lat, center_lon, radius_km, mobile, first_seen, last_seen, sources `[str]` + provenance |
| **WeatherObs** | id, base_id, valid_ts, ceiling_ft, visibility_km, wind_kt, gust_kt, crosswind_kt, precip_mm, thunderstorm, is_forecast + provenance |
| **WeatherCell** | id, label (`CB-1`), center_lat, center_lon, radius_km, severity, motion_deg, motion_kts |
| **Plan** | id, version, status, profile, parent_plan_id, trigger_event_id, objective, kpis `{coverage_pct, p1_p2_coverage_pct, avg_time_to_station_min, avg_risk, avg_fuel_margin_pct, utilisation_pct, aircraft_hours}`, confidence, solve_ms, solver_status, created_by, approved_by, approved_at, reject_reason |
| **Assignment** | id, plan_id, mission_id, aircraft_id, crew_ids `[ ]`, store_category, takeoff_ts, on_station_ts, off_station_ts, land_ts, route_geojson, route_km, time_to_station_min, fuel_margin_pct, risk_score, reliability, rationale `[str]`, why_not `[{aircraft_id, reason_code, text}]`, locked |
| **UnassignedMission** | plan_id, mission_id, reason_codes, suggestion |
| **Event** | id, ts, sim_ts, source, type, severity, payload (JSON), processed |
| **Alert** | id, ts, severity, category, message, entity_refs `[{kind,id}]`, dedup_key, acknowledged_by, acknowledged_at, resolved, resolved_at |
| **AuditEntry** | id, ts, user_id, role, action, entity_kind, entity_id, before, after, reason, prev_hash, hash |
| **User** | id, username, display_name, role, password_hash |

### 6.4 Core TypeScript types (mirror the generated OpenAPI types)

```ts
export interface Assignment {
  id: string; planId: string; missionId: string; aircraftId: string; crewIds: string[];
  storeCategory: StoreCategory;
  takeoffTs: string; onStationTs: string; offStationTs: string; landTs: string;
  route: GeoJSON.LineString; routeKm: number; timeToStationMin: number;
  fuelMarginPct: number; riskScore: number; reliability: number;
  rationale: string[]; whyNot: { aircraftId: string; reasonCode: ReasonCode; text: string }[];
  locked: boolean;
}
export interface Plan {
  id: string; version: number; status: PlanStatus; profile: PlanProfile;
  kpis: PlanKpis; confidence: number; solveMs: number;
  assignments: Assignment[]; unassigned: UnassignedMission[];
}
```

---

## 7. Synthetic data & exercise scenario

Generator: `python -m app.seed --reset [--scenario vayu_shield]`. Uses **seed 26250**, so data is reproducible.

### 7.1 Bases (fictional)

| Base | Lat, Lon | Role | Units hosted |
|---|---|---|---|
| **Alpha** | 21.60, 78.20 | Main fighter hub | SU30, LCA, IL78 |
| **Bravo** | 22.90, 80.60 | Fighter & AEW | RAF, M2K, NETRA |
| **Charlie** | 19.60, 76.40 | Transport & strike | JAG, C130, MI17 |
| **Delta** | 20.40, 82.90 | Forward base | SU30, MI17, C17 |

The Blueland/Redland "line" runs along ~23.6°N in the north-east of the theatre. Mission areas use a sector grid **S1–S12**.

### 7.2 Fleet (illustrative values only)

| Code | Type | Roles | Cruise kt | Range km | Endurance h | Turnaround min | Crew required | Qty |
|---|---|---|---|---|---|---|---|---|
| SU30 | Su-30MKI | CAP, STRIKE | 480 | 3000 | 3.5 | 90 | PILOT 1, WSO 1 | 10 |
| RAF | Rafale | CAP, STRIKE, RECCE | 480 | 3500 | 4.0 | 75 | PILOT 1 | 6 |
| LCA | Tejas Mk1A | CAP | 450 | 1800 | 2.0 | 60 | PILOT 1 | 6 |
| M2K | Mirage 2000 | CAP, STRIKE | 460 | 2000 | 2.5 | 75 | PILOT 1 | 4 |
| JAG | Jaguar | STRIKE, RECCE | 420 | 1400 | 2.0 | 75 | PILOT 1 | 4 |
| C17 | C-17 Globemaster III | AIRLIFT, HADR | 450 | 4400 | 6.0 | 180 | PILOT 2, LOADMASTER 1 | 2 |
| C130 | C-130J | AIRLIFT, SAR, HADR | 320 | 3300 | 6.0 | 120 | PILOT 2, NAVIGATOR 1, LOADMASTER 1 | 3 |
| IL78 | IL-78 | TANKER | 400 | 3500 | 5.0 | 150 | PILOT 2, NAVIGATOR 1, FLIGHT_ENGINEER 1 | 2 |
| NETRA | Netra AEW&C | AEW | 380 | 2500 | 4.0 | 150 | PILOT 2, MISSION_SYSTEMS_OP 3 | 1 |
| MI17 | Mi-17V5 | SAR, HADR, AIRLIFT | 120 | 580 | 3.0 | 45 | PILOT 2, FLIGHT_ENGINEER 1 | 4 |

That is **42 aircraft**. Initial state: ~78% READY, ~10% MAINTENANCE, ~5% UNSERVICEABLE, ~7% TURNAROUND. Fuel is 60–100%. Hours to next maintenance are randomised 2–120 h, with a few deliberately low so maintenance clashes appear.

### 7.3 Crew

- For each type, generate **≈1.4× the crew needed** to fly every airframe once (expect ~120–140 crew), based at the type's bases.
- About 10% have a type currency expiring within 72 h, about 5% are on LEAVE/MEDICAL, and the rest have randomised duty/rest states.
- Names are synthetic (generated Indian first and last names), with ranks Fg Offr → Gp Capt.

### 7.4 Store inventory

Each base gets counts per `StoreCategory` matching its hosted types (e.g. Alpha: AD_STD 14, GA_GENERIC 6, TANKER_PODS 2). One base gets a deliberately low count so a `STORES_SHORTFALL` alert can be demonstrated.

### 7.5 Airspace, threats & weather

- **Airspace:** `OSCAR` (RESTRICTED, initially OPEN), `PAPA` (DANGER, ACTIVE), `CIVIL-1` (CORRIDOR), `ROMEO` (MOA training area).
- **Threat zones (fictional):** `T-1` HIGH (24.40, 82.60, r 70 km); `T-2` MED (23.90, 83.50, r 50 km); `T-3` MED (24.90, 80.80, r 45 km).
- **Weather cells:** `CB-1` (thunderstorm) starts 80 km south-west of Bravo, moving at 040°/15 kt.

### 7.6 Mission requests (12 initial, in the 12 h after sim start; sim start = **12:00Z**)

Examples: `OP THUNDERBIRD` (CAP, P2, S4, 6 h, split into 3 relay slots × 2 aircraft), `OP GARUDA EYE` (RECCE, P2, S7), `OP IRON MONSOON` (STRIKE, P3, S9, 4 aircraft, GA_GENERIC), `OP SKYBRIDGE` (AIRLIFT, P3, Alpha→Delta), `OP NECTAR` (TANKER, P3), `OP WATCHTOWER` (AEW, P2), `OP LIFELINE` (SAR standby, P2), `OP SANJEEVANI` (HADR, P4), plus 4 more routine missions.

### 7.7 Scripted disruption timeline (sim time)

| Sim time | Source | Event | Expected system reaction |
|---|---|---|---|
| 12:20Z | Maint-MIS | `SU30 #04` hydraulic snag → UNSERVICEABLE (assigned to THUNDERBIRD) | CRITICAL alert, retask proposal |
| 12:40Z | Threat Intel A + B | New threat `T-4` HIGH, reported by **two sources** with a slight position offset | Fusion merges into one zone (higher confidence); GARUDA EYE route at risk; reroute proposal |
| 13:00Z | Met Feed | `CB-1` reaches Bravo → Bravo **CLOSED 13:00–15:00Z** | Missions launching from or recovering to Bravo re-planned |
| 13:15Z | Airspace/NOTAM | `AIRSPACE OSCAR CLOSED 1315Z-1800Z` | "Re-route required" alert, routes rebuilt |
| 13:30Z | Tasking | **P1 FLASH** SAR `OP LIFELINE-2` in S6 | Lower-priority assignment displaced, with explanation |
| 14:00Z | Crew Roster | A Su-30 WSO reported medical-unfit | Crew re-pairing via stage B only |

### 7.8 ML training history

`python -m app.seed.history` writes `backend/data/history/maintenance_history.csv`: **180 days × 42 aircraft** daily rows with `hours_flown, sorties, hours_since_maint, airframe_hours, type, base, snag_next_24h/48h/72h`. Labels come from a known logistic ground truth plus noise, so the model learns sensible patterns:
`p = sigmoid(-4.0 + 0.018·hours_since_maint + 0.25·sorties_last_7d/7 + type_factor + 0.4·recent_snag + ε)`.

### 7.9 Seed users (development only)

`commander/commander123`, `planner/planner123`, `maint/maint123`, `met/met123`, `intel/intel123`, `crew/crew123`, `admin/admin123`.

---

## 8. Multi-source data fusion

### 8.1 Source adapters (each an async task emitting raw records in its *own* native format)

| Adapter | Native format (deliberately different) | Emits |
|---|---|---|
| `maint_mis` | CSV-style dict rows; tail as `"KB-604"`; IST local time strings | serviceability, snags, maintenance due |
| `crew_roster` | JSON with service numbers, duty times in IST, `"rest_ok": "Y"/"N"` | duty/rest, availability, currency |
| `stores_inv` | Per-base counts keyed by legacy store codes (`"S-AD1"`) | inventory deltas |
| `met_feed` | **METAR-like strings** (`"VABA 141300Z 22018G28KT 3000 TSRA BKN015CB"`), plus Open-Meteo JSON hourly forecast | observations, forecasts, cells |
| `airspace_notam` | **NOTAM-like text** (`"AIRSPACE OSCAR CLOSED 1315Z-1800Z"`) | airspace status windows |
| `threat_intel_a` / `threat_intel_b` | Two sensors with different coordinate formats (decimal vs DMS) and confidence scales (0–1 vs 1–5) | threat detections |
| `track_feed` | ADS-B-like position messages at 1 Hz (`{icao24, lat, lon, alt, gs, trk}`) | own aircraft positions |
| `tasking` | Mission request JSON from the UI or a scripted injector | new/changed missions |

### 8.2 Fusion pipeline (`services/fusion/engine.py`)

1. **Normalise:** parse each native format into canonical Pydantic records; convert all times to UTC; convert all units (kt, km, ft) consistently.
2. **ID crosswalk:** a registry maps source IDs (`KB-604`, `icao24=800A1F`, service numbers) to canonical IDs.
3. **Entity resolution:** two threat reports within **25 km and 10 min** are the same entity. The merged position is a confidence-weighted mean, and `confidence = 1 − Π(1 − cᵢ)`.
4. **Conflict resolution:** field-level source authority, then recency. Example: `Maint-MIS` is authoritative for `status`; `track_feed` is authoritative for position; on a tie, the newest wins.
5. **Staleness:** a per-field max age (position 10 s, status 30 min, weather 60 min, threat 20 min). Stale fields set `stale=true`, raise a `DATA_STALE` alert and render greyed in the UI.
6. **Provenance:** every canonical field records its source and timestamp. The UI tooltip reads e.g. *"Source: Maint-MIS · 2 min ago · conf 0.97"*.
7. **Publish:** persist to the DB, update the in-memory snapshot, emit domain events (`AircraftStatusChanged`, `ThreatDetected`, …) on the bus, and broadcast `cop.delta` over WS.

### 8.3 Fusion health

`GET /fusion/sources` returns per-source `last_msg_ts`, `msgs_per_min`, `errors`, `lag_s` and `status (OK/DEGRADED/DOWN)`. The UI shows these in Settings → Data Sources and as a tooltip on the WS connection dot. Each source can be **toggled off** to demonstrate degraded-mode behaviour.

---

## 9. Optimisation engine

### 9.1 Pre-processing: feasibility matrix (`feasibility.py`)

For each (aircraft `a`, mission `m`), compute eligibility and **reason codes** when ineligible:

- role ∈ type roles, else `ROLE_MISMATCH`
- status is READY/TURNAROUND, or predicted ready before `latest_start`, else `NOT_READY`
- `hours_to_next_maint ≥ sortie_hours`, else `MAINT_DUE`
- base not closed for the whole window, else `BASE_CLOSED`
- base weather ≥ type minima at takeoff/landing (forecast), else `WX_BELOW_MINIMA`
- **fuel/range model** (below), else `OUT_OF_RANGE`
- store category available at the base, else `NO_STORES`
- at least one qualified, current, rested crew set exists at the base, else `NO_QUALIFIED_CREW`

**Route & fuel model** (`geo/routing.py`, `geo/risk.py`):

- Route = great circle from base to mission area centroid. If it intersects an **active threat ring (buffered +10 km)**, a **closed airspace polygon** or a **severe weather cell**, build a detour with a visibility graph over tangent points of the buffered circles and polygon vertices, and take the shortest path (Dijkstra).
- `required_km = 2·route_km + (on_station_min/60)·cruise_kmh·0.7`
- `usable_km = range_km · 0.8` (20% reserve)
- `fuel_margin_pct = (usable_km − required_km) / usable_km · 100`; feasible if ≥ 0
- `time_to_station_min = route_km / cruise_kmh · 60`
- `risk ∈ [0,1]` = Σ over threat rings of (path length inside ring / ring diameter) × level weight (HIGH 1.0, MED 0.6, LOW 0.3) × confidence, plus weather-cell exposure, clipped to 1.

Long CAP missions are pre-split into **relay slots** so each slot fits within one sortie's endurance.

### 9.2 Stage A — aircraft & timing (CP-SAT, `stage_a.py`)

Time unit = minutes from horizon start (horizon 24 h = 1440).

**Variables**

- `x[a,m] ∈ {0,1}`, only for eligible pairs
- `u[m] ∈ {0,1}`: mission fully covered
- `t[a,m]`: takeoff time, domain = allowed takeoff windows (base closures removed via `Domain.FromIntervals`)
- `I[a,m]` = optional interval `[t, t + D[a,m] + turnaround]`, present iff `x[a,m]`. Here `D` = transit + on-station + return.

**Constraints**

- `Σₐ x[a,m] = required_aircraft[m] · u[m]` (all or nothing per mission/slot)
- `NoOverlap({I[a,m] : m})` for each aircraft
- on-station start `t + transit ∈ [earliest_start, latest_start]` (enforced if `x[a,m]`)
- landing time `t + D` ∉ the base closure windows (domain constraint)
- per base and store category: `Σ x[a,m]·[store(m)=k ∧ base(a)=b] ≤ available[b,k]`
- runway capacity: takeoffs per base per 15-min bucket ≤ `runway_capacity_per_15min` (P1)
- aggregate crew capacity per (base, type, role) per 4-h block (keeps stage B feasible)
- `locked` assignments are fixed (airborne missions, or ones pinned by a human)

**Objective (maximise, integer-scaled)**

```text
  Σₘ W_priority(m) · u[m]
− α · Σ risk[a,m]·x[a,m]
− β · Σ time_to_station[a,m]·x[a,m]
− γ · Σ (100 − fuel_margin[a,m])·x[a,m]
− ρ · Σ p_unserviceable[a]·x[a,m]
− λ · Σ changes_vs_current_plan          (retasking only)
```

`W_priority`: P1 = 10000, P2 = 4000, P3 = 1500, P4 = 500 (coverage dominates).

| Profile | α (risk) | β (time) | γ (fuel) | ρ (reliability) | λ (stability) |
|---|---|---|---|---|---|
| BALANCED | 40 | 1 | 2 | 30 | 25 |
| LOW_RISK | 120 | 0.5 | 2 | 40 | 25 |
| FASTEST | 20 | 4 | 1 | 20 | 25 |
| RESOURCE_SAVER | 40 | 1 | 6 | 60 | 25 |

All weights are editable in **Settings → Planner weights** (Commander/Admin).

**Solver:** `max_time_in_seconds = 5`, `num_workers = 8`, and `AddHint` from the current plan when retasking.

### 9.3 Stage B — crew pairing (CP-SAT, `stage_b.py`)

- For each stage-A assignment `j`, choose crew to meet `crew_required[type]` by role from the **same base**, **qualified and current** on that type.
- Duty interval = sortie `[takeoff − 60, land + 30]` (pre-brief/debrief). Crew `NoOverlap`.
- Duty limits (illustrative, configurable): flight duty period ≤ **12 h** in 24 h, ≤ **60 h** in 7 days, minimum rest **10 h** before a new duty.
- Objective: minimise Σ fatigue score + spread of workload; prefer crews already paired.
- If stage B is infeasible for assignment `j`, add a cut `x[a,m] = 0` for that pair and re-solve stage A (at most 3 iterations), then report `NO_QUALIFIED_CREW`.

```python
# stage_a.py — skeleton the agent should flesh out
from ortools.sat.python import cp_model

def solve_stage_a(ctx: PlanningContext, profile: Profile, hint: Plan | None) -> StageAResult:
    m = cp_model.CpModel()
    x, t, iv, u = {}, {}, {}, {}
    for (a, ms), f in ctx.feasible.items():                 # eligible pairs only
        x[a, ms] = m.NewBoolVar(f"x_{a}_{ms}")
        t[a, ms] = m.NewIntVarFromDomain(ctx.takeoff_domain(a, ms), f"t_{a}_{ms}")
        size = f.duration_min + ctx.turnaround(a)
        end = m.NewIntVar(0, ctx.horizon + size, f"e_{a}_{ms}")
        iv[a, ms] = m.NewOptionalIntervalVar(t[a, ms], size, end, x[a, ms], f"i_{a}_{ms}")
        m.Add(t[a, ms] + f.transit_min >= ctx.earliest(ms)).OnlyEnforceIf(x[a, ms])
        m.Add(t[a, ms] + f.transit_min <= ctx.latest(ms)).OnlyEnforceIf(x[a, ms])
    for ms in ctx.missions:
        u[ms] = m.NewBoolVar(f"u_{ms}")
        m.Add(sum(x[a, ms] for a in ctx.candidates(ms)) == ctx.required(ms) * u[ms])
    for a in ctx.aircraft:
        m.AddNoOverlap([iv[k] for k in iv if k[0] == a])
    # + stores, runway capacity, crew capacity, locks, landing-closure constraints
    m.Maximize(objective(ctx, profile, x, u, hint))
    if hint: apply_hints(m, x, t, hint)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 5; s.parameters.num_workers = 8
    status = s.Solve(m)
    return extract(s, status, x, t, u)
```

### 9.4 Alternatives (`alternatives.py`)

Generate **3 alternatives** in parallel: run the other profiles, plus a **diversity cut** (≥ 30% of assignments must differ from the best plan). Each alternative carries a KPI vector so the UI can compare risk, speed, fuel, coverage and utilisation.

### 9.5 Explainability (`explain.py`, deterministic templates, optional LLM rephrasing)

For each assignment, rank the chosen aircraft among all eligible candidates on distance, time-to-station, risk, fuel margin, reliability and crew fatigue. Emit rationale lines for the 2–4 strongest factors, e.g.:

- *"Nearest eligible aircraft — 182 km from Base Alpha (rank 1 of 5)"*
- *"Lowest threat exposure among 5 candidates (risk 0.08)"*
- *"Crew fully rested — fatigue 12/100"*
- *"Fuel margin +35%"*

**Why-not** lines for the next 2 best candidates, e.g. *"RAF #07 not chosen: maintenance due in 1.2 h (MAINT_DUE)"* or *"SU30 #02 not chosen: +14 min to station (SLOWER)"*.

**Unassigned missions** list the binding reason codes and a suggestion. The suggestion comes from a quick re-solve with the time window relaxed by +30 min or one more aircraft type allowed: *"Relaxing window by 30 min allows coverage"*.

### 9.6 Confidence (`confidence.py`)

`confidence = 100 × (0.5·solver_quality + 0.3·data_freshness + 0.2·prediction_certainty)`

- `solver_quality` = 1 if OPTIMAL, else `max(0, 1 − gap)`, where `gap = |obj − bound| / max(1, |obj|)`
- `data_freshness` = share of inputs not stale
- `prediction_certainty` = mean over assigned aircraft of `1 − binary_entropy(p_unserviceable)`

Shown in the KPI strip as **"AI ENGINE: 98.4% CONFIDENCE"**.

### 9.7 Independent validator (`validate.py`)

`validate_plan(plan, cop) -> list[Violation]` re-checks everything **without the solver**: no aircraft/crew double booking, duty limits, rest, currency, range/fuel, stores, base closures, weather minima, airspace and threat intersections. It is used for unit tests, **manual overrides** and the alert engine.

---

## 10. Dynamic retasking

### 10.1 Triggers (domain events)

`AircraftStatusChanged(→UNSERVICEABLE|MAINTENANCE)`, `ThreatDetected/Updated`, `BaseClosed`, `AirspaceClosed`, `WeatherBelowMinima`, `CrewUnavailable`, `MissionRequested(P1|P2)`, `MissionPriorityChanged`, `MissionCancelled`.

### 10.2 Impact analysis (`retask/impact.py`)

Find affected assignments in the current **APPROVED** plan:

- the aircraft or crew of the assignment is no longer available
- the route intersects a new or updated threat ring or a newly closed airspace
- the takeoff or landing base is closed during its takeoff/landing window
- base weather falls below minima for that type
- a new P1/P2 mission cannot be covered without displacement

### 10.3 Re-solve (`retask/manager.py`)

- **Freeze** unaffected AIRBORNE/ON_STATION assignments. Affected airborne ones may only be **rerouted or recalled (RTB)**, never re-launched.
- Warm-start with `AddHint` from the current plan, using **stability penalty λ** per changed assignment so the plan doesn't churn.
- Target latency **< 5 s**. Show *"Re-planned in 2.4 s"*.
- Produce a **diff**: `ADDED`, `REMOVED`, `AIRCRAFT_SWAPPED`, `RETIMED`, `REROUTED`, `CREW_CHANGED`, `RECALLED`. Each entry carries a reason that links back to the trigger event.
- KPI delta: coverage, P1/P2 coverage, risk, fuel and utilisation (before → after).

### 10.4 Modes

**Auto-propose** (default): proposals are generated automatically and await approval. **Manual**: an event raises an alert with a "Re-plan" button. **No auto-approval in any mode.**

---

## 11. Predictive analytics

| Model | Method | Inputs | Output | Used by |
|---|---|---|---|---|
| **Serviceability forecast** | `GradientBoostingClassifier` (3 heads: 24/48/72 h); calibrated with `CalibratedClassifierCV` | type, airframe_hours, hours_since_maint, sorties_7d, avg_sortie_h, recent_snag, base | `P(U/S)` per aircraft; **fleet availability curve** (expected ready count per hour for 72 h, with a band) | optimiser (ρ penalty), map badges, analytics |
| **Crew fatigue** | Rule-based score inspired by biomathematical fatigue models: hours awake/on duty + circadian dip (02:00–06:00 local) + 7-day cumulative duty | roster | fatigue 0–100 now and forecast 24 h; thresholds 60 (amber) / 80 (red) | stage B, alerts, heatmap |
| **Weather impact** | Threshold model on forecast | Open-Meteo hourly `visibility, cloud_cover_low, wind_speed_10m, wind_gusts_10m, precipitation, cape`; METAR obs; synthetic cells | per-base hourly **GO / MARGINAL / NO-GO** for each type's minima | feasibility, alerts, timeline |
| **Mission risk** | Weighted composite | route threat exposure, route weather, crew fatigue, aircraft reliability, fuel margin | 0–100 with a factor breakdown | AI panel, Gantt tooltip |
| **Sortie-generation capacity** | Simulation from availability + turnaround + crew | the above | max sorties per base per 6-h block (72 h) | analytics, what-if |

- Training: `python -m app.services.predictive.train` writes to `data/models/*.joblib` and records metrics (ROC-AUC, Brier score) in `model_card.json`.
- The Analytics page shows a **Model Card**: features, metrics, training date and the "synthetic data" caveat.
- Open-Meteo base URL: `https://api.open-meteo.com/v1/forecast`. If unreachable or `WEATHER_MODE=synthetic`, fall back to the synthetic generator automatically.

---

## 12. API & WebSocket contract

Base path **`/api/v1`**. JSON. Times in ISO-8601 UTC (`Z`). Errors use the shape `{ "error": { "code", "message", "details" } }`.
RBAC: **C**ommander, **P**lanner, **M**aintenance, Me**t**, **I**ntel, **A**ircrew, A**d**min. Read endpoints are open to all authenticated users.

### 12.1 REST

| Method & path | Purpose | Write roles |
|---|---|---|
| `POST /auth/login` · `GET /auth/me` | JWT login / current user | — |
| `GET /health` | Liveness | — |
| `GET /cop/snapshot` | Everything the map needs in one call (bases, aircraft, routes, threats, airspace, wx cells, active plan summary) | — |
| `GET /kpis` | KPI strip values | — |
| `GET /bases` · `GET /bases/{id}` · `PATCH /bases/{id}` | Bases | C, D |
| `GET /aircraft-types` | Fleet types | — |
| `GET /aircraft?base=&type=&status=` · `GET /aircraft/{id}` · `PATCH /aircraft/{id}/status` | Aircraft | M |
| `GET /crew?base=&type=&status=` · `PATCH /crew/{id}/status` | Crew | P, D |
| `GET /stores` · `PATCH /stores/{id}` | Store inventory | M, D |
| `GET/POST /missions` · `GET/PATCH/DELETE /missions/{id}` | Mission requests | P, C |
| `GET /airspace` · `PATCH /airspace/{id}` | Airspace | P, D |
| `GET /threats` · `POST /threats` · `PATCH /threats/{id}` | Threat zones | I |
| `GET /weather/bases` · `GET /weather/cells` · `GET /weather/forecast/{base_id}` | Weather | T (write via adapter) |
| `POST /plans/generate` `{profile?, mission_ids?, horizon_h?}` | Generate plan + alternatives | P, C |
| `GET /plans?status=` · `GET /plans/active` · `GET /plans/{id}` | Plans | — |
| `GET /plans/{id}/alternatives` | Alternatives with KPI vectors | — |
| `POST /plans/{id}/approve` · `POST /plans/{id}/reject {reason}` | Decision | **C only** |
| `PATCH /plans/{id}/assignments/{aid}` | Manual override → returns violations | P, C |
| `POST /plans/{id}/validate` | Run `validate_plan` | — |
| `GET /plans/{a}/diff/{b}` | Plan diff | — |
| `GET /retask/proposals` · `POST /retask/trigger {event_id?}` | Retasking | P, C |
| `GET /sim/state` · `POST /sim/start` · `POST /sim/pause` · `POST /sim/speed {x}` · `POST /sim/reset` · `GET /sim/scenarios` | Simulation clock | C, D |
| `POST /sim/inject {type, payload}` | Inject a disruption | C, D |
| `POST /whatif {perturbations[]}` | Sandbox re-plan + KPI delta | P, C |
| `GET /analytics/availability-forecast?hours=72` | Fleet availability curve | — |
| `GET /analytics/reliability` | Per-aircraft `P(U/S)` | — |
| `GET /analytics/crew-fatigue` | Fatigue matrix | — |
| `GET /analytics/weather-impact` | Go/no-go timelines | — |
| `GET /analytics/mission-risk/{mission_id}` | Risk breakdown | — |
| `GET /analytics/capacity` | Sortie capacity | — |
| `GET /analytics/model-card` | Model metadata | — |
| `GET /alerts?severity=&open=` · `POST /alerts/{id}/ack` · `POST /alerts/{id}/resolve` · `POST /alerts/{id}/fix` | Alerts (*fix* = focused retask) | P, C |
| `GET /audit?user=&action=&from=&to=` · `GET /audit/verify` | Audit ledger | — |
| `GET /reports/aar?from=&to=` · `GET /reports/aar.pdf?from=&to=` | After-action report | — |
| `GET /fusion/sources` · `PATCH /fusion/sources/{name} {enabled}` | Fusion health / toggle | D |
| `POST /assistant/query {text}` | Natural-language COP query | — |
| `GET /settings` · `PATCH /settings` | Thresholds, planner weights, duty limits | C, D |

### 12.2 WebSocket `GET /ws?token=<jwt>`

Envelope:

```json
{ "type": "aircraft.position", "ts": "2026-10-14T14:32:05Z", "seq": 1042, "payload": { } }
```

| `type` | Payload | Rate |
|---|---|---|
| `cop.delta` | changed entities `{kind, id, patch}` | on change |
| `aircraft.position` | batched `[{id, lat, lon, hdg, alt, spd, fuel}]` | 1 Hz |
| `kpi.update` | KPI strip values | 1 Hz / on change |
| `alert.new` · `alert.update` | Alert | on change |
| `plan.proposed` · `plan.approved` · `plan.rejected` | Plan summary | on change |
| `retask.proposed` | `{plan_id, diff, kpi_delta, solve_ms, trigger}` | on change |
| `sim.clock` | `{sim_ts, speed, running}` | 1 Hz |
| `fusion.health` | per-source health | 0.2 Hz |

The client reconnects with exponential backoff and refetches `/cop/snapshot` after each reconnect.

---

## 13. UI specification (from the reference image)

> Reference: `docs/ui-reference.png`. Reproduce the **layout, density and visual language**. The image shows the same screen split into **TACTICAL LIGHT** (left) and **BUNKER DARK** (right) themes; the app renders **one theme at a time** via the toggle.

### 13.1 Fixes to apply versus the reference image

- Replace non-IAF aircraft labels (*F-35A, P-38A, F333A*) with the fleet in §7.2 (e.g. `SU30 #04`, `RAF #12`, `C17 #01`).
- The KPI shows "AIRCRAFT READY: 42/39". Render it as **ready / total**, e.g. `AIRCRAFT READY: 33/42`.
- Fix typos: "rodor/rudar zones" → **"THREAT ZONE T-1 · HIGH"**; "ALLDCATION" → **ALLOCATION**; "REGCE" → **RECCE**; "Bose Alpha" → **Base Alpha**.
- The Gantt header shows "12:00" twice and duplicate `C-17 #09` rows. Generate them from data so they're correct.
- Window-chrome icons (minimise/maximise) are not needed in a web app. Keep the settings cog.

### 13.2 Layout grid (desktop ≥ 1440 px)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ ExerciseBanner: "EXERCISE VAYU SHIELD — SYNTHETIC DATA"                       (h-6)     │
├────┬─────────────────────────────────────────────────────────────────────────────────────┤
│ ☰  │ TopBar: COMMON OPERATING PICTURE (COP) | AI MISSION PLANNER   THEME: TACTICAL LIGHT / BUNKER DARK  ⚙ │ (h-14)
│    ├─────────────────────────────────────────────────────────────────────────────────────┤
│ S  │ KpiStrip: ✈ AIRCRAFT READY 33/42 │ ✈ ACTIVE SORTIES 12 │ ● CREW CURRENCY 94% │ ☀/☾ │ │ (h-12)
│ i  │           ⚠ CRITICAL ALERTS 3 │ ● AI ENGINE 98.4% CONFIDENCE │ ZULU TIME 14:32:05Z         │
│ d  ├───────────────────────────────────────────────────────────────┬─────────────────────┤
│ e  │                                                               │ AI DYNAMIC          │
│ N  │                 COP MAP (flex-1)                              │ ALLOCATION ENGINE   │
│ a  │   compass · graticule · bases · aircraft · routes ·           │ & RETASKING         │
│ v  │   threat rings · hatched airspace · wx cells · scale bar      │ (w-[360px])         │
│    │  ┌─────────────────────────┐                                  │ PlanCard, trade-offs│
│(w- │  │ LIVE CONFLICT ALERTS    │  (overlay bottom-left, w-[300px]) │ APPROVE / ALT / WHAT│
│ 20)│  └─────────────────────────┘                                  │ IF, assignments …   │
│    ├───────────────────────────────────────────────────────────────┴─────────────────────┤
│ ⚙  │ MISSION GANTT / RESOURCE TIMELINE   (h-[220px], resizable)   legend: CAP RECCE …     │
└────┴─────────────────────────────────────────────────────────────────────────────────────┘
```

- **1024–1439 px:** the right panel collapses to a toggleable drawer and the Gantt defaults to 180 px.
- **< 768 px:** redirect to the **mobile field view** (`/m`, Phase 15).

### 13.3 Design tokens (`src/styles/tokens.css`)

```css
:root, [data-theme="light"] {           /* TACTICAL LIGHT */
  --bg: #E9EEF3; --panel: #F7F9FB; --panel-2: #EEF2F6; --border: #CBD5E1;
  --text: #0F172A; --text-muted: #475569; --grid: rgba(15,23,42,.08);
  --accent: #0EA5E9; --ok: #16A34A; --warn: #D97706; --crit: #DC2626;
  --threat-fill: rgba(239,68,68,.18); --threat-stroke: #EF4444;
  --map-bg: #E5ECF2;
}
[data-theme="dark"] {                   /* BUNKER DARK */
  --bg: #070D18; --panel: #0E1626; --panel-2: #121C2F; --border: #1E2A40;
  --text: #E2E8F0; --text-muted: #8DA0B8; --grid: rgba(148,163,184,.10);
  --accent: #38BDF8; --ok: #22C55E; --warn: #F59E0B; --crit: #EF4444;
  --threat-fill: rgba(239,68,68,.16); --threat-stroke: #F87171;
  --map-bg: #0A1322;
}
/* mission-type colours (same in both themes) */
:root {
  --m-cap: #3B82F6; --m-recce: #8B5CF6; --m-strike: #F97316; --m-airlift: #14B8A6;
  --m-tanker: #06B6D4; --m-aew: #EAB308; --m-sar: #10B981; --m-hadr: #84CC16;
}
```

- **Typography:** labels and headings in Rajdhani 600, UPPERCASE, `letter-spacing: .06em`; numbers, times and callsigns in JetBrains Mono; body in Inter 14 px.
- **Panels:** 1 px `--border`, radius 6 px, subtle inner glow in dark mode (`box-shadow: inset 0 0 0 1px rgba(56,189,248,.06)`).
- **Hatching** (`patterns.css`): a 45° repeating-linear-gradient for restricted airspace, crew rest blocks and maintenance blocks.
- **Theme toggle:** `AUTO / DAY / NIGHT`. AUTO picks DAY between 06:00 and 18:00 local, as in the reference ("DAY MODE (06:00–18:00)" / "NIGHT / C2 BUNKER MODE"). The choice persists in `localStorage` with try/catch. The map tiles switch with the theme.

### 13.4 Components (behaviour spec)

**TopBar.** Hamburger (collapses the SideNav labels), title, theme segmented control, settings cog, user badge (name · role), logout, WS connection dot (green/amber/red, with a tooltip listing source health).

**KpiStrip / KpiChip.** Props: `icon, label, value, tone (ok|warn|crit|info), onClick`. Clicking a chip filters the map and tables (e.g. *CRITICAL ALERTS* opens the alert drawer; *AIRCRAFT READY* filters to ready aircraft). Values come from `kpi.update`.

**ZuluClock.** Shows `ZULU TIME HH:MM:SSZ`. It uses sim time when the sim is running, plus an "×10" speed badge.

**SideNav.** Items: COP MAP `/`, RESOURCE STATUS `/resources`, AI QUEUE `/queue`, PREDICTIVE ANALYTICS `/analytics`, SIMULATION `/simulation`, AUDIT LOG `/audit`, REPORTS `/reports`, with the settings cog at the bottom (`/settings`). Icon above an uppercase label, with an active state shown as an accent left border and panel-2 background.

**CopMap (react-leaflet)**

- Tiles: CARTO light/dark by theme, with attribution "© OpenStreetMap contributors © CARTO". **Offline fallback:** no tiles, just `--map-bg` plus the graticule and theatre outline from `public/geo/`.
- `maxBounds` = theatre box padded by 1°, `minZoom` 6, `maxZoom` 11.
- **Graticule** with lat/lon labels on the edges (as in the reference), **CompassRose** (top-left), **ScaleBar** (bottom-right), **CoordReadout** (cursor lat/lon in DMS).
- **BaseLayer:** a runway glyph inside a status ring (OPEN green, RESTRICTED amber, CLOSED red with a pulsing animation) and a label badge (`BASE ALPHA`).
- **AircraftLayer:** a plane icon rotated to heading; colour by status (READY `--ok`, AIRBORNE `--accent`, U/S `--crit`); label chip `SU30 #04`; smooth interpolation between 1 Hz updates; a small amber dot badge if `P(U/S 24h) > 0.4`. Use the canvas renderer if the marker count exceeds 100.
- **RouteLayer:** planned routes dashed, airborne solid, flown track dotted; coloured by mission type. Hovering an assignment in the AI panel or Gantt highlights its route.
- **ThreatLayer:** concentric rings (inner solid, outer dashed) in `--threat-fill`/`--threat-stroke`, with label `THREAT ZONE T-1 · HIGH · conf 0.92`. New threats pulse for 10 s.
- **AirspaceLayer:** hatched polygons, label `AIRSPACE OSCAR — CLOSED 1315–1800Z`.
- **WeatherLayer:** translucent cells drifting with their motion vector, plus base weather badges (GO/MARGINAL/NO-GO).
- **LayerToggle:** checkboxes for Bases, Aircraft, Routes, Threats, Airspace, Weather, Sector grid, Labels.
- **RangeRingTool:** click a base to show reachable rings for a selected type (range and the 30/60 min transit ring).
- **EntityDrawer:** clicking any entity opens a details drawer with provenance per field, a mini timeline and actions (e.g. "Mark U/S" for MAINTENANCE).

**ConflictAlertsPanel** (map overlay, bottom-left, as in the reference). Title `LIVE CONFLICT ALERTS`, a collapse icon and a scrollable list. Each item has a severity left-border and a bold header (`CONFLICT ALERT:` / `RE-ROUTE REQUIRED:`), a message (*"FLIGHT PATH OF SU30 #04 EN ROUTE THREAT ZONE T-4 — 14:50Z"*) and actions **Locate · Ack · Fix with AI**.

**AiPlanPanel** (right, as in the reference)

- Header: `AI DYNAMIC ALLOCATION ENGINE & RETASKING`.
- **RetaskBanner** (when a proposal exists): amber, *"RETASK PROPOSED — 3 changes · re-planned in 2.4 s"* with a **Review** button that opens the PlanDiffModal.
- **PlanCard:** `AI OPTIMIZED PLAN:` then the operation name (`OP THUNDERBIRD — CAP PATROL`). A mission selector cycles through assignments in the plan.
  - `RECOMMENDATION RATIONALE`: the rationale lines from §9.5.
  - `TRADE-OFF SCORES`: **RISK** (bar + LOW/MED/HIGH), **SPEED** ("12m TO STATION"), **FUEL MARGIN** (+35%). The **ConfidenceDonut** on the right shows mission risk/confidence.
  - Expandable "Why not other aircraft?".
- Buttons: **APPROVE PLAN** (green, full width; disabled unless the role is COMMANDER; asks for confirmation), **ALTERNATIVE PLANS (3)** (outline), **SIMULATE WHAT-IF** (outline, accent).
- Below: **AssignmentList** (compact rows: mission chip, aircraft, crew, T/O time, risk dot) and **UnassignedList** (reason codes + suggestion + "Apply suggestion").
- **Generate plan** split-button with profile choice (Planner/Commander).

**AlternativesDrawer.** Three plan cards side by side with a KPI table (coverage, P1/P2 coverage, avg time to station, avg risk, avg fuel margin, utilisation, confidence), a small grouped bar chart, and "Select this plan" (makes it the proposal).

**PlanDiffModal.** Change list grouped by type, colour-coded (added green, removed red, changed amber). KPI before → after. A map toggle between *Before* and *After* routes. Buttons **Approve retask** (Commander) and **Reject** (with a reason).

**MissionGantt** (bottom, as in the reference)

- Title `MISSION GANTT / RESOURCE TIMELINE`, legend on the right (CAP, RECCE, STRIKE, … plus *CREW DUTY CYCLES* hatched).
- Columns: **TAIL NUMB.** (with a plane icon and a type-colour left stripe) · **CREW** (names, truncated, with a tooltip) · **timeline**.
- Bars coloured by mission type, labelled with the type and operation code. Crew duty/rest blocks are hatched; maintenance blocks are grey hatched; conflicts get a red outline; a **NowLine** in accent colour.
- Zoom 6 h / 12 h / 24 h; horizontal scroll; sticky first two columns; group rows by base.
- Click a bar to select the assignment (map focus + PlanCard). **Drag a bar** (Planner/Commander) to retime it, or drop it on another row to swap the aircraft. This calls `PATCH …/assignments/{aid}`; violations show in a popover with **Keep anyway (logs override)** or **Revert**.

### 13.5 Pages

| Page | Contents |
|---|---|
| **Resource Status** | Tabs **Aircraft · Crew · Stores · Bases**. TanStack tables with sorting, filters, search, RAG chips and provenance tooltips. Aircraft: status, fuel, hours to maintenance, `P(U/S 24h)`, store config, current mission. Crew: role, quals, currency expiry (amber < 72 h), duty hours, fatigue bar, status. Stores: per base and category, available/reserved. Bases: status, closures, weather GO/NO-GO, runway capacity. Inline status edits for permitted roles |
| **AI Queue** | Mission requests grouped by priority, then status. A **MissionForm** (type, priority, area via map click/draw, window, on-station time, aircraft count, store category). Actions: edit, cancel, change priority, generate plan for selected missions. Shows relay-slot children for CAP |
| **Predictive Analytics** | Fleet availability forecast (72 h, by type, with confidence band); top-10 reliability risk table; crew fatigue heatmap (crew × next 24 h); base weather GO/NO-GO timeline; mission risk breakdown (stacked bar per mission); sortie capacity per base; **Model Card** |
| **Simulation** | Sim controls (start/pause/reset, speed 1×/5×/10×/30×/60×), scenario picker, the scripted timeline (with each event's status), a **manual inject panel** (one button per disruption type plus a payload form), and the **What-If Builder** with comparison |
| **Audit Log** | Filterable table (time, user, role, action, entity, reason) with expandable before/after JSON diff and a **Verify chain** badge |
| **Reports** | After-action report for a time range: planned vs actual Gantt, coverage, utilisation by type/base, re-plan count and latency, alert summary, planning time saved; **Export PDF** |
| **Settings** | Planner weights per profile, duty limits, alert thresholds, data-source toggles (fusion health), theme, LLM provider status, user list (Admin) |

### 13.6 Global UX rules

- Keyboard: `Ctrl/⌘ + K` opens **ASK COP**; `G` generates a plan; `A` opens the alert center; `1`–`6` inject scripted events in demo mode.
- Every async action shows a loading state and finishes with a sonner toast.
- Every list has empty and error states.
- Focus rings are visible; text contrast meets WCAG AA in both themes.
- All times are shown in Zulu (`HH:MMZ`); hovering shows IST.

---

## 14. Alerts & conflict-detection rules

The engine (`alerts/engine.py`) runs on every relevant event **and** sweeps every 10 s. Alerts are de-duplicated by `dedup_key` and auto-resolve when the condition clears.

| Category | Condition | Severity | Example message |
|---|---|---|---|
| `ROUTE_THREAT` | A planned or airborne route intersects an active threat ring | CRITICAL | FLIGHT PATH OF SU30 #04 EN ROUTE THREAT ZONE T-4 — 14:50Z |
| `AIRSPACE_CLOSED` | A route crosses an airspace closed during its transit | CRITICAL | RE-ROUTE REQUIRED: AIRSPACE OSCAR CLOSED |
| `ASSET_LOST` | The assigned aircraft goes U/S or into MAINTENANCE | CRITICAL | SU30 #04 U/S — OP THUNDERBIRD SLOT 2 UNCOVERED |
| `MISSION_UNCOVERED` | A P1/P2 mission is not covered | CRITICAL (P1) / WARNING (P2) | P1 FLASH OP LIFELINE-2 HAS NO ASSIGNED ASSET |
| `BASE_WX` | A base is below minima at a planned takeoff/landing | CRITICAL | BASE BRAVO NO-GO 13:00–15:00Z (TSRA) |
| `DOUBLE_BOOKING` | Aircraft or crew overlap (after a manual override) | CRITICAL | C130 #02 DOUBLE-BOOKED 15:10–16:40Z |
| `CREW_DUTY` | Duty ≥ 85% of the limit (WARNING) or exceeded (CRITICAL) | WARNING/CRITICAL | FLT LT R. MENON DUTY 10.6/12 H |
| `CREW_CURRENCY` | Assigned crew currency expired or expiring before the sortie | WARNING | SQN LDR A. RAO SU30 CURRENCY EXPIRES 16:00Z |
| `MAINT_DUE` | Maintenance due before the assignment ends | WARNING | RAF #07 MAINT DUE IN 1.2 H |
| `FUEL_MARGIN` | Fuel margin < 15% | WARNING | JAG #03 FUEL MARGIN 11% |
| `STORES_SHORTFALL` | Planned demand > available | WARNING | BASE DELTA GA_GENERIC SHORT BY 2 |
| `DATA_STALE` | A source has gone stale | WARNING | THREAT INTEL B — NO DATA FOR 22 MIN |
| `FATIGUE` | Assigned crew fatigue ≥ 80 | WARNING | CREW FATIGUE HIGH ON OP NECTAR |

Every alert has `entity_refs`, so **Locate** can focus the map and **Fix with AI** (`POST /alerts/{id}/fix`) can trigger a focused retask.

---

## 15. Phase-wise implementation plan

```text
P0 Foundation ─► P1 Data & scenario ─► P2 API & auth ─► P3 Fusion & realtime
                                                         │
P4 UI shell ─► P5 COP map ─► P6 Resources & queue ◄──────┘
                                   │
                    P7 Optimiser ─► P8 AI panel & Gantt ─► P9 Sim & retasking ─► P10 Alerts
                                                                                    │
            P11 Predictive ─► P12 What-if ─► P13 Audit & AAR ─► P14 Assistant ─► P15 Mobile ─► P16 Hardening & demo
```

---

### Phase 0 — Foundation & tooling · **P0**

**Goal:** an empty but runnable full-stack skeleton.

- [ ] `git init`; add `.gitignore` (Python, Node, `.env`, `data/models`, `*.db`), `.editorconfig`, `README.md` stub.
- [ ] Backend: `pyproject.toml` with the deps from §3.2; `app/main.py` with a lifespan hook; `GET /api/v1/health → {"status":"ok","version":...}`; `core/config.py` (pydantic-settings); structured logging; CORS for `http://localhost:5173`.
- [ ] Frontend: Vite React TS; Tailwind + shadcn/ui init; `@/` path alias; ESLint + Prettier; Vite proxy `/api` and `/ws` → `http://localhost:8000`.
- [ ] `docker-compose.yml`: `db` (postgres:16 with healthcheck), `backend` (uvicorn --reload), `frontend` (vite dev).
- [ ] `.env.example`:
  ```env
  DATABASE_URL=postgresql+psycopg://vayu:vayu@localhost:5432/vayu   # or sqlite:///./vayu.db
  JWT_SECRET=change-me
  JWT_EXPIRE_MIN=720
  WEATHER_MODE=auto            # auto | live | synthetic
  MAP_TILES=auto               # auto | online | offline
  LLM_PROVIDER=none            # none | anthropic | openai | ollama
  LLM_MODEL=
  LLM_API_KEY=
  OLLAMA_URL=http://localhost:11434
  SIM_AUTOSTART=false
  SIM_SPEED=10
  ```
- [ ] `Makefile` targets: `setup`, `dev` (backend + frontend concurrently), `seed`, `train`, `test`, `test-backend`, `test-frontend`, `e2e`, `lint`, `fmt`, `api-types`, `demo`, `docker-up`.
- [ ] Add `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `docs/ui-reference.png`.

**Acceptance:** `make setup && make dev` serves the placeholder at `:5173`, and `curl :8000/api/v1/health` returns ok. `make lint` passes.

**Agent prompt:** *"Implement Phase 0 of IMPLEMENTATION.md exactly: scaffold backend and frontend with the pinned stack, docker-compose, Makefile and .env.example. Verify with make dev and the health endpoint."*

---

### Phase 1 — Domain model, database & synthetic scenario · **P0**

**Goal:** a realistic, reproducible exercise world in the DB.

- [ ] SQLAlchemy models for **every entity in §6.3** (with the provenance mixin); enums from §6.1.
- [ ] Alembic setup and the first migration. SQLite fallback works through `DATABASE_URL`.
- [ ] Pydantic schemas (`Read`/`Create`/`Update`) per entity, with camelCase aliases for JSON.
- [ ] `seed/scenarios/vayu_shield.json` containing **all** of §7.1–7.7 (bases, types, airspace polygons, threats, weather cells, missions, disruption script).
- [ ] `seed/generator.py` (seed 26250) creating aircraft, crew, inventory and users per §7.
- [ ] `seed/history.py` creating the ML history CSV per §7.8.
- [ ] CLI: `python -m app.seed --reset` and `make seed`.
- [ ] Tests: entity counts; every aircraft at a valid base; every crew member qualified on a type present at their base; all coordinates inside the theatre box; mission windows valid; scenario JSON validates against its Pydantic schema.

**Acceptance:** `make seed` prints a summary table (42 aircraft, ~130 crew, 12 missions, 4 bases, 3 threats, 4 airspaces); tests pass.

**Agent prompt:** *"Implement Phase 1: models, migration, scenario JSON and generators exactly per §6–§7 of IMPLEMENTATION.md. Make the seed reproducible with seed 26250 and add the listed tests."*

---

### Phase 2 — Core API, auth & RBAC · **P0**

**Goal:** a typed, secured API over the COP.

- [ ] JWT login/me; bcrypt hashing; `require_roles(*roles)` dependency; 401/403 handling.
- [ ] All read endpoints and the CRUD endpoints in §12.1 for bases, types, aircraft, crew, stores, missions, airspace, threats and weather (filters + pagination).
- [ ] `GET /cop/snapshot` (single optimised query set) and `GET /kpis`.
- [ ] Uniform error model and request-ID middleware.
- [ ] `make api-types` runs `openapi-typescript http://localhost:8000/openapi.json -o frontend/src/lib/api-types.ts`.
- [ ] Tests: auth flow, RBAC denial (e.g. AIRCREW cannot PATCH aircraft status), snapshot shape, filters.

**Acceptance:** Swagger at `/docs` lists all Phase 2 endpoints; snapshot < 300 ms on seed data; tests pass.

---

### Phase 3 — Multi-source data fusion & real-time bus · **P0**

**Goal:** demonstrate genuine multi-source fusion with live updates.

- [ ] `core/events.py`: a typed asyncio pub/sub bus (`publish`, `subscribe(event_type)`).
- [ ] `fusion/adapters/base.py` plus the **8 adapters** in §8.1, each emitting its own native raw format (METAR/NOTAM-like strings, IST times, DMS coordinates, legacy codes).
- [ ] `normaliser.py`, `crosswalk.py`, `resolver.py` (entity resolution + confidence combination + source authority), `staleness.py` (5 s sweep), provenance stamping, `engine.py` orchestration.
- [ ] Open-Meteo client with timeout and a synthetic fallback (`WEATHER_MODE`).
- [ ] WebSocket `/ws`: JWT auth, connection manager, envelope with `seq`, batching of `aircraft.position` at 1 Hz, plus `cop.delta`, `kpi.update` and `fusion.health`.
- [ ] `GET/PATCH /fusion/sources` (health + enable/disable).
- [ ] Tests: METAR and NOTAM parsing; DMS → decimal; duplicate threat merge (two sources → one zone with higher confidence); authority conflict (track feed can't override maintenance status); staleness flagging.

**Acceptance:** with adapters running, a WS client receives position batches at 1 Hz; disabling `threat_intel_b` produces `DATA_STALE` after its max age.

---

### Phase 4 — UI shell & design system · **P0**

**Goal:** the reference image's frame, live.

- [ ] `tokens.css`, `patterns.css` and Tailwind theme mapping to the CSS variables; self-hosted fonts (§13.3).
- [ ] `AppLayout` grid exactly per §13.2; `ExerciseBanner`, `TopBar`, `KpiStrip` + `KpiChip`, `ZuluClock`, `ThemeToggle` (AUTO/DAY/NIGHT), `SideNav`, `ConnectionDot`.
- [ ] Login page (dark tactical styling), auth context, route guard, role badge.
- [ ] `lib/api.ts` (fetch wrapper + typed endpoints), TanStack Query setup, `lib/ws.ts` (reconnect + dispatch into Zustand stores).
- [ ] Routes and placeholders for every page in §13.5; mobile redirect stub.
- [ ] Vitest: KpiChip renders tones; ThemeToggle switches `data-theme`; ZuluClock formatting.

**Acceptance:** side by side with `docs/ui-reference.png`, the frame (top bar, KPI strip, side nav, right panel area, bottom Gantt area) matches in both themes. KPIs show live backend values. The WS dot is green.

---

### Phase 5 — COP map · **P0**

**Goal:** the live operational picture.

- [ ] `CopMap` with theme-matched tiles, offline fallback, `maxBounds`/`minZoom` per §2.
- [ ] All layers from §13.4: Base, Aircraft (rotation, interpolation, labels), Route, Threat (rings + pulse), Airspace (hatched), Weather (drifting cells + base badges), Graticule with edge labels, CompassRose, ScaleBar, CoordReadout, LayerToggle, RangeRingTool.
- [ ] `EntityDrawer` with per-field provenance.
- [ ] `ConflictAlertsPanel` overlay bound to `GET /alerts` (live updates arrive in Phase 10).
- [ ] Performance: 42+ moving aircraft at 60 fps (memoised markers, canvas renderer fallback).

**Acceptance:** aircraft move smoothly; clicking any entity shows its details and provenance; switching the theme switches tiles; offline mode (`MAP_TILES=offline`) still renders a usable map.

---

### Phase 6 — Resource status boards & mission queue · **P0**

- [ ] Resources page: four tabs with TanStack tables per §13.5; RAG chips; provenance tooltips; inline status edits (role-gated) that emit events through a `manual` fusion source.
- [ ] AI Queue page: priority/status grouping, `MissionForm` with zod validation and `AreaPicker` (click or draw on a mini-map), edit/cancel/priority change; CAP relay-slot auto-split shown as children.
- [ ] Changing a mission or status updates the map, KPIs and other clients live through WS.

**Acceptance:** creating a P2 CAP mission of 6 h shows 3 relay slots; marking an aircraft U/S in Resources changes its map icon and the KPI within 1 s.

---

### Phase 7 — Optimisation engine · **P0** (the core)

- [ ] `geo/geometry.py`, `geo/routing.py` (visibility-graph detours around buffered threats, closed airspace and severe cells), `geo/risk.py`.
- [ ] `feasibility.py` with reason codes (§9.1).
- [ ] `stage_a.py` and `stage_b.py` (§9.2–9.3) with the decomposition loop; `profiles.py`; `alternatives.py`; `explain.py`; `confidence.py`; `validate.py`; `service.py`.
- [ ] Endpoints: `POST /plans/generate`, `GET /plans*`, `/alternatives`, `/validate`, `/diff`; persist the plan and assignments; broadcast `plan.proposed`.
- [ ] Record `solve_ms`; expose `planning_time` metrics for reports.
- [ ] Tests (each plan checked with `validate_plan`): no double booking; duty and rest respected; range/fuel feasible; base closure respected; stores respected; P1 is covered before P4 under scarcity; LOW_RISK yields lower average risk than FASTEST on the seed scenario; explanation and why-not lines present.

**Acceptance:** on the seed scenario (42 aircraft, 12 missions + slots), plan generation plus 3 alternatives completes in **< 5 s** with zero validator violations.

---

### Phase 8 — AI plan panel, approval flow & mission Gantt · **P0**

- [ ] `AiPlanPanel`, `PlanCard`, `TradeoffBar`, `ConfidenceDonut`, `AssignmentList`, `UnassignedList` (with "Apply suggestion"), Generate split-button (§13.4).
- [ ] `AlternativesDrawer` with KPI comparison and "Select this plan".
- [ ] Approve/reject flow (Commander only, confirm dialog, reject reason); mission statuses update; routes render on the map with hover linking.
- [ ] `MissionGantt` exactly as in §13.4, including drag-to-retime and drop-to-swap → `PATCH` → violation popover → keep (logged override) or revert.
- [ ] Vitest: GanttBar positioning maths; approve button disabled for PLANNER.

**Acceptance:** the full loop *Generate → review rationale → compare alternatives → Approve* works in the UI; the Gantt matches the reference visually; dragging a bar into a crew rest block shows a `CREW_DUTY` violation.

---

### Phase 9 — Simulation engine & dynamic retasking · **P0**

- [ ] `sim/clock.py` (start/pause/speed/reset; sim time drives Zulu).
- [ ] `sim/executor.py`: the mission state machine `APPROVED → AIRBORNE → ON_STATION → RTB → COMPLETED`, moving aircraft along route geometry, burning fuel, accruing crew duty, applying turnaround, writing actual times (for the after-action report).
- [ ] `sim/injector.py`: scripted timeline from the scenario plus manual injects via `POST /sim/inject`.
- [ ] `retask/impact.py`, `retask/manager.py`, `retask/diff.py` per §10; `retask.proposed` broadcast; latency measured.
- [ ] UI: Simulation page controls and timeline; `RetaskBanner`; `PlanDiffModal` with before/after map toggle; approve/reject retask.
- [ ] Tests: each of the 6 scripted events produces a proposal that passes `validate_plan`; unaffected assignments stay unchanged (stability); airborne assignments are only rerouted or recalled.

**Acceptance:** run the demo timeline at 10×. Every disruption results in an alert plus a retask proposal within 5 s, and approving it updates the map, Gantt and KPIs live.

---

### Phase 10 — Alerts & conflict detection · **P0**

- [ ] `alerts/rules.py` implementing **every rule in §14**; `alerts/engine.py` (event-driven + 10 s sweep, dedup, auto-resolve).
- [ ] Endpoints: list, ack, resolve, fix (focused retask).
- [ ] UI: live `ConflictAlertsPanel`, CRITICAL toasts, the **CRITICAL ALERTS** KPI, an `AlertCenter` drawer with filters, and Locate / Ack / Fix with AI actions.
- [ ] Tests for each rule (positive and negative cases).

**Acceptance:** the 12:40Z threat event shows *"FLIGHT PATH … EN ROUTE THREAT ZONE T-4"*. Clicking **Fix with AI** produces a reroute proposal; approving it auto-resolves the alert.

> ✅ **MVP complete at this point** (internal hackathon ready).

---

### Phase 11 — Predictive analytics · **P1**

- [ ] `predictive/train.py` (serviceability models + calibration + model card); `make train`.
- [ ] `serviceability.py`, `fatigue.py`, `weather_impact.py`, `mission_risk.py`, `capacity.py` per §11.
- [ ] Wire into the optimiser (ρ penalty, predicted ready time), stage B (fatigue), feasibility (weather), alerts (`FATIGUE`) and map badges.
- [ ] Analytics page: all charts and tables in §13.5 plus the Model Card.
- [ ] Tests: model trains with ROC-AUC > 0.75 on held-out synthetic data; the fatigue score rises in the circadian low; a NO-GO window matches the forecast thresholds.

**Acceptance:** the Analytics page renders a 72 h availability forecast with a band, and high-risk aircraft show amber map badges and get deprioritised by the optimiser.

---

### Phase 12 — What-if simulator · **P1**

- [ ] `whatif/perturbations.py`: `LOSE_BASE`, `AIRCRAFT_UNSERVICEABLE {type, n}`, `MISSION_SURGE {pct}`, `THREAT_ADD`, `WEATHER_CLOSE_BASE {base, from, to}`, `CREW_SHORTAGE {pct}`, `STORES_SHORTAGE {base, category, pct}`.
- [ ] `whatif/sandbox.py`: deep-copy the COP state, apply the perturbations, solve, and return the plan and KPI delta. **No persistence and no broadcast.**
- [ ] UI: a `WhatIfBuilder` (toggles, sliders, base picker) on the Simulation page and from **SIMULATE WHAT-IF** in the AI panel; `WhatIfCompare` (baseline vs scenario KPI cards, uncovered missions list, delta chart); *Save scenario* to rerun later.

**Acceptance:** "Lose Base Bravo + 20% mission surge" returns in < 6 s with a clear coverage drop and the list of missions lost.

---

### Phase 13 — Audit ledger & after-action reports · **P1**

- [ ] `audit/ledger.py`: append-only, `hash = sha256(prev_hash + canonical_json(entry))`; record login, plan generate/approve/reject, overrides, mission CRUD, status edits, alert ack/fix, sim injects and settings changes.
- [ ] `GET /audit/verify` walks the chain and reports the first broken link.
- [ ] Audit page with filters, a JSON diff view and the verify badge.
- [ ] `reports/aar.py` + `pdf.py`: planned vs actual, coverage, utilisation by type and base, re-plan count and latency, alerts summary, **planning time saved** (manual baseline from settings vs solver time).
- [ ] Reports page + PDF export.

**Acceptance:** tampering with one audit row in the DB makes Verify show ❌ at that entry. The PDF report downloads with charts.

---

### Phase 14 — AI assistant "ASK COP" · **P1**

- [ ] `assistant/provider.py`: an LLM provider abstraction (`LLM_PROVIDER` env) using tool/function calling.
- [ ] `assistant/tools.py`, wrapping services: `find_aircraft(filters)`, `aircraft_reachable(area, minutes, type?)`, `mission_status(code)`, `explain_assignment(mission)`, `open_alerts(severity?)`, `base_weather(base)`, `fleet_forecast(hours)`, `propose_plan(profile)` (creates a proposal only).
- [ ] `assistant/intents.py`: an **offline rule-based fallback** covering at least these queries:
  - "Which aircraft can reach Sector 4 in 30 minutes?"
  - "Why was SU30 #04 assigned to Thunderbird?"
  - "What happens if Base Bravo closes?" (routes to what-if)
  - "Show critical alerts"
  - "How many Su-30s are ready at Alpha?"
  - "Weather at Bravo for the next 3 hours"
  - "Generate a low-risk plan"
  - "Which crew are near duty limits?"
  - "Fleet availability tomorrow"
  - "Status of Op Lifeline-2"
- [ ] UI: `AskCopDrawer` (`Ctrl/⌘ + K`). Answers include **entity chips** that focus the map, and action buttons (e.g. *Generate low-risk plan*). Nothing executes or approves without a click.

**Acceptance:** with `LLM_PROVIDER=none`, all 10 queries above return correct, data-backed answers.

---

### Phase 15 — Mobile field view · **P2**

- [ ] `/m` shell (390 px first), with a role-based home:
  - **AIRCREW:** next sortie card (mission, aircraft, T/O, route mini-map, weather), rest/duty status, "Acknowledge tasking".
  - **MAINTENANCE:** aircraft list for their base, one-tap status change with a snag note (goes through the `manual` fusion source → triggers retasking).
  - **COMMANDER:** critical alerts plus pending approvals, with Approve/Reject.
- [ ] `vite-plugin-pwa` manifest and an offline shell.

**Acceptance:** in Chrome devtools at iPhone size, a maintenance user marking an aircraft U/S triggers a retask proposal on the desktop COP.

---

### Phase 16 — Hardening, testing, performance & demo packaging · **P0 for the finale**

- [ ] Backend test coverage ≥ 75% on `services/`; frontend component tests for the planner, Gantt and alerts.
- [ ] **Playwright e2e:** login → generate → approve → inject U/S → approve retask → verify Gantt/map updated → export the report.
- [ ] Error boundaries, skeleton loaders, empty states, keyboard navigation, contrast checks.
- [ ] Performance pass against §18 targets.
- [ ] `make demo`: reset, seed, train if needed, then start the sim at 10× with scripted disruptions enabled; presenter hotkeys `1`–`6`.
- [ ] Production Docker: frontend built and served by nginx; backend with uvicorn workers; an `OFFLINE.md` covering air-gapped install (wheel/npm caches, offline tiles, Ollama).
- [ ] README with screenshots of both themes, the architecture diagram, run instructions and the feature list; `docs/demo-script.md` (§16).

**Acceptance:** a fresh clone → `docker compose up --build` → the full demo script in §16 runs without errors in under 7 minutes.

---

## 16. Demo script for judges

1. **Login as Commander.** Night (Bunker Dark) theme. Point out the exercise banner and the live KPI strip.
2. **COP map.** Bases, 42 aircraft moving, threat rings, hatched airspace, a weather cell drifting. Hover an aircraft to show provenance ("fused from Maint-MIS + Track Feed").
3. **Data fusion.** Settings → Data Sources: 8 heterogeneous feeds. Turn off Threat Intel B and watch the `DATA_STALE` alert appear.
4. **AI Queue.** 12 mission requests. Click **Generate plan**: done in ~2 s. The AI panel shows the rationale, trade-offs and confidence. Open **Alternative Plans (3)** and compare LOW_RISK vs FASTEST.
5. **Approve.** The Gantt fills and the routes are drawn.
6. **Start sim at 10×.** Hotkey `1`: SU30 #04 goes U/S. CRITICAL alert → retask proposal in < 5 s → open the diff → approve.
7. Hotkey `2`: new threat T-4, reported by two sensors and fused into one. The route-threat alert appears; **Fix with AI** reroutes around it.
8. Hotkey `5`: **P1 FLASH SAR**. The optimiser displaces a P4 mission and explains why.
9. **What-if:** "Lose Base Bravo + 20% surge" shows the coverage impact.
10. **Predictive analytics:** 72 h availability forecast and the aircraft likely to go U/S tomorrow.
11. **ASK COP:** "Which aircraft can reach Sector 4 in 30 minutes?"
12. **Audit + after-action report:** verify the chain, export the PDF, and show **planning time: manual baseline vs seconds**.

---

## 17. KPIs & evaluation

| Metric | How it's measured | Shown where |
|---|---|---|
| Planning time | Solver `solve_ms` vs a **manual baseline you time yourselves** (team members plan the seed scenario by hand); record both honestly | Reports, demo |
| Re-plan latency | Trigger event → proposal ready | RetaskBanner, Reports |
| Mission coverage | % of missions/slots covered; P1/P2 coverage separately | Plan KPIs |
| Plan stability | # of changed assignments per retask | Diff modal, Reports |
| Risk exposure | Mean / max route risk | Trade-offs |
| Utilisation | Aircraft hours tasked ÷ available hours | Reports |
| Fuel margin | Mean margin across assignments | Trade-offs |
| Prediction quality | ROC-AUC, Brier score (synthetic hold-out) | Model card |
| Data freshness | % of fields not stale | Confidence, fusion health |

---

## 18. Testing & performance targets

| Area | Target |
|---|---|
| `/cop/snapshot` | < 300 ms |
| Plan generation (42 aircraft, ~20 missions/slots, + 3 alternatives) | < 5 s |
| Retask proposal | < 5 s from event |
| What-if | < 6 s |
| WS position updates | 1 Hz; UI at 60 fps with ≥ 50 aircraft |
| First load (prod build) | < 3 s on a laptop |
| Backend coverage (`services/`) | ≥ 75% |

**Test layers:** unit (parsers, fusion, geometry, optimiser constraints via `validate_plan`, alert rules, predictive), API (pytest + httpx), component (Vitest + RTL), e2e (Playwright, §Phase 16).

---

## 19. Security, offline deployment & ops

- **Auth & RBAC:** JWT (12 h), bcrypt, role checks on every write; Commander-only approvals.
- **Audit:** hash-chained, append-only ledger; verification endpoint.
- **Input validation:** Pydantic/zod on every boundary; GeoJSON validated with shapely.
- **Secrets:** only in `.env`; nothing committed.
- **Air-gapped mode:** `MAP_TILES=offline`, `WEATHER_MODE=synthetic`, `LLM_PROVIDER=none|ollama`, self-hosted fonts, no CDN usage. Document wheel/npm cache installs in `OFFLINE.md`.
- **Resilience:** adapters fail independently (fusion health shows DEGRADED/DOWN); the optimiser runs on the last good COP snapshot and lowers confidence accordingly.
- **Observability:** structured logs with request IDs; `/health` plus `/fusion/sources`.

---

## 20. AGENTS.md / CLAUDE.md (agent rules)

Copy this block into `AGENTS.md` and `CLAUDE.md` at the repo root:

```markdown
# Agent rules for VAYU-COP

- IMPLEMENTATION.md is the source of truth. Implement only the phase you are asked to.
- Follow the stack, versions, folder layout, data model, API contract and UI spec exactly.
  If something is ambiguous, choose the simplest option consistent with the spec and note it in PROGRESS.md.
- Never hard-code numbers in the UI; everything comes from the API.
- Every AI/optimiser output is a proposal. Approvals require the COMMANDER role. Never add auto-approval.
- All data is synthetic. Do not add real unit data, real base data or real threat-system parameters.
  Store configurations stay generic categories.
- Keep the map locked to the theatre bounds (minZoom 6) so international boundaries never render.
- Backend: Python 3.11, type hints everywhere, Pydantic v2, SQLAlchemy 2.0 style, ruff clean.
- Frontend: TypeScript strict, functional components, Tailwind with CSS variables from tokens.css,
  shadcn/ui primitives, TanStack Query for server state, Zustand for live state.
- Times are UTC in the backend and displayed as Zulu in the UI.
- Write tests for every service you add. Run `make lint` and `make test` before finishing.
- For UI work, compare against docs/ui-reference.png (applying the fixes in §13.1).
- At the end of each phase: tick the checkboxes in PROGRESS.md and list how to verify.
```

---

## 21. PROGRESS.md template

```markdown
# VAYU-COP — Progress

| Phase | Name | Status | Notes |
|---|---|---|---|
| 0 | Foundation & tooling | ☐ | |
| 1 | Domain model, DB & scenario | ☐ | |
| 2 | Core API, auth & RBAC | ☐ | |
| 3 | Data fusion & real-time bus | ☐ | |
| 4 | UI shell & design system | ☐ | |
| 5 | COP map | ☐ | |
| 6 | Resources & mission queue | ☐ | |
| 7 | Optimisation engine | ☐ | |
| 8 | AI panel, approval & Gantt | ☐ | |
| 9 | Simulation & dynamic retasking | ☐ | |
| 10 | Alerts & conflict detection | ☐ | MVP done |
| 11 | Predictive analytics | ☐ | |
| 12 | What-if simulator | ☐ | |
| 13 | Audit ledger & AAR | ☐ | |
| 14 | ASK COP assistant | ☐ | |
| 15 | Mobile field view | ☐ | |
| 16 | Hardening & demo packaging | ☐ | |

## Decisions / deviations
-

## Known issues
-
```

---

## 22. Glossary

| Term | Meaning |
|---|---|
| **COP** | Common Operating Picture: one shared, live view of the operational situation |
| **CAP** | Combat Air Patrol: aircraft holding a station for a set period |
| **RECCE** | Reconnaissance mission |
| **AEW&C** | Airborne Early Warning & Control |
| **Tanker** | Air-to-air refuelling mission |
| **SAR / HADR** | Search and Rescue / Humanitarian Assistance & Disaster Relief |
| **Sortie** | One flight by one aircraft, from takeoff to landing |
| **Turnaround** | Ground time to refuel, rearm and check an aircraft between sorties |
| **Retasking** | Changing an approved plan in response to new events |
| **Relay slot** | Part of a long CAP covered by one sortie; slots chain to cover the full duration |
| **U/S** | Unserviceable: aircraft not fit to fly |
| **Zulu (Z)** | UTC time, the standard time reference in air operations |
| **METAR / NOTAM** | Aviation weather report / Notice to Airmen (airspace and facility notices) |
| **RAG** | Red/Amber/Green status colouring |
| **CP-SAT** | Google OR-Tools constraint-programming solver used for allocation |
| **AAR (report)** | After-action report: planned vs actual review after the operation |
