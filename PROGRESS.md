# VAYU-COP — Progress

| Phase | Name | Status | Notes |
|---|---|---|---|
| 0 | Foundation & tooling | ✅ | Backend (FastAPI) + frontend (Vite/React) skeletons, Docker Compose, Makefile, env config. See deviations below. |
| 1 | Domain model, DB & scenario | ✅ | 17 SQLAlchemy models + Alembic migration, camelCase Pydantic schemas, `vayu_shield.json` scenario, seeded generator + ML history CSV. See deviations below. |
| 2 | Core API, auth & RBAC | ✅ | JWT login/me, `require_roles` RBAC, 24 REST endpoints, `/cop/snapshot` + `/kpis`, uniform error envelope, `make api-types`. See deviations below. |
| 3 | Data fusion & real-time bus | ✅ | 9 source adapters, normalise→crosswalk→resolve→stale→provenance→publish pipeline, Open-Meteo+synthetic weather, `/ws` (4 msg types), `/fusion/sources`. See deviations below. |
| 4 | UI shell & design system | ✅ | Design tokens, AppLayout frame, auth context + route guard, routing, WS client + Zustand stores, 3 Vitest suites. **No ui-reference.png yet — see deviations.** |
| 5 | COP map | ✅ | Leaflet map: tiles+offline fallback, bases/aircraft/routes/threats/airspace/weather layers, graticule/compass/scale/coord-readout, layer toggles, range rings, entity drawer, conflict alerts. See deviations. |
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

- **Python version:** the dev machine has no Python 3.11 installed (3.12 and 3.14 only). The local
  venv (`backend/.venv`) is built with **3.12** (`pyproject.toml` allows `>=3.11,<3.13`) so `make dev`
  works without Docker. The Docker image (`backend/Dockerfile`) still pins **`python:3.11-slim`** per
  the spec, so the containerised path matches §3.2 exactly. No code depends on a 3.12-only feature.
- **`docs/ui-reference.png`** was not supplied by the user yet. Phases 4, 5 and 8 depend on it for
  visual fidelity — add the real reference image before starting Phase 4, or those phases will have
  to work from the written spec in §13 alone.
- **DB for local dev:** SQLite (`backend/vayu.db`, gitignored) is the default via `DATABASE_URL` in
  `.env.example`, per the "SQLite fallback for zero-setup dev" note in §3.2. Postgres 16 is wired up
  in `docker-compose.yml` for the containerised path.
- **ESLint 8** (not 9) was pinned to pair with `@typescript-eslint` v7 and keep a simple flat-free
  `.eslintrc.cjs` — the spec only says "ESLint + Prettier" without a major version, so this was the
  simplest option consistent with the rest of the pinned frontend stack (React 18.3 / Vite 5 / TS 5).
- Only the Phase 0/2 slice of the frontend stack (§3.1) was installed — React, Vite, TS, Tailwind,
  shadcn/ui foundations (`components.json`, `cn()` util), ESLint, Prettier, and now
  `openapi-typescript` (Phase 2 needs `make api-types`). Leaflet, Recharts, TanStack Query/Table,
  Zustand, React Router, react-hook-form/zod, lucide-react, sonner, framer-motion, date-fns,
  Vitest/RTL and Playwright are **not yet installed** — they belong to the phases that actually use
  them (4, 5, 6, 8, 11, 12, 16) per the "nothing from later phases" rule in AGENTS.md.
- **`AirBase` naming:** the §6.3 entity "Base" is modelled as the Python class `AirBase`
  (table `bases`) — `Base` itself is the SQLAlchemy declarative base in `core/db.py`. JSON/API
  naming is unaffected; this is a Python-only naming workaround.
- **No circular FK between `aircraft` and `assignments`:** `Aircraft.current_assignment_id` is a
  plain string column with no `ForeignKey` constraint, because SQLite can't `ALTER TABLE ADD
  CONSTRAINT`, so two tables can't hold FKs pointing at each other at creation time. The reverse
  direction (`Assignment.aircraft_id -> aircraft.id`) is a real FK.
- **Sector grid (S1–S12):** §7 says missions use "a sector grid S1-S12" but never gives exact
  boundaries. Invented a simple 3×4 grid over the theatre box (3 lat bands × 4 lon bands) and
  assigned each of the 12 seed missions to a plausible sector. Revisit if Phase 7's routing/risk
  model wants sector boundaries to mean something more specific.
- **Scenario JSON authoring format for airspace polygons:** `vayu_shield.json` stores airspace
  polygons as `polygon_lat_lon: [[lat, lon], ...]` (human-friendly) rather than raw GeoJSON;
  `seed/generator.py` converts to GeoJSON `[lon, lat]` winding when writing `Airspace.polygon_geojson`.
  Mission polygons are generated the same way from a `center_lat`/`center_lon`/`half_width_deg` triple.
- **Crew margin multiplier is 1.5×, not the spec's "≈1.4×"** (§7.3) — 1.4× landed the crew count at
  117, just under the stated ~120–140 target; 1.5× lands at 123. Tunable in `seed/generator.py`
  (`seed_crew`'s `_weighted_role_counts(..., 1.5)` call) if the target range should shift.
- **Each crew member is qualified on exactly one aircraft type** (their own), not cross-qualified
  on multiple compatible types. The spec doesn't ask for cross-qualification in Phase 1; revisit if
  a later phase's crew-pairing logic (stage B, §9.3) needs more flexible qualification pools.
- **Create/Update Pydantic schemas were only written for entities the API contract (§12.1)
  actually lets users mutate directly** (bases, aircraft status, crew status, stores, missions,
  airspace, threats). `Plan`, `Assignment`, `UnassignedMission`, `Event`, `Alert`, `AuditEntry`,
  `WeatherObs`/`WeatherCell` and `AircraftType` are service-/seed-created, so they only have `Read`
  schemas — a generic Create/Update pair for them would be dead code until something calls it.
- **`seed/history.py`'s 180-day window ends "today"** (`date.today() - timedelta(days=180)` through
  today), not relative to the scenario's `sim_start` — the ML history is background training data
  for the serviceability model (§11), unrelated to the exercise's own clock, so it didn't need to
  share a date axis with the scenario.
- **`openapi_url` is `/api/v1/openapi.json`, not the bare `/openapi.json`** the Phase 2 checklist's
  prose names — kept consistent with "Base path `/api/v1`" (§12) and Phase 0's existing setting.
  `Makefile`'s `api-types` target already pointed at `/api/v1/openapi.json` from Phase 0, so this
  phase just added `openapi-typescript` as a frontend dev dependency and confirmed the target works.
- **Login uses `OAuth2PasswordRequestForm`** (form-encoded `username`/`password`), not a JSON body —
  the FastAPI-idiomatic choice for JWT auth, and it makes the `/docs` Swagger "Authorize" button work
  out of the box for manual testing. A JSON login body would work equally well if that's preferred.
- **RBAC is enforced via a `require_roles(*roles)` dependency factory**, applied only to
  write endpoints (POST/PATCH/DELETE) — every GET endpoint only requires `get_current_user` (any
  authenticated role), matching "Read endpoints are open to all authenticated users" (§12).
- **`/kpis`' `crew_currency_pct`** compares each crew member's `currency_expiry` against the real
  wall-clock UTC date, not a sim clock — the sim clock doesn't exist until Phase 9. Because the
  scenario's `sim_start` (2026-11-02) is itself still in the future relative to whenever these tests
  run, this reads as 100% until that date arrives in the real world; expected and harmless until
  Phase 9 wires `/kpis` to the sim clock instead.
- **`GET /cop/snapshot`'s `routes` and `activePlan`** are empty/`null` until Phase 7 creates an
  `APPROVED` `Plan` — the query logic for "pull the active plan's assignment routes" is already
  written and will light up the moment a plan exists; no changes needed in Phase 7/8.
- **A pydantic `UnsupportedFieldAttributeWarning` fires on every write endpoint** (confirmed benign —
  camelCase aliasing still round-trips correctly end to end; it's a FastAPI-internal field-cloning
  quirk against our `CamelModel`'s `alias_generator`, not a bug in our code). Filtered in
  `pyproject.toml`'s `[tool.pytest.ini_options] filterwarnings` rather than restructuring every
  schema field into `Annotated[...]` form just to silence it.
- **`tests/test_seed.py` re-seeds the DB in its own module-scoped fixture** on top of the
  session-scoped seed in `conftest.py`, because `test_rbac.py` (which runs first, alphabetically)
  creates a real threat row through the live API — `test_seed.py`'s exact-count assertions need a
  pristine DB immediately before they run.
- **SQLite silently drops tzinfo on `DateTime(timezone=True)` columns** — a value written aware
  comes back naive on read. This broke every timestamp comparison in the fusion resolver/staleness
  code (`TypeError: can't compare offset-naive and offset-aware datetimes`) the moment real data
  flowed through it. Fixed with `fusion/time_utils.ensure_aware_utc()`, applied at every comparison
  site (`resolver.should_overwrite`, `resolver.find_mergeable_threat`, `staleness._sweep_model`).
  Postgres would not have this problem; this is a SQLite-dev-fallback-specific gotcha worth
  remembering if more datetime-comparing code gets added later.
- **"Warm start" on engine startup** (`FusionEngine._warm_start`): the seed scenario's
  `source_ts`/`fused_ts`/`first_seen`/`last_seen` are anchored to the exercise's fictional
  `sim_start` (2026-11-02), which can be weeks away from the real wall-clock time the server
  actually starts at — there's no sim clock until Phase 9, so adapters tick on real time. Without
  warm-start, the very first threat-intel tick would miss every seeded zone's merge window and try
  to insert a duplicate (`UNIQUE constraint failed: threat_zones.label`), and the first staleness
  sweep would flag every single entity stale on server start. `start()` now re-stamps every
  freshness timestamp to "now" once (no business data touched) before adapters begin ticking.
  Revisit once Phase 9's sim clock exists — it may make more sense to warm-start to `sim_start`
  instead of real "now" at that point.
- **Field-level provenance is a design principle demonstrated by a pure, tested function
  (`resolver.should_overwrite`), not something literally enforced per-field at the DB layer** —
  `ProvenanceMixin` (§6.2) gives each row exactly one `(source, source_ts, fused_ts, confidence,
  stale)` tuple, not one per field. In practice none of the 9 adapters actually contend over the
  same Aircraft field (`maint_mis` owns status/hours, `track_feed` owns position — disjoint by
  construction, which is itself the simplest form of authority enforcement), so there's no live
  code path that needs to call `should_overwrite` for Aircraft. The one place real multi-source
  contention exists — two threat sensors reporting the same physical threat — gets genuine
  resolution via `resolver.find_mergeable_threat` / `merge_confidence` / `merge_position`.
  `should_overwrite` is called for Aircraft.status (maint_mis vs. itself, always a same-source
  recency check) and is unit-tested directly against the authority rules it encodes.
- **`WeatherObs` is append-only** (a new row per observation/forecast hour, never mutated) except
  for forecast rows, which the weather-forecast loop deletes and re-inserts wholesale per base every
  10 minutes to avoid unbounded growth. `GET /weather/bases` (Phase 2) already picks the latest
  non-forecast row per base, so this needed no changes there.
- **`square_polygon()` is duplicated** between `app/seed/generator.py` and
  `app/services/fusion/engine.py` rather than importing the seed module into runtime code — the
  seed package is a CLI tool (`python -m app.seed`), not meant to be imported by the running app.
  Both copies are 5 lines; if they need to diverge or a third caller appears, move it to a shared
  `app/services/geo/` helper (which Phase 7 will need anyway for real routing).
- **`/ws` is mounted without the `/api/v1` prefix** (`GET /ws?token=<jwt>` exactly as §12.2 writes
  it), unlike every REST route. The frontend's Vite proxy (Phase 0) already expects this split.
- Synthetic native-format details not pinned by the spec (legacy store/status codes, fictional
  4-letter station codes VABA/VABR/VACH/VADL, synthetic icao24/service-number derivation) were
  invented to be internally consistent; see `normaliser.py`'s code maps and `crosswalk.py`'s
  `synthetic_icao24`/`synthetic_service_number` if a real integration ever needs to match them.
- **`docs/ui-reference.png` still hasn't been supplied.** Phase 4 was built strictly from the
  written spec in §13 — the exact CSS tokens (§13.3), the ASCII layout grid (§13.2), and the
  component behaviour descriptions (§13.4) — not from visual comparison against the actual
  reference image, since it doesn't exist in this repo. Everything here should be *consistent*
  with the image once it's added, but pixel-level fidelity (exact spacing, icon choices, information
  density) has not been verified against it. **Do this before/while building Phase 5 and 8**, which
  depend even more heavily on visual fidelity (the map and the AI panel are the image's centrepiece).
- **Browser automation wasn't available in this environment** (the Claude-in-Chrome extension
  wasn't connected), so the UI shell was verified by: `tsc`/`eslint` clean, all Vitest suites
  passing, the production build succeeding, and confirming every module resolves with `200` through
  the live Vite dev server (no transform/syntax errors). It was **not** visually inspected in an
  actual browser. Please open `http://localhost:5173` yourself after `make dev` and sanity-check
  the frame in both themes before treating "the frame matches the reference" as satisfied.
- **A temporary `_smoke.test.tsx` rendering `<App/>` hit a real jsdom/Node-undici incompatibility**
  with React Router v6's data-router `fetch`/`AbortSignal` internals (`TypeError: RequestInit:
  Expected signal ... to be an instance of AbortSignal`) — a known class of jsdom-vs-native-fetch
  conflict, not an app bug (the dev server serves every module fine; the production build succeeds).
  The diagnostic file was deleted rather than kept as a failing/skipped test. If a future phase wants
  a true full-router render test, it may need `vitest-environment-happy-dom` instead of jsdom, or a
  fetch-polyfill workaround — flagging here so it isn't rediscovered from scratch.
- **ZuluClock's `now` prop, when supplied, freezes the displayed time** (no local ticking interval)
  — `KpiStrip` deliberately passes the backend's `kpis.zuluTime` as `now`, so the clock reflects
  "the backend's current time" rather than the browser's wall clock, which is also exactly the hook
  point Phase 9's sim clock will use (sim time instead of real time) without changing `ZuluClock`
  itself. When no backend KPI has loaded yet (first paint, or WS/API both down), it falls back to a
  real ticking `setInterval` clock.
- **AUTO theme's day/night boundary re-evaluates every 60s**, not continuously — acceptable given
  the boundary only matters twice a day (06:00/18:00 local), and avoids a render on every tick.
- Tailwind's `xl:` breakpoint (1280px) stands in for the spec's literal "≥1440px" desktop threshold
  for the right AI panel's visibility (§13.2) — Tailwind's default scale has no 1440 breakpoint and
  adding a custom one for a single breakpoint wasn't worth the config surface. The right panel is
  a placeholder until Phase 8 regardless, so exact pixel fidelity here doesn't matter yet.
- **Found and fixed a real Pydantic casing gotcha**: the `to_camel` alias generator
  capitalises the letter immediately after a digit, so `p_unserviceable_24h` serialises as
  `pUnserviceable24H` (capital H), not `pUnserviceable24h`. Caught it by actually curling the
  live `/cop/snapshot` response rather than guessing the camelCase form. **Watch for this in
  Phase 6+**: `CrewMember.duty_hours_24h` -> `dutyHours24H` and `duty_hours_7d` -> `dutyHours7D`
  will hit the same gotcha the moment the Resources page reads them — verified via
  `to_camel()` directly, not just inferred from this one case.
- **`/cop/snapshot`'s `routes` field was widened from raw `list[dict]` geometry to a proper
  `RouteSegmentRead`** (`assignmentId`, `missionId`, `missionType`, `aircraftId`, `phase`,
  `geometry`) so `RouteLayer` can actually colour-by-mission-type and dash-by-phase as the
  spec asks (§13.4) once Phase 7/8 starts creating plans — this was a backend schema change
  made *during* Phase 5 because the old shape had no way to style a route at all. `phase`
  (PLANNED/AIRBORNE/FLOWN) is derived purely from `now` vs. the assignment's own
  `takeoff_ts`/`land_ts`, independent of the aircraft's own `.status`.
- **"Hatched" airspace polygons use a hand-rolled SVG `<pattern>`** injected into Leaflet's own
  SVG renderer root (`HatchPatternDefs.tsx`), referenced via `fillColor: 'url(#vayu-hatch)'` —
  not a Leaflet plugin (none is in the pinned stack) and not literally `leaflet.pattern`. Relies
  on Leaflet's SVG renderer (not `preferCanvas`) staying on for vector layers; see the next point.
- **`preferCanvas` was left off** (SVG renderer for all vector layers). The spec's "canvas renderer
  if marker count exceeds 100" (§13.4) talks about *aircraft markers*, but aircraft render as
  `L.divIcon` `Marker`s, which are plain DOM elements in both Leaflet renderer modes —
  `preferCanvas` only affects vector `Path` layers (`Circle`/`Polygon`/`Rectangle`), not Markers. At
  today's fleet size (42) this is moot either way; if a much larger fleet ever needs real marker
  virtualization, that's a different library (e.g. `Leaflet.markercluster`), not `preferCanvas`.
- **Weather cells "drift"** via client-side dead reckoning from each cell's snapshot
  `motionDeg`/`motionKts` (a local `requestAnimationFrame` loop), not because the backend
  continuously moves them — there's no sim clock to drive that until Phase 9. Base weather
  GO/MARGINAL/NO-GO badges use a single direct ceiling/visibility threshold, not the real
  per-aircraft-type model (§11), which is Phase 11's trained predictive-analytics work.
- **Aircraft position interpolation** tweens between the previous and current WS tick over the
  gap between them (`AircraftLayer.tsx`'s `useInterpolated`), falling back to the REST snapshot's
  own lat/lon until the first WS tick arrives for that aircraft (so markers don't pop in/out).
- **The sector grid (S1-S12) is duplicated** between `backend/app/seed/generator.py` and
  `frontend/src/components/map/SectorGrid.tsx` — both hand-encode the same invented 3×4 grid
  (see the Phase 1 deviation above) since the backend doesn't expose sector boundaries via any
  endpoint. If a later phase needs them to literally match (not just visually), expose them from
  the backend instead of keeping two copies in sync by convention.
- **Visual verification still wasn't possible** — browser automation remains unavailable in this
  environment (same as Phase 4). Leaflet especially needs a real browser (DOM measurement, SVG
  internals that jsdom can't meaningfully emulate), so this phase was verified via: clean
  `tsc`/`eslint`, a successful production build, every new module resolving with `200` through the
  live Vite dev server, and the live `/cop/snapshot` response shape checked by hand with `curl`
  (which is how the `pUnserviceable24H` bug above was actually caught). **Please open
  `http://localhost:5173` yourself** and confirm: aircraft markers move/rotate, clicking any
  entity opens the drawer, the theme toggle swaps tile sets, and `VITE_MAP_TILES=offline` in
  `frontend/.env.local` still renders a usable map (graticule + outline, no base tiles).

## Known issues

- `npm audit` reports vulnerabilities in transitive dev-only build tooling (e.g. `postcss-selector-parser`
  via Tailwind 3.4's internals). Fixing requires upgrading to Tailwind 4, which breaks the pinned
  stack (§3.1 says Tailwind 3.4, don't upgrade mid-build). Left as-is; revisit at Phase 16 hardening.
- `frontend/package-lock.json` and `backend/.venv` are present locally but gitignored/untracked by
  design — a fresh clone must run `make setup` before `make dev`.

## How to verify Phase 0

```bash
make setup   # creates backend/.venv, installs backend+frontend deps
make dev     # backend on :8000, frontend on :5173
curl localhost:8000/api/v1/health   # -> {"status":"ok","version":"0.1.0"}
make lint    # ruff (backend) + eslint (frontend), both clean
make test    # pytest (backend) — 1 passing health test; no frontend tests yet
```

Open `http://localhost:5173` — it shows the VAYU-COP placeholder and
`backend: ok (v0.1.0)` once the backend responds (proves the `/api` Vite proxy works).

## How to verify Phase 1

```bash
make seed    # drops & recreates all tables, seeds the VAYU SHIELD scenario
# -> bases: 4, aircraft: 42, crew: ~120-140, missions: 12 (+3 relay slots),
#    threats: 3, airspaces: 4, weather_cells: 1, users: 7

cd backend && .venv/bin/python -m app.seed.history   # writes data/history/maintenance_history.csv
#    (180 days x 42 aircraft, ~5-20% snag rate depending on window — Phase 11 training data)

cd backend && .venv/bin/alembic upgrade head   # applies the Phase 1 migration from scratch
make test-backend   # 8 passing tests: entity counts, base validity, crew/base qualification,
                     # theatre-bounds, mission-window validity, store non-negativity,
                     # scenario-JSON-against-Pydantic-schema
make lint            # ruff clean
```

## How to verify Phase 2

```bash
make seed            # fresh seeded DB
make dev              # backend on :8000
open http://localhost:8000/docs   # Swagger lists all 24 Phase 2 endpoints, grouped by tag

curl -X POST localhost:8000/api/v1/auth/login -d "username=commander&password=commander123"
#   -> {"accessToken": "...", "tokenType": "bearer", "user": {...}}

TOKEN=<accessToken from above>
curl localhost:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"
curl localhost:8000/api/v1/cop/snapshot -H "Authorization: Bearer $TOKEN"   # ~13ms on seed data
curl localhost:8000/api/v1/kpis -H "Authorization: Bearer $TOKEN"

# RBAC: an AIRCREW token gets 403 on a write only COMMANDER/MAINTENANCE/etc. may do
curl -X PATCH localhost:8000/api/v1/aircraft/SU30-01/status \
  -H "Authorization: Bearer <crew's token>" -H "Content-Type: application/json" \
  -d '{"status":"READY"}'   # -> 403 {"error":{"code":"FORBIDDEN",...}}

make api-types        # writes frontend/src/lib/api-types.ts from the live OpenAPI schema
make test-backend     # 29 passing tests (auth, RBAC, snapshot shape+timing, filters, seed)
make lint              # ruff + eslint clean
```

## How to verify Phase 3

```bash
make seed
make dev   # backend on :8000 — the fusion engine and WS broadcasters start automatically

TOKEN=$(curl -s -X POST localhost:8000/api/v1/auth/login -d "username=admin&password=admin123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")

curl localhost:8000/api/v1/fusion/sources -H "Authorization: Bearer $TOKEN"
#   -> 9 sources (maint_mis, crew_roster, stores_inv, met_feed, airspace_notam,
#      threat_intel_a, threat_intel_b, track_feed, tasking), each OK within a few seconds

curl -X PATCH localhost:8000/api/v1/fusion/sources/threat_intel_b \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"enabled": false}'
#   -> {"enabled": false, "status": "DOWN", ...} — try it as a non-ADMIN token first for a 403

# WebSocket: connect to ws://localhost:8000/ws?token=$TOKEN with any WS client (e.g. websocat,
# or a browser console) and watch aircraft.position arrive every ~1s with all 42 aircraft,
# kpi.update every ~1s, fusion.health every ~5s, and cop.delta whenever an adapter changes
# something (e.g. a maint_mis snag, a threat zone merge, a NOTAM status flip).

make test-backend   # 56 passing tests total — 27 new: METAR/NOTAM parsing, DMS<->decimal,
                     # authority-conflict resolution, two-sensor threat merge (confidence rises
                     # above either sensor's own report), staleness sweep transitions
make lint            # ruff clean
```

## How to verify Phase 4

```bash
make seed
make dev   # backend on :8000, frontend on :5173

cd frontend && npx vitest run   # 12 passing tests: KpiChip tones, ThemeToggle -> [data-theme],
                                  # ZuluClock HH:MM:SSZ formatting + speed badge
npx tsc --noEmit                 # clean
npx eslint . --max-warnings=0    # clean
npm run build                    # production build succeeds
```

Then **open `http://localhost:5173` yourself** (not verified in-session — no browser available):
- `/login` renders the dark tactical login card; sign in as `commander` / `commander123`.
- After login you land on `/` inside the full frame: exercise banner, top bar (hamburger,
  title, theme segmented control, settings cog, user badge, logout, connection dot),
  KPI strip, side nav (COP MAP/RESOURCE STATUS/AI QUEUE/PREDICTIVE ANALYTICS/SIMULATION/
  AUDIT LOG/REPORTS + SETTINGS), a map-area placeholder, a right AI-panel placeholder
  (only ≥1280px wide — see the Tailwind-breakpoint deviation above), and a bottom
  Gantt-area placeholder.
- The KPI strip should show real values within ~1s (`AIRCRAFT READY 33/42` etc.) and the
  connection dot should turn **green** once the WebSocket connects.
- Settings → Theme: clicking AUTO/DAY/NIGHT should visibly flip the whole page between
  TACTICAL LIGHT and BUNKER DARK, and the choice should survive a reload (localStorage).
- Resize the window under 768px: it should redirect to `/m` (the mobile placeholder stub).
- Click the hamburger: the side-nav labels should hide, leaving just icons.
- Compare both themes against `docs/ui-reference.png` once it exists — this has not been
  done yet (see the deviations section above).

## How to verify Phase 5

```bash
make seed
make dev   # backend on :8000, frontend on :5173

cd frontend
npx tsc --noEmit                # clean
npx eslint . --max-warnings=0   # clean
npx vitest run                  # 12 passing (unchanged from Phase 4 — no new Vitest suites
                                 # were required for this phase; Leaflet needs a real browser)
npm run build                   # production build succeeds

curl -s http://localhost:8000/api/v1/cop/snapshot -H "Authorization: Bearer <token>" \
  | python3 -m json.tool | head -30   # bases/aircraft/airspace/threats/weatherCells/routes
```

Then **open `http://localhost:5173` yourself** (same caveat as Phase 4 — no browser available
in this environment):
- `/` (COP MAP) should show a Leaflet map locked to the VAYU SHIELD theatre — pan/zoom out and
  confirm you can never scroll past the theatre box or zoom out past level 6 (no international
  boundary should ever be visible, per §2).
- 4 base glyphs (runway icon in a status ring), 42 aircraft icons (rotated to heading, colour by
  status), 3 pulsing-then-steady threat rings, 4 hatched airspace polygons, the CB-1 weather cell
  slowly drifting, a compass rose (top-left), scale bar (bottom-right), and a coordinate readout
  (top-right, in DMS) that updates as you move the mouse.
- Aircraft should visibly glide rather than jump between positions (1 Hz WS updates, interpolated).
- Click any base/aircraft/threat/airspace/weather cell: the entity drawer opens on the right with
  its fields and a provenance tooltip (hover a field with a dotted/underline cue) on fused fields.
- Right-click a base: a range-ring picker appears (top-right) with a type dropdown; the map shows
  that type's full range ring plus 30/60-minute transit rings.
- The layer-toggle panel (top-right) should show/hide each layer; "Sector grid" draws the S1-S12
  grid used by the seed scenario.
- "LIVE CONFLICT ALERTS" (bottom-left) should show "No active conflicts" (no `/alerts` endpoint
  exists until Phase 10 — confirm this doesn't error, just shows the empty state).
- Settings → Theme: toggling DAY/NIGHT should swap the CARTO tile set (light_all/dark_all), not
  just the UI chrome.
- Set `VITE_MAP_TILES=offline` in `frontend/.env.local`, restart `npm run dev`: the map should
  still show the graticule, theatre outline, and all entity layers — just without base tiles — with
  an "OFFLINE MAP MODE" badge bottom-right.


