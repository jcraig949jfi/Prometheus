"""T-P5. The INDEX must be sufficient for adjudication, with no per-run fallback.

THE DEFECT (Z80A-D03). The predecessor's index whitelist carried `replicated` and
`replication_rate` but not `replication_events` or `births_similar_no_write`. The
adjudicator read them from the index, found them absent, and returned INADMISSIBLE for
all 36 spontaneity flags in flight with the reason "no evidence-backed replication
event" - which was false; the per-run records showed one or more each.

The fix at the time was to open the per-run RESULT.json. That produced a correct answer
from a record the index no longer described, so the index silently stopped being a
checkable account of the campaign.

This test asserts the stronger property: adjudicating from index rows and adjudicating
from full per-run records give EXACTLY equal verdicts across every special-result class.
Since `adjudicate()` has no file path in it at all, equality here means the whitelist is
complete rather than that a fallback rescued it.

The negative control is the part that makes this non-vacuous: dropping a whitelist field
must make the comparison fail. If it does not, the test is not testing anything.

Run:  python tests/test_p5_index.py
Exit: 0 all checks pass, 1 otherwise.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import adjudicate  # noqa: E402
import specials  # noqa: E402


def cell(**kw):
    base = {"world": "GRID", "environment": "STATIC", "representation": "Z8_64",
            "reproduction": "ENDOGENOUS_COPY", "self_location": "PRIMITIVE",
            "copy_primitive": "BYTEWISE", "pressure": "NONE_IMPLICIT",
            "structure": "NICHES_HIGH_MIG", "task_transform": "ADD1",
            "read_order": "ANSWER_BEFORE_READ", "bridge": "VALLEY",
            "seeding": "RANDOM", "mutation_operator": "BOTH",
            "mutation_locality": "LOCAL", "mutation_rate": "MID", "atlas_axis": "NONE"}
    base.update(kw)
    return base


def derived(**kw):
    base = {"endogenous": True, "spontaneity_test": True, "constant_kind": "INCREMENTAL",
            "has_task": True, "moat": True, "seeded_instrument": False}
    base.update(kw)
    return base


def full_summary(**kw):
    """A COMPLETE per-run summary: every field world.py emits that matters here, plus
    extras the index deliberately does not carry."""
    base = {
        "pop_final": 180, "extinct": False, "epochs_run": 4000, "ops": 900000,
        "crossed_ever": True, "crossed_at_final": True,
        "held_max_ever": 0.95, "held_max_final": 0.95, "n_cross_events": 3,
        "replicated": True, "replication_rate": 0.004, "replication_events": 6,
        "births_similar_no_write": 2, "births_endogenous": 6, "births_external": 0,
        "max_ancestry_depth": 7, "n_lineages_depth_ge_2": 20, "n_lineages_depth_ge_5": 6,
        "max_causal_replication_depth": 6, "n_causal_lineages_depth_ge_2": 9,
        "n_causal_lineages_depth_ge_5": 2, "propagating_replicators": 3,
        "lineage_complete": True, "migration_events": 40,
        "has_reservoir_certificate": False, "ancestry_certificate": None,
        "comp_max": 0.96, "span_mean_final": 62.0, "niche_occupancy": [40, 40, 40, 40],
        "first_replicator": {"fidelity": 0.95, "epoch": 100},
        "entropy_drop": 0.2, "dom_share_final": 0.3, "uniq_final": 120,
        "len_mean_final": 64.0, "fid_mean_final": 0.9,
        # present per-run, intentionally NOT in the index whitelist
        "writes_blocked": 12, "alloc_fails": 3, "copy_bytes": 5000,
        "validation_writes": 0, "halted_share_of_best": 0.1,
    }
    base.update(kw)
    return base


def reservoir_cert():
    return {"founder": 3, "founder_niche": 0,
            "migration": {"oid": 3, "epoch": 40, "from_niche": 0, "to_niche": 2},
            "crossing_oid": 91, "crossing_niche": 2, "crossing_epoch": 120,
            "crossing_held": 0.95, "lineage_len": 6, "lineage_complete": True}


# --------------------------------------------------------------- fixture set
# One fixture per special-result class, plus the interesting failure shapes.
def build_fixtures():
    F = []

    # 1. RESERVOIR with a genuine certificate -> ADMISSIBLE
    F.append(("reservoir_certified", cell(structure="RESERVOIR"), derived(),
              full_summary(has_reservoir_certificate=True,
                           ancestry_certificate=reservoir_cert())))
    # 2. RESERVOIR, certificate but truncated lineage -> INADMISSIBLE
    F.append(("reservoir_truncated", cell(structure="RESERVOIR"), derived(),
              full_summary(has_reservoir_certificate=True,
                           ancestry_certificate=reservoir_cert(),
                           lineage_complete=False)))
    # 3. RESERVOIR, seeded instrument -> INADMISSIBLE
    F.append(("reservoir_seeded", cell(structure="RESERVOIR", seeding="SEEDED_READER"),
              derived(seeded_instrument=True, spontaneity_test=False),
              full_summary(has_reservoir_certificate=True,
                           ancestry_certificate=reservoir_cert())))
    # 4. SPONTANEOUS with deep causal lineage -> ADMISSIBLE
    F.append(("spontaneous_deep", cell(), derived(), full_summary()))
    # 5. SPONTANEOUS, events but star-shaped (the predecessor's real result) -> WEAK
    F.append(("spontaneous_star", cell(), derived(),
              full_summary(max_causal_replication_depth=1, propagating_replicators=0)))
    # 6. SPONTANEOUS, resemblance only -> INADMISSIBLE
    F.append(("spontaneous_no_evidence", cell(), derived(),
              full_summary(replication_events=0, births_similar_no_write=26)))
    # 7. ARCHITECTURE under a gated pressure -> WEAK
    F.append(("architecture", cell(pressure="TASK_GATED_INTERACTION"), derived(),
              full_summary(span_mean_final=20.0)))
    # 8. ENDOGENOUS-only, clean margin -> ADMISSIBLE
    F.append(("endogenous_clean", cell(), derived(), full_summary()))
    # 9. ENDOGENOUS-only, control finished ahead -> INADMISSIBLE
    F.append(("endogenous_inverted", cell(), derived(), full_summary()))
    # 10. INCREMENTAL vs atomic sibling
    F.append(("incremental", cell(), derived(), full_summary()))
    return F


def controls_for(name):
    """The matched-control / sibling records a flag needs, as full summaries."""
    if name == "endogenous_clean":
        return {"control_summary": full_summary(crossed_ever=False, crossed_at_final=False,
                                                held_max_ever=0.0, held_max_final=0.0),
                "control_axis": "reproduction"}
    if name == "endogenous_inverted":
        return {"control_summary": full_summary(crossed_ever=False, crossed_at_final=False,
                                                held_max_ever=0.99, held_max_final=0.99),
                "control_axis": "reproduction"}
    if name == "incremental":
        return {"sibling_atomic": full_summary(crossed_ever=False, held_max_ever=0.1,
                                               held_max_final=0.1)}
    return {}


# Rows whose `specials` were written by the UNREPAIRED flag layer: the flag name is
# present with no certificate behind it. The adjudicator is a post-hoc pass over a frozen
# record and can be handed exactly these, so its rejection branches must be live rather
# than unreachable because the repaired flag declines to fire upstream.
LEGACY_ROWS = [
    ("legacy_reservoir_no_cert", cell(structure="RESERVOIR"), derived(),
     full_summary(has_reservoir_certificate=False, ancestry_certificate=None,
                  migration_events=0),
     [{"flag": "RESERVOIR_CROSSED_A_MOAT", "reads": "historical",
       "evidence": {"held": 0.95, "niche_occupancy": [64, 64, 64, 64]}}]),
    ("legacy_reservoir_seeded", cell(structure="RESERVOIR", seeding="SEEDED_READER"),
     derived(seeded_instrument=True, spontaneity_test=False),
     full_summary(has_reservoir_certificate=True, ancestry_certificate=reservoir_cert()),
     [{"flag": "RESERVOIR_CROSSED_A_MOAT", "reads": "historical", "evidence": {}}]),
    ("legacy_reservoir_truncated", cell(structure="RESERVOIR"), derived(),
     full_summary(has_reservoir_certificate=True, ancestry_certificate=reservoir_cert(),
                  lineage_complete=False),
     [{"flag": "RESERVOIR_CROSSED_A_MOAT", "reads": "historical", "evidence": {}}]),
    ("legacy_spontaneous_resemblance", cell(), derived(),
     full_summary(replication_events=0, births_similar_no_write=26),
     [{"flag": "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES", "reads": "historical",
       "evidence": {"first_replicator": {"fidelity": 0.95}}}]),
]


def make_rows(fixtures, whitelist):
    """Index rows (summary restricted to `whitelist`) and full rows, from one source."""
    index_rows, full_rows = [], []
    for name, c, d, s in fixtures:
        rec = controls_for(name)
        flags = specials.special_flags(c, d, s, rec)
        if not flags:
            continue
        index_rows.append({"run_id": name, "family": name[:8], "cell": c, "derived": d,
                           "specials": flags,
                           "summary": {k: s[k] for k in whitelist if k in s}})
        full_rows.append({"run_id": name, "family": name[:8], "cell": c, "derived": d,
                          "specials": flags, "summary": dict(s)})
    for name, c, d, s, flags in LEGACY_ROWS:
        index_rows.append({"run_id": name, "family": name[:8], "cell": c, "derived": d,
                           "specials": flags,
                           "summary": {k: s[k] for k in whitelist if k in s}})
        full_rows.append({"run_id": name, "family": name[:8], "cell": c, "derived": d,
                          "specials": flags, "summary": dict(s)})
    return index_rows, full_rows


def verdict_map(result):
    return {(v["run_id"], v["flag"]): (v["verdict"], v["why"]) for v in result["verdicts"]}


def main():
    ok = True
    fixtures = build_fixtures()
    index_rows, full_rows = make_rows(fixtures, adjudicate.INDEX_WHITELIST)

    classes = sorted({v["flag"] for v in
                      adjudicate.adjudicate(full_rows, source="full")["verdicts"]})
    print("special-result classes covered by the fixture set: %d" % len(classes))
    for c in classes:
        print("   ", c)
    if len(classes) < len(adjudicate.RULES):
        print("FAIL: fixture set does not cover every special-result class "
              "(%d of %d)" % (len(classes), len(adjudicate.RULES)))
        ok = False

    a_index = adjudicate.adjudicate(index_rows, source="INDEX")
    a_full = adjudicate.adjudicate(full_rows, source="per-run")
    m_index, m_full = verdict_map(a_index), verdict_map(a_full)

    print()
    print("%-26s %-42s %-14s %s" % ("run", "flag", "verdict", "index == per-run"))
    print("-" * 104)
    for key in sorted(m_full):
        vi, vf = m_index.get(key), m_full[key]
        same = vi == vf
        if not same:
            ok = False
        print("%-26s %-42s %-14s %s" % (
            key[0][:26], key[1][:42], vf[0],
            "yes" if same else "NO  index=%s" % (vi[0] if vi else "<absent>")))
    print("-" * 104)

    if m_index != m_full:
        print("FAIL: INDEX-only adjudication differs from per-run adjudication")
        ok = False
    else:
        print("PASS: %d verdicts identical from INDEX alone" % len(m_full))

    # The adjudicator's rejection branches must be live. Rows carrying a legacy flag
    # with nothing behind it have to be rejected for the RIGHT reason, not merely
    # rejected.
    print()
    print("adjudicator rejection branches on unrepaired-flag rows")
    print("%-32s %-14s %s" % ("run", "verdict", "reason"))
    print("-" * 96)
    EXPECT = {
        ("legacy_reservoir_no_cert", "RESERVOIR_CROSSED_A_MOAT"):
            ("INADMISSIBLE", "no complete easy-niche ancestry certificate"),
        ("legacy_reservoir_seeded", "RESERVOIR_CROSSED_A_MOAT"):
            ("INADMISSIBLE", "seeded instrument population"),
        ("legacy_reservoir_truncated", "RESERVOIR_CROSSED_A_MOAT"):
            ("INADMISSIBLE", "lineage incomplete"),
        ("legacy_spontaneous_resemblance", "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES"):
            ("INADMISSIBLE", "no evidence-backed replication event"),
    }
    for key, (want_v, want_why) in sorted(EXPECT.items()):
        got = m_index.get(key)
        good = got is not None and got[0] == want_v and want_why in got[1]
        if not good:
            ok = False
        print("%-32s %-14s %s" % (key[0][:32], got[0] if got else "<absent>",
                                  ("PASS" if good else "FAIL wanted %s / %r"
                                   % (want_v, want_why))))
    print("-" * 96)

    # No MISSING_FIELD may appear when the whitelist is intact.
    missing = [k for k, v in m_index.items() if v[0] == "MISSING_FIELD"]
    if missing:
        print("FAIL: whitelist incomplete, MISSING_FIELD on %s" % (missing,))
        ok = False
    else:
        print("PASS: no MISSING_FIELD verdicts under the declared whitelist")

    # ---------------- negative control ----------------
    # Drop each field some verdict requires and confirm the comparison breaks. A test
    # that cannot fail proves nothing about the whitelist.
    print()
    print("negative control: drop one required field at a time")
    print("%-34s %s" % ("dropped field", "detected"))
    print("-" * 60)
    required = sorted({f for fs in adjudicate.REQUIRED.values() for f in fs})
    undetected = []
    for field in required:
        reduced = tuple(f for f in adjudicate.INDEX_WHITELIST if f != field)
        idx_rows, fl_rows = make_rows(fixtures, reduced)
        got = verdict_map(adjudicate.adjudicate(idx_rows, source="INDEX"))
        want = verdict_map(adjudicate.adjudicate(fl_rows, source="per-run"))
        detected = got != want
        if not detected:
            undetected.append(field)
        print("%-34s %s" % (field, "yes" if detected else "NO - whitelist entry is dead"))
    print("-" * 60)
    if undetected:
        print("FAIL: dropping %s changed no verdict; those entries are not load-bearing"
              % ", ".join(undetected))
        ok = False
    else:
        print("PASS: every required whitelist field is load-bearing")

    # The adjudicator must contain no per-run read path at all.
    src = (pathlib.Path(__file__).resolve().parent.parent / "adjudicate.py").read_text(
        encoding="ascii")
    body = src.split('"""', 2)[-1]   # skip the module docstring, which names the defect
    if "RESULT.json" in body:
        print("FAIL: adjudicate.py still references a per-run record")
        ok = False
    else:
        print("PASS: adjudicate.py contains no per-run read path")

    print("\nT-P5:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
