"""Generates backend/data/history/maintenance_history.csv (§7.8): 180 days x 42 aircraft of
daily maintenance-relevant rows, labelled from a known logistic ground truth plus noise so the
Phase 11 serviceability model has something sensible to learn.
"""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

from app.seed.generator import load_scenario

HISTORY_DIR = Path(__file__).resolve().parents[2] / "data" / "history"
HISTORY_FILE = HISTORY_DIR / "maintenance_history.csv"

DAYS = 180

# Illustrative per-type reliability offsets for the ground-truth logistic model (§7.8).
TYPE_FACTOR = {
    "SU30": 0.10,
    "RAF": -0.05,
    "LCA": 0.05,
    "M2K": 0.15,
    "JAG": 0.20,
    "C17": -0.15,
    "C130": -0.10,
    "IL78": -0.05,
    "NETRA": -0.10,
    "MI17": 0.25,
}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _tail_numbers(scenario) -> list[tuple[str, str, str]]:
    """Returns (tail_id, type_code, base_id) for every airframe, in the same seq order
    seed/generator.py uses, so tail ids line up with the seeded Aircraft rows."""
    tails = []
    per_type_seq: dict[str, int] = {}
    for t in scenario.aircraft_types:
        for alloc in t.allocations:
            for _ in range(alloc.qty):
                per_type_seq[t.code] = per_type_seq.get(t.code, 0) + 1
                tails.append((f"{t.code}-{per_type_seq[t.code]:02d}", t.code, alloc.base_id))
    return tails


def generate(scenario_name: str = "vayu_shield", seed: int | None = None) -> Path:
    scenario = load_scenario(scenario_name)
    rng = random.Random(seed if seed is not None else scenario.seed)
    tails = _tail_numbers(scenario)

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    start_date = date.today() - timedelta(days=DAYS)

    with HISTORY_FILE.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "date",
                "tail_id",
                "type",
                "base",
                "hours_flown",
                "sorties",
                "hours_since_maint",
                "airframe_hours",
                "snag_next_24h",
                "snag_next_48h",
                "snag_next_72h",
            ]
        )

        for tail_id, type_code, base_id in tails:
            airframe_hours = rng.uniform(500, 6000)
            hours_since_maint = rng.uniform(0, 20)
            sorties_7d: list[int] = [0] * 7
            recent_snag = 0

            for day_offset in range(DAYS):
                day = start_date + timedelta(days=day_offset)
                sorties = rng.choices([0, 1, 2, 3], weights=[0.35, 0.35, 0.20, 0.10])[0]
                hours_flown = round(sorties * rng.uniform(1.0, 3.0), 2)

                airframe_hours += hours_flown
                hours_since_maint += hours_flown

                sorties_7d.append(sorties)
                sorties_7d.pop(0)
                sorties_last_7d = sum(sorties_7d)

                p = _sigmoid(
                    -4.0
                    + 0.018 * hours_since_maint
                    + 0.25 * (sorties_last_7d / 7)
                    + TYPE_FACTOR.get(type_code, 0.0)
                    + 0.4 * recent_snag
                    + rng.gauss(0, 0.3)
                )
                snag_24h = 1 if rng.random() < p else 0
                snag_48h = 1 if snag_24h or rng.random() < p * 1.5 else 0
                snag_72h = 1 if snag_48h or rng.random() < p * 2.0 else 0

                writer.writerow(
                    [
                        day.isoformat(),
                        tail_id,
                        type_code,
                        base_id,
                        hours_flown,
                        sorties,
                        round(hours_since_maint, 2),
                        round(airframe_hours, 2),
                        snag_24h,
                        snag_48h,
                        snag_72h,
                    ]
                )

                recent_snag = snag_24h
                if snag_24h:
                    hours_since_maint = rng.uniform(0, 2)  # maintenance reset after a snag

    return HISTORY_FILE


def main() -> None:
    path = generate()
    print(f"Wrote {path} ({DAYS} days x fleet)")


if __name__ == "__main__":
    main()
