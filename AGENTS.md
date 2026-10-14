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
