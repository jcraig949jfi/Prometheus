"""Build the declared fixture streams. Deterministic; no RNG that is not seeded and recorded.

    python -m techne.h3_retention.build_fixture

Two streams, and the second exists because of a specific failure mode:

  stream_v0.jsonl          the general fixture -- every birth status, real collisions, an
                           EXACT tie, a duplicate-content pair under two ids, mixed payload
                           sizes. Caps set so NEITHER binds.
  stream_v0_capbind.jsonl  the same candidates against caps chosen to make BOTH bind, so the
                           cap paths are exercised rather than merely implemented.

A cap that never fires on any fixture is a cap nobody has tested. The contract says a run
where neither bound is not evidence the caps work, so a fixture that makes them bind is part
of the deliverable, not an extra.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from . import stream as S

ASSAY = {
    "assay_id": "fixture_assay_v0",
    "assay_version": "0.1.0",
    "digest": "sha256:" + hashlib.sha256(b"fixture_assay_v0/0.1.0").hexdigest(),
}

MEASURE_RANGES = [[0.0, 1.0], [0.0, 1.0]]
DIM = 2

# (id, objective, measures, birth_status, parents, payload_bytes, note)
# Cells under a 4x4 grid over [0,1]^2: measure 0.125->col 0, 0.375->1, 0.625->2, 0.875->3.
SPEC = [
    ("c000", 1.0, (0.125, 0.125), "SEEDED",     (),                 1200,
     "new cell (0,0)"),
    ("c001", 5.0, (0.375, 0.125), "SEEDED",     (),                  900,
     "new cell (1,0)"),
    ("c002", 2.0, (0.125, 0.125), "MUTATED",    ("c000",),          1500,
     "collision with c000, HIGHER -> replaces"),
    ("c003", 0.5, (0.125, 0.125), "MUTATED",    ("c000",),           700,
     "collision, LOWER -> rejected by the archive"),
    ("c004", 5.0, (0.375, 0.125), "MUTATED",    ("c001",),           800,
     "EXACT TIE with c001 -> first-writer-wins keeps c001"),
    ("c005", 3.0, (0.625, 0.625), "RECOMBINED", ("c001", "c002"),   2400,
     "new cell (2,2); the largest payload, so it is the one a tight byte cap bites"),
    ("c006", 3.0, (0.875, 0.625), "RECOMBINED", ("c002", "c005"),    600,
     "new cell (3,2); equal objective, DIFFERENT cell -> both kept"),
    ("c007", 4.0, (0.875, 0.875), "REPLAYED",   ("c006",),           500,
     "new cell (3,3)"),
    ("c008", 9.0, (0.625, 0.625), "MUTATED",    ("c005",),           300,
     "improves cell (2,2); byte DELTA is negative (300 - 2400)"),
    ("c009", 1.0, (0.125, 0.875), "SEEDED",     (),                  400,
     "new cell (0,3); duplicate CONTENT of c000 under a different id"),
]

# c009 deliberately carries the same payload as c000 so the validator's duplicate-content
# detector has something to find. Identical content, different objective and cell -- which is
# exactly the case that inflates a per-candidate count without being illegal.
DUP_OF = {"c009": "c000"}


def _payload(cid: str) -> dict:
    src = DUP_OF.get(cid, cid)
    return {"kind": "fixture_candidate", "genome": [ord(ch) for ch in src], "arity": len(src)}


def build_rows() -> list[dict]:
    rows = []
    for seq, (cid, obj, meas, status, parents, pbytes, note) in enumerate(SPEC):
        payload = _payload(cid)
        blob = json.dumps({"candidate": cid, "result": "fixture", "objective": obj},
                          sort_keys=True).encode("utf-8")
        rows.append({
            "seq": seq,
            "candidate_id": cid,
            "candidate_digest": S.digest(payload),
            "payload": payload,
            "birth": {"status": status, "parent_ids": list(parents), "birth_seq": seq},
            "assay_ref": ASSAY,
            "measures": list(meas),
            "objective": obj,
            "result_ref": {
                "kind": "inline_fixture",
                "ref": f"fixture://{cid}",
                "digest": "sha256:" + hashlib.sha256(blob).hexdigest(),
                "bytes": len(blob),
            },
            "payload_bytes": pbytes,
            "note": note,
        })
    return rows


def resolver(result_ref: dict) -> bytes | None:
    """The fixture's own resolver, so recoverability is VERIFIED rather than assumed."""
    cid = result_ref["ref"].split("://", 1)[1]
    for seq, (c, obj, *_rest) in enumerate(SPEC):
        if c == cid:
            return json.dumps({"candidate": cid, "result": "fixture", "objective": obj},
                              sort_keys=True).encode("utf-8")
    return None


def header(stream_id: str, rows: list[dict]) -> dict:
    return {
        "schema": S.SCHEMA,
        "stream_id": stream_id,
        "n_rows": len(rows),
        "measure_dim": DIM,
        "measure_ranges": MEASURE_RANGES,
        "assay_ref": ASSAY,
        "declared_order": "seq ascending, 0-based, contiguous",
        "produced_by": "techne/h3_retention/build_fixture.py",
        "NOT_ARCHAEONS_FORMAT": "This is a Techne PROPOSAL standing in until Archaeon hands "
                                "over the real H3 stream format from Track B's C3 corpus or "
                                "Track E's NK. It will lose to the real one.",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(pathlib.Path(__file__).resolve().parent / "fixture"))
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out_dir)

    rows = build_rows()
    written = []
    for sid, name in (("h3_fixture_v0", "stream_v0.jsonl"),
                      ("h3_fixture_v0_capbind", "stream_v0_capbind.jsonl")):
        h = header(sid, rows)
        p = S.write_jsonl(out / name, h, rows)
        st = S.read_jsonl(p, resolver=resolver)
        written.append((p, st))
        print(f"{name}: {st.validation['n_rows']} rows, digest {st.validation['stream_digest']}")
        print(f"   births {st.validation['birth_status_counts']}")
        print(f"   duplicate-content groups {st.validation['n_duplicate_content_groups']} "
              f"{st.validation['duplicate_digests_under_distinct_ids']}")
        print(f"   recoverability: {st.validation['recoverability_check']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
