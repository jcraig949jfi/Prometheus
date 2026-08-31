"""Four-hour ASCII field report for Charon, and the campaign manifest.

WRITTEN FOR AN AUDITOR OF TRAJECTORY, NOT VOLUME. Charon's job is to attack the campaign, so
the report leads with what was killed and what is merely proposed, and it prints the ratio
between adjudicated and proposed rather than a corpus size. A report that makes a campaign look
productive by counting downloads is exactly the artifact this one must not be.

ASCII ONLY, terminal-readable, timestamped filenames, no overwriting -- matching the existing
convention in charon/reports/.
"""
from __future__ import annotations

import json
import pathlib
import time

from . import store, taxonomy
from .schema import now_iso

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHARON_REPORTS = REPO_ROOT / "charon" / "reports"
MANIFEST_PATH = pathlib.Path(__file__).resolve().parent / "CAMPAIGN_MANIFEST.json"


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _hours_elapsed(man: dict) -> float:
    start = man.get("start_epoch")
    if not start:
        return 0.0
    return (time.time() - float(start)) / 3600.0


def _bar(label: str, value, width: int = 38) -> str:
    return "  " + (label + " ").ljust(width, ".") + " " + str(value)


def build_report(man: dict) -> str:
    s = store.summary()
    cycles = store.read_cycles()
    integ = store.integrity()
    hours = _hours_elapsed(man)
    n_cycles = len(cycles)
    planned = man.get("planned_cycles", 96)

    # Cell occupancy over the QD archive.
    occupied = set()
    for g in store.current("genomes").values():
        occupied.add(taxonomy.cell_of(g))
    # 'unknown'-only cells are artifacts of our tagging, not niches; count them separately so
    # coverage is not inflated by the papers we failed to classify.
    real_cells = {c for c in occupied if "unknown" not in c and "B_UNASSIGNED" not in c}

    lanes = {}
    for c in cycles:
        k = c.get("frontier_kind") or "?"
        lanes[k] = lanes.get(k, 0) + 1

    statuses = {}
    for c in cycles:
        k = c.get("status") or "?"
        statuses[k] = statuses.get(k, 0) + 1

    holes = store.current("holes")
    persistent = [h for h in holes.values() if h.get("status") == "PERSISTENT_COVERAGE_HOLE"]
    killed = [h for h in holes.values() if h.get("status") == "KILLED_BY_RETRIEVAL"]
    confounds = list(store.current("confounds").values())
    migrations = {}
    for c in confounds:
        if c.get("cost_migration"):
            for m in str(c["cost_migration"]).split(";"):
                m = m.strip()
                if m:
                    migrations[m] = migrations.get(m, 0) + 1

    L = []
    A = L.append
    A("=" * 70)
    A("TECHNE RESEARCH CARTOGRAPHER -- HOUR {:02d} / {:02d}".format(
        int(hours), int(man.get("duration_hours", 48))))
    A("UTC: " + now_iso())
    A("CAMPAIGN: " + str(man.get("campaign_id", "?")))
    A("MANIFEST DIGEST: " + str(man.get("manifest_digest", "?"))[:32])
    A("CYCLES COMPLETE: {} / {}".format(n_cycles, planned))
    A("")
    A("MISSION")
    A("")
    A("  Build a cross-field map of search physics and identify falsifiable")
    A("  research holes without treating retrieval absence as discovery.")
    A("")
    A("CORPUS")
    A(_bar("sources compiled to ResearchGenome", s["genomes"]))
    A(_bar("with abstract evidence", s["genomes"]))
    A(_bar("with full text", s["genomes_with_fulltext"]))
    A(_bar("open access", s["genomes_open_access"]))
    A(_bar("with linked code", s["genomes_with_code"]))
    A(_bar("sources rejected (recorded)", s["rejected_sources"]))
    A(_bar("retrieval attempts logged", s["retrieval_attempts"]))
    A("")
    A("CLAIM LEDGER -- the three predicates are NOT the same predicate")
    A(_bar("CLAIM_PRESENT (text asserts it)", s["claims_present"]))
    A(_bar("CLAIM_SUPPORTED (named comparator)", s["claims_supported"]))
    A(_bar("MECHANISM_ISOLATED rows written", s["mechanism_isolated"]))
    A(_bar("  of which CONFIRMED by P3", s["mechanism_isolated_confirmed"]))
    A(_bar("  of which REFUTED by P3", s["mechanism_isolated_refuted"]))
    mi = s["mechanism_isolated"] or 1
    A(_bar("  isolation rate", "{:.1f}%".format(100.0 * s["mechanism_isolated_confirmed"] / mi)))
    A(_bar("adjudication=PROPOSED (not adjudicated)", s["claims_proposed"]))
    A("")
    A("  NOTE: extraction scope is ABSTRACT for the whole corpus. Abstracts")
    A("  advertise results and rarely state ablations, so P3 UNDER-fires by")
    A("  construction. A low MECHANISM_ISOLATED count is a fact about our")
    A("  evidence, not a finding about the literature.")
    A("")
    A("QD COVERAGE")
    A(_bar("archive cells (total possible)", taxonomy.total_cells()))
    A(_bar("cells occupied (any)", len(occupied)))
    A(_bar("cells occupied (fully classified)", len(real_cells)))
    from .cycle import MIN_CLASSIFICATION_RATE, classification_rate
    crate, cok, ctot = classification_rate()
    A(_bar("classification rate (abstract-bearing)",
           "{:.1f}% ({}/{})".format(100.0 * crate, cok, ctot)))
    A(_bar("hole proposal", "BLOCKED (rate < {:.0f}%)".format(100.0 * MIN_CLASSIFICATION_RATE)
           if crate < MIN_CLASSIFICATION_RATE else "allowed"))
    A(_bar("coverage holes CANDIDATE", s["holes_candidate"]))
    A(_bar("coverage holes PERSISTENT", s["holes_persistent"]))
    A(_bar("holes KILLED by retrieval", s["holes_killed"]))
    A("")
    A("FAILURE / CONFOUND CARTOGRAPHY -- the priority lane")
    A(_bar("confounded causal claims (P4 CONFIRMED)", s["confounds"]))
    A(_bar("  with cost-migration signature (P5)", s["confounds_with_cost_migration"]))
    if migrations:
        for m, n in sorted(migrations.items(), key=lambda kv: -kv[1])[:6]:
            A(_bar("    " + m, n))
    A("")
    A("CYCLE HEALTH")
    for k in sorted(statuses):
        A(_bar("cycles with status " + k, statuses[k]))
    A("")
    A("LANE BALANCE (diversity pressure -- flat is healthy)")
    for k in sorted(lanes):
        A(_bar(k, lanes[k]))
    A("")
    A("STORE INTEGRITY")
    torn = sum(v["torn"] for v in integ.values())
    A(_bar("torn lines across all stores", torn))
    A("  (a torn line is the expected signature of a kill mid-write; it is")
    A("   reported rather than swallowed so counts stay comparable)")
    A("")
    A("  READ THE CLASSIFICATION RATE BEFORE THE HOLE COUNT. An empty cell in")
    A("  an archive where most papers could not be placed is a fact about the")
    A("  tagger, not about the literature. Holes proposed while the rate was")
    A("  below threshold are marked suspect_low_classification and must not be")
    A("  reported as gaps.")
    A("")
    A("TOP PERSISTENT HOLES (absence under OUR protocol, nothing more)")
    if not persistent:
        A("  none promoted yet -- promotion needs >= 4 formulations across >= 3 indexes")
    for h in persistent[:5]:
        A("  cell " + str(h["coordinates"]["cell"]))
        A("       formulations=" + str(h.get("n_formulations")) + "  " +
          str(h.get("confidence_in_absence"))[:60])
    A("")
    A("HOLES KILLED SINCE START (this is the desirable outcome)")
    if not killed:
        A("  none yet")
    for h in killed[:5]:
        A("  cell " + str(h["coordinates"]["cell"]))
        A("       " + str(h.get("killed_by"))[:78])
    A("")
    A("BLOCKERS / RISKS")
    seen = set()
    for c in reversed(cycles):
        for b in (c.get("blockers") or []):
            if b not in seen:
                seen.add(b)
                A("  * " + str(b)[:76])
            if len(seen) >= 6:
                break
        if len(seen) >= 6:
            break
    if not seen:
        A("  * none recorded")
    A("  * Semantic Scholar returns HTTP 429 without an API key; it is never")
    A("    counted as an independent formulation for a hole promotion.")
    A("")
    A("CLAIM DISCIPLINE")
    A("")
    A("  No empty QD cell is reported as a scientific discovery.")
    A("  No LLM interpretation is treated as adjudication.")
    A("  No causal mechanism is credited without isolation evidence.")
    A("  No new scientific result is claimed without deterministic support.")
    A("")
    A("=" * 70)
    return "\n".join(L) + "\n"


def write_report(man: dict) -> pathlib.Path:
    """Write a timestamped ASCII report into the existing charon/reports/ convention.

    Never overwrites: filenames carry a UTC timestamp, matching the existing
    `<name>_<date>.md` / `<name>_<YYYYMMDD_HHMMSS>.log` pattern already in that directory.
    """
    CHARON_REPORTS.mkdir(parents=True, exist_ok=True)
    text = build_report(man)
    stamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    hours = int(_hours_elapsed(man))
    p = CHARON_REPORTS / ("techne_cartography_hour{:02d}_{}.txt".format(hours, stamp))
    p.write_text(text.encode("ascii", "replace").decode("ascii"), encoding="ascii")
    return p
