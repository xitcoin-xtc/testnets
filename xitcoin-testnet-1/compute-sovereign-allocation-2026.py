#!/usr/bin/env python3
"""Planned Member State seat allocation, 2026 reference.

Recomputes sovereign-allocation-index-2026.csv and sovereign-allocation-index-2026.json from the population
column of the CSV, so anyone can re-run it:

    python3 compute-sovereign-allocation-2026.py            # rewrite both files
    python3 compute-sovereign-allocation-2026.py --check    # fail if the files differ from a fresh computation
    python3 compute-sovereign-allocation-2026.py --wpp WPP2024_TotalPopulationBySex.csv.gz
                                                            # also check every population against the UN file

Model (planned for mainnet, not implemented on chain):
- seat pool 386,000,000 XTC, the sovereign reserve of the testnet genesis;
- equal share: 1,500,000 XTC for each of the 193 UN Member States (289,500,000 XTC);
- population pool: 96,500,000 XTC shared in proportion to the square root of each Member State's population;
- population: UN World Population Prospects 2024, medium variant, 1 July 2026, the figure published for each
  Member State as it is (no territory is added to or removed from any Member State);
- whole XTC, the units left by rounding go to the largest remainders, ties broken by ISO3 code; the total is
  exactly 386,000,000 XTC.
"""
import csv
import gzip
import io
import json
import math
import sys
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 60
HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "sovereign-allocation-index-2026.csv"
JSON_PATH = HERE / "sovereign-allocation-index-2026.json"
POOL = 386_000_000
EQUAL = 1_500_000
STATES = 193
ATOMIC = 10**18
FIELDS = ["position", "name", "m49", "iso2", "iso3", "population_2026", "equal_xtc", "population_share_xtc",
          "allocation_xtc", "allocation_atomic"]


def read_rows():
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    population_field = "population_2026" if "population_2026" in rows[0] else "base_population_2026"
    states = [{"name": r["name"], "m49": r["m49"], "iso2": r["iso2"], "iso3": r["iso3"],
               "population": int(r[population_field])} for r in rows]
    assert len(states) == STATES and len({s["iso3"] for s in states}) == STATES
    return states


def allocate(states):
    demographic = POOL - EQUAL * STATES
    roots = {s["iso3"]: Decimal(s["population"]).sqrt() for s in states}
    total_roots = sum(roots.values())
    exact = {k: Decimal(demographic) * r / total_roots for k, r in roots.items()}
    share = {k: int(v) for k, v in exact.items()}
    left = demographic - sum(share.values())
    for k in sorted(share, key=lambda k: (-(exact[k] - share[k]), k))[:left]:
        share[k] += 1
    # independent check with integer arithmetic on scaled square roots
    scaled = {s["iso3"]: math.isqrt(s["population"] * 10**24) for s in states}
    total_scaled = sum(scaled.values())
    numerators = {k: demographic * v for k, v in scaled.items()}
    check = {k: n // total_scaled for k, n in numerators.items()}
    for k in sorted(check, key=lambda k: (-(numerators[k] % total_scaled), k))[:demographic - sum(check.values())]:
        check[k] += 1
    assert check == share, "the two computations disagree"
    assert sum(share.values()) == demographic
    return share, left


def build(states):
    share, left = allocate(states)
    rows = []
    for i, s in enumerate(states, 1):
        allocation = EQUAL + share[s["iso3"]]
        rows.append({"position": str(i), "name": s["name"], "m49": s["m49"], "iso2": s["iso2"], "iso3": s["iso3"],
                     "population_2026": str(s["population"]), "equal_xtc": str(EQUAL),
                     "population_share_xtc": str(share[s["iso3"]]), "allocation_xtc": str(allocation),
                     "allocation_atomic": str(allocation * ATOMIC)})
    assert sum(int(r["allocation_xtc"]) for r in rows) == POOL
    ordered = sorted(rows, key=lambda r: (int(r["allocation_xtc"]), r["iso3"]))
    example = lambda r: {"name": r["name"], "iso3": r["iso3"], "population_2026": int(r["population_2026"]),
                         "allocation_xtc": int(r["allocation_xtc"])}
    metadata = {
        "status": "planned_for_mainnet_not_implemented_on_chain",
        "selection_basis": "united_nations_member_states",
        "position_count": STATES,
        "reference_year": 2026,
        "population_source": "UN World Population Prospects 2024, medium variant",
        "population_date": "2026-07-01",
        "population_basis": "figure published for each Member State, used as it is (no territorial consolidation)",
        "population_transformation": "square_root",
        "pool_xtc": str(POOL),
        "pool_atomic": str(POOL * ATOMIC),
        "equal_share_per_state_xtc": str(EQUAL),
        "equal_pool_xtc": str(EQUAL * STATES),
        "population_pool_xtc": str(POOL - EQUAL * STATES),
        "rounding": "whole XTC, largest remainder, ties by ISO3 code",
        "rounding_units_assigned": left,
        "funding": ("Funded from the Xitchain reserve of Kcalb Ltd (Cronos wallet "
                    "0x4993F2012D72C3cFb67eBde946481b9dbFB3F254). At mainnet the pool crosses the bridge one for one, "
                    "locked on Cronos, so the total supply stays 5,250,000,000 XTC."),
        "self_stake_per_state_xtc": "5000000",
        "vesting": "20% a year over 5 years while the validator stays active and in good standing",
        "examples": {"smallest": example(ordered[0]), "median": example(ordered[STATES // 2]),
                     "largest": example(ordered[-1])},
    }
    return rows, metadata


def render(rows, metadata):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue(), json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"


def check_wpp(states, path):
    wanted = {s["iso3"]: s["population"] for s in states}
    found = {}
    with gzip.open(path, "rt", encoding="utf-8-sig") as handle:
        for r in csv.DictReader(handle):
            if (r["Variant"] == "Medium" and r["Time"] == "2026" and r["LocTypeName"] == "Country/Area"
                    and r["ISO3_code"] in wanted):
                found[r["ISO3_code"]] = int(Decimal(r["PopTotal"]) * 1000)
    bad = sorted(k for k in wanted if found.get(k) != wanted[k])
    assert not bad, f"population differs from the UN file for: {bad}"
    print("wpp=OK (193 populations match UN WPP 2024, medium variant, 2026)")


def main(argv):
    states = read_rows()
    if "--wpp" in argv:
        check_wpp(states, argv[argv.index("--wpp") + 1])
    rows, metadata = build(states)
    csv_text, json_text = render(rows, metadata)
    if "--check" in argv:
        assert CSV_PATH.read_text(encoding="utf-8") == csv_text, "CSV differs from a fresh computation"
        assert JSON_PATH.read_text(encoding="utf-8") == json_text, "JSON differs from a fresh computation"
    else:
        CSV_PATH.write_text(csv_text, encoding="utf-8")
        JSON_PATH.write_text(json_text, encoding="utf-8")
    ex = metadata["examples"]
    print(f"positions={STATES} total_xtc={sum(int(r['allocation_xtc']) for r in rows)} "
          f"equal_pool_xtc={metadata['equal_pool_xtc']} population_pool_xtc={metadata['population_pool_xtc']}")
    for key in ("smallest", "median", "largest"):
        e = ex[key]
        print(f"{key}: {e['name']} ({e['iso3']}) population {e['population_2026']:,} allocation {e['allocation_xtc']:,} XTC")
    print("validation=OK")


if __name__ == "__main__":
    main(sys.argv[1:])
