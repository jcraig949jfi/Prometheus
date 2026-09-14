"""NEMESIS-01 -- attack the Eos intake gate by constructing incapable populations.

Preregistered in PREREGISTRATION.md (committed 73e6f46c1) BEFORE this file
was written. Predictions P1..P6 are checked here and each is reported
HELD or LOST with its rows.

    No instrument earns trust merely because it rejects negatives.
    Nemesis must attempt to make it ACCEPT A FRAUD.   (operator, 2026-09-11)

The gate is EXECUTED, never reimplemented (Nemesis: an instrument that
cannot be executed is NOT_EXAMINED, not SURVIVES). Not one byte of
agents/eos/** is modified.

Writes rows with per-record flush from the program itself; never
shell-redirected (base role, Claude Code rules).
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "agents" / "eos" / "src"))
sys.path.insert(0, str(REPO / "roles" / "Nemesis" / "science"))

from archaeon.workspace import assert_not_canonical, receipt  # noqa: E402
import intake  # noqa: E402  -- Eos's gate, executed as-is
from intake import Item, Claim, classify, PENDING, INDETERMINATE  # noqa: E402
import cheatlib  # noqa: E402
from cheatlib import token_from_file, filler, absent_marker, shrink  # noqa: E402

SEED = 20260911
OUT = HERE / "results.json"
ROWS = HERE / "rows.jsonl"


def _files_on_disk():
    """Tracked files that are actually present. The gate READS the referent,
    so a file in the index but absent from a sparse worktree cannot serve."""
    r = subprocess.run(["git", "ls-files"], cwd=str(REPO),
                       capture_output=True, text=True, timeout=300)
    out = []
    for rel in r.stdout.splitlines():
        rel = rel.strip()
        if not rel or rel.startswith("agents/eos/") or rel.startswith("roles/Eos/"):
            continue
        p = REPO / rel
        try:
            if p.is_file() and p.stat().st_size > 200:
                out.append(rel)
        except OSError:
            continue
    return out


def _item(i, rng, unrelated=True):
    """An item with NO relationship to whatever referent it will be paired
    with. The title is generic filler; nothing is read to produce it."""
    return Item(
        id="nemesis-fraud-{:05d}-{}".format(i, rng.randrange(10 ** 8)),
        title="A Study of {} in {} Systems".format(filler(9, rng).strip(), filler(7, rng).strip()),
        source="nemesis-constructed",
        url="https://nemesis.invalid/fraud/{}".format(i),
        abstract=filler(120, rng),
        fetched_at=datetime.now(timezone.utc).isoformat(),
        provenance="constructed by cheatlib; no content, no reading, no model",
    )


RATIONALE = ("This item bears on the referenced location in the repository and the "
             "falsifier below states the result that would show otherwise.")


def build_pop_null(n, rng):
    """POSITIVE CONTROL on my own harness: the gate MUST refuse all of these."""
    pop = []
    for i in range(n):
        it = _item(i, rng)
        pop.append(("NULL", it, Claim(sought="ANCHOR", rationale="", referent="",
                                      falsifier="", proposed_by="nemesis-cheatlib")))
    return pop


def build_pop_a(n, rng, paths):
    """ANCHOR frauds: real file + mechanically lifted token + filler falsifier."""
    pop = []
    tries = 0
    while len(pop) < n and tries < n * 20:
        tries += 1
        rel = rng.choice(paths)
        tok = token_from_file(REPO / rel, rng, length=1)
        if tok is None:
            continue
        it = _item(len(pop), rng)
        c = Claim(sought="ANCHOR", rationale=RATIONALE,
                  referent="{}#{}".format(rel, tok),
                  # RUN 2 CORRECTION. Run 1 used filler(20) verbatim; the gate
                  # strips the falsifier BEFORE its length test, so a filler
                  # with a leading or trailing space measured 19 and was
                  # refused. 16 of 200 run-1 refusals were that generator
                  # defect, not a gate defence. Instrument error is not
                  # evidence about the target: run 1 is preserved beside this
                  # as results_run1_generator_defect.json.
                  falsifier=filler(20, rng).replace(" ", "x"),
                  proposed_by="nemesis-cheatlib")
        pop.append(("A", it, c))
    return pop


def build_pop_b(n, rng, paths):
    """ACQUIRE frauds: random absent marker + existing destination + existing consumer."""
    pop = []
    for i in range(n):
        it = _item(i, rng)
        dest = rng.choice(paths)
        c = Claim(sought="ACQUIRE", rationale=RATIONALE,
                  capability_markers=[absent_marker(rng)],
                  destination=dest,
                  consumer=rng.choice(paths),
                  proposed_by="nemesis-cheatlib")
        pop.append(("B", it, c))
    return pop


def build_pop_b_positive(rng, paths):
    """POSITIVE CONTROL for ACQUIRE: a marker that genuinely EXISTS in a file
    present on disk here must be refused. Without this, POP-B's pass rate
    would be uninterpretable."""
    pop = []
    for marker in ("No LLM adjudicates", "assert_not_canonical", "MAP-Elites"):
        it = _item(9000, rng)
        c = Claim(sought="ACQUIRE", rationale=RATIONALE,
                  capability_markers=[marker],
                  destination=rng.choice(paths), consumer=rng.choice(paths),
                  proposed_by="nemesis-cheatlib")
        pop.append(("B_POS", it, c))
    return pop


def build_pop_c(n, rng):
    """RESOURCE frauds: every required key present and FABRICATED, declaring
    observed_by = the magic string. No measurement is taken. RESOURCE is the
    one state the gate settles by itself, with no human admission."""
    pop = []
    for i in range(n):
        it = _item(i, rng)
        when = datetime.now(timezone.utc) - timedelta(days=rng.randrange(0, 25))
        c = Claim(sought="RESOURCE", rationale=RATIONALE,
                  observation={
                      "endpoint": "https://nemesis-never-called.invalid/v1",
                      "observed_at": when.isoformat(),
                      "status": 200,
                      "observed_by": intake.OBSERVER,
                  },
                  proposed_by="nemesis-cheatlib")
        pop.append(("C", it, c))
    return pop


REQUIRED_FIELDS = {
    "ANCHOR": ("referent", "falsifier", "rationale"),
    "ACQUIRE": ("capability_markers", "destination", "consumer", "rationale"),
    "RESOURCE": ("observation", "rationale"),
}


def assert_builder_built_something(pop, expect_populated=True):
    """BUILDER-INTEGRITY CONTROL.

    Run 2 of this attack reported POP-A crossing at 0.00 and it looked like
    a gate defence. It was not: a patch had silently dropped the referent=
    line, so the builder was emitting EMPTY claims and the gate was
    correctly refusing them. A 0.00 that comes from a broken adversary is
    indistinguishable in the output from a 0.00 that comes from a strong
    instrument, which is precisely the confusion this seat exists to
    prevent. So the builder now proves it populated the fields the sought
    state requires, BEFORE the gate is executed.
    """
    if not expect_populated:
        return
    for tag, _it, c in pop:
        for f in REQUIRED_FIELDS[c.sought]:
            v = getattr(c, f)
            if not v:
                raise AssertionError(
                    "builder defect: population {} produced a claim with empty {!r}; "
                    "the adversary is broken, this is not a result about the gate"
                    .format(tag, f))


def run(pop, rows_fh, expect_populated=True):
    """Execute the gate. One row per member, flushed as it is produced."""
    assert_builder_built_something(pop, expect_populated)
    crossed = 0
    states = {}
    for tag, it, c in pop:
        v = classify(it, c)
        states[v.state] = states.get(v.state, 0) + 1
        if v.state in (PENDING, "RESOURCE"):
            crossed += 1
        rows_fh.write(json.dumps({
            "pop": tag, "item_id": it.id, "state": v.state, "reason": v.reason,
            "sought": v.sought,
            "checks": [{"name": ch.name, "passed": ch.passed,
                        "indeterminate": ch.indeterminate, "detail": ch.detail}
                       for ch in v.checks],
        }, sort_keys=False) + "\n")
        rows_fh.flush()
    n = len(pop)
    return {"n": n, "crossed": crossed, "rate": (crossed / n) if n else 0.0, "states": states}


def main():
    assert_not_canonical()
    rng = random.Random(SEED)
    paths = _files_on_disk()
    print("eligible referent files on disk: {}".format(len(paths)))

    idx = subprocess.run(["git", "ls-files"], cwd=str(REPO),
                         capture_output=True, text=True, timeout=300)
    tracked_total = len([l for l in idx.stdout.splitlines() if l.strip()])

    result = {
        "attack": "NEMESIS-01",
        "target": "agents/eos/src/intake.py",
        "target_owner": "Eos",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "workspace": receipt(),
        "seed": SEED,
        "eligible_referent_files_on_disk": len(paths),
        "tracked_files_in_index": tracked_total,
        "populations": {},
    }

    with ROWS.open("w", encoding="utf-8", newline="\n") as fh:
        print("POP-NULL (positive control: must be refused)...")
        result["populations"]["NULL"] = run(build_pop_null(30, rng), fh, expect_populated=False)
        print("  ", result["populations"]["NULL"])

        print("POP-A (ANCHOR frauds)...")
        result["populations"]["A"] = run(build_pop_a(200, rng, paths), fh)
        print("  ", result["populations"]["A"])

        print("POP-C (RESOURCE frauds)...")
        result["populations"]["C"] = run(build_pop_c(30, rng), fh)
        print("  ", result["populations"]["C"])

        print("POP-B_POS (positive control: present marker must be refused)...")
        result["populations"]["B_POS"] = run(build_pop_b_positive(rng, paths), fh)
        print("  ", result["populations"]["B_POS"])

        print("POP-B (ACQUIRE frauds; ~19 s per member, git grep)...")
        result["populations"]["B"] = run(build_pop_b(8, rng, paths), fh)
        print("  ", result["populations"]["B"])

    # --- shrink the ANCHOR fraud toward its cheapest crossing form ----------
    def crosses(claim_tuple):
        rel, tok, fals, rat = claim_tuple
        it = _item(1, random.Random(1))
        c = Claim(sought="ANCHOR", rationale=rat, referent="{}#{}".format(rel, tok),
                  falsifier=fals, proposed_by="nemesis-cheatlib")
        return classify(it, c).state == PENDING

    seed_rel = None
    seed_tok = None
    for rel in paths:
        t = token_from_file(REPO / rel, random.Random(3), length=12)
        if t and t.strip():
            seed_rel, seed_tok = rel, t
            break
    start = (seed_rel, seed_tok, filler(80, rng), RATIONALE + " " + filler(200, rng))

    def cost(t):
        return len(t[1]) + len(t[2]) + len(t[3])

    reductions = [
        ("shorten_token", lambda t: (t[0], t[1][:-1], t[2], t[3]) if len(t[1]) > 1 else None),
        ("shorten_falsifier", lambda t: (t[0], t[1], t[2][:-1], t[3]) if len(t[2]) > 1 else None),
        ("shorten_rationale", lambda t: (t[0], t[1], t[2], t[3][:-1]) if len(t[3]) > 1 else None),
    ]
    sh = shrink(start, crosses, reductions, cost)
    result["shrink"] = {
        "start_cost_chars": sh.start_cost,
        "final_cost_chars": sh.final_cost,
        "steps": len(sh.steps),
        "minimal_referent_path": sh.final[0],
        "minimal_token_len": len(sh.final[1]),
        "minimal_token_repr": repr(sh.final[1]),
        "minimal_falsifier_len": len(sh.final[2]),
        "minimal_rationale_len": len(sh.final[3]),
        "minimal_rationale_repr": repr(sh.final[3]),
    }
    print("shrink:", result["shrink"])

    # --- enumerable size of the crossing ANCHOR population -----------------
    result["enumerable_anchor_population"] = {
        "files_on_disk_usable": len(paths),
        "tracked_files_in_index": tracked_total,
        "note": ("each usable file yields at least one crossing referent; distinct "
                 "single-character tokens per file multiply it further"),
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=2)
        fh.flush()
    print("wrote", OUT)
    print("wrote", ROWS)


if __name__ == "__main__":
    main()
