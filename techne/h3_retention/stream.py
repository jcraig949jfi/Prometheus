"""The declared H3 candidate-stream contract, v0 -- reader, validator, and fixture builder.

Spec: techne/h3_retention/STREAM_CONTRACT_V0.md. This is a PROPOSAL standing in for a format
that does not exist yet (H3 alpha is NOT STARTED). It exists so the adapter can be built and
qualified now, and so that when Archaeon hands over the real format the difference is a diff
rather than a rewrite.

Every one of the five required properties is a REFUSAL here, not a convention. A validator
that warns is a validator that gets ignored; a stream that fails validation does not reach the
archive at all.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Iterable

SCHEMA = "techne.h3.stream/0"
BIRTH_STATUSES = ("SEEDED", "MUTATED", "RECOMBINED", "REPLAYED")


class StreamError(ValueError):
    """A stream that cannot be replayed. Carries the row and the property it violated."""

    def __init__(self, prop: str, message: str, *, seq: int | None = None):
        super().__init__(f"[{prop}]" + (f" seq={seq}" if seq is not None else "") + f": {message}")
        self.prop = prop
        self.seq = seq


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


@dataclass(frozen=True)
class Row:
    seq: int
    candidate_id: str
    candidate_digest: str
    payload: dict
    birth_status: str
    parent_ids: tuple[str, ...]
    assay_ref: dict
    measures: tuple[float, ...]
    objective: float | None
    result_ref: dict
    payload_bytes: int
    raw: dict = field(repr=False, default_factory=dict)


@dataclass
class Stream:
    header: dict
    rows: list[Row]
    validation: dict

    @property
    def measure_dim(self) -> int:
        return int(self.header["measure_dim"])

    @property
    def ranges(self) -> list[tuple[float, float]]:
        return [tuple(r) for r in self.header["measure_ranges"]]

    @property
    def stream_id(self) -> str:
        return self.header["stream_id"]


# --------------------------------------------------------------------------- validation
def _require(cond: bool, prop: str, msg: str, seq: int | None = None) -> None:
    if not cond:
        raise StreamError(prop, msg, seq=seq)


def validate(header: dict, raw_rows: list[dict], *, resolver=None, seam_mode: bool = False) -> Stream:
    """Refuse anything that would make a retention replay ambiguous.

    `resolver`, when given, is called as resolver(result_ref) -> bytes and is used to check
    that the declared byte count is the truth rather than the producer's claim. Without one,
    recoverability is checked structurally only, and the validation record says so.

    `seam_mode` is for a stream that arrives from an upstream producer rather than from a
    fixture this seat built. TWO checks weaken, and they weaken in a NAMED way rather than
    being switched off:

      * a row with `payload: None` carries its digest instead of proving it. The digest is
        still an identity -- duplicates are found, tampering is detectable against the stream
        digest -- but it is upstream's assertion.
      * a `result_ref` with `digest: None` is checked for resolution and declared length only.

    Neither weakening is inferred from the data: `seam_mode` has to be asked for, and the
    validation record reports exactly which rows used it. A validator that silently relaxes
    when it meets data it cannot check is not a validator.
    """
    _require(header.get("schema") == SCHEMA, "header",
             f"schema must be {SCHEMA!r}, got {header.get('schema')!r}")
    for k in ("stream_id", "n_rows", "measure_dim", "measure_ranges", "assay_ref"):
        _require(k in header, "header", f"header is missing {k!r}")
    dim = int(header["measure_dim"])
    ranges = [tuple(r) for r in header["measure_ranges"]]
    _require(len(ranges) == dim, "header",
             f"measure_ranges has {len(ranges)} entries for measure_dim {dim}")
    fixed_assay = header["assay_ref"]

    _require(len(raw_rows) == int(header["n_rows"]), "header",
             f"header declares n_rows={header['n_rows']} but the stream has {len(raw_rows)}")

    rows: list[Row] = []
    seen_ids: dict[str, int] = {}
    seen_digests: dict[str, list[str]] = {}
    unresolved_refs: list[str] = []
    carried_digests = 0
    undigested_refs = 0

    for i, r in enumerate(raw_rows):
        seq = r.get("seq")

        # --- 1. stable ordered ids
        _require(seq == i, "ordered_ids",
                 f"seq must be 0-based and contiguous; expected {i}, got {seq!r}", seq=seq)
        cid = r.get("candidate_id")
        _require(isinstance(cid, str) and cid, "ordered_ids", "candidate_id must be a non-empty string", seq=seq)
        _require(cid not in seen_ids, "ordered_ids",
                 f"duplicate candidate_id {cid!r}, first seen at seq={seen_ids.get(cid)}", seq=seq)

        # --- 2. candidate digests
        payload = r.get("payload")
        if payload is None and seam_mode:
            _require(isinstance(r.get("candidate_digest"), str) and r["candidate_digest"],
                     "digests", "a carried digest must still be a non-empty string", seq=seq)
            carried_digests += 1
        else:
            _require(isinstance(payload, dict), "digests", "payload must be an object", seq=seq)
            want = digest(payload)
            _require(r.get("candidate_digest") == want, "digests",
                     f"candidate_digest {r.get('candidate_digest')!r} does not match the payload "
                     f"(recomputed {want})", seq=seq)

        # --- 3. birth status
        birth = r.get("birth") or {}
        status = birth.get("status")
        _require(status in BIRTH_STATUSES, "birth",
                 f"birth.status must be one of {BIRTH_STATUSES}, got {status!r}", seq=seq)
        parents = tuple(birth.get("parent_ids") or ())
        if status == "SEEDED":
            _require(not parents, "birth", "SEEDED candidates must have no parents", seq=seq)
        else:
            _require(bool(parents), "birth", f"{status} requires at least one parent", seq=seq)
        for p in parents:
            _require(p in seen_ids, "birth",
                     f"parent {p!r} has not appeared earlier in the stream; a stream whose "
                     f"parents follow their children cannot be replayed forward", seq=seq)
            _require(seen_ids[p] < i, "birth", f"parent {p!r} is not strictly earlier", seq=seq)

        # --- 4. fixed assay references
        _require(r.get("assay_ref") == fixed_assay, "fixed_assay",
                 f"assay_ref {r.get('assay_ref')!r} differs from the header's {fixed_assay!r}; "
                 f"a stream that changes assay mid-way makes a policy comparison a mixture of "
                 f"policy effect and instrument change", seq=seq)

        # --- 5. recoverable results
        rref = r.get("result_ref") or {}
        for k in ("kind", "ref", "digest", "bytes"):
            _require(k in rref, "recoverable", f"result_ref is missing {k!r}", seq=seq)
        _require(bool(rref.get("ref")), "recoverable", "result_ref.ref must be non-empty", seq=seq)
        if rref.get("digest") is None:
            _require(seam_mode, "recoverable",
                     "result_ref carries no content digest; only a seam-mode stream may do that",
                     seq=seq)
            undigested_refs += 1
        if resolver is not None:
            blob = resolver(rref)
            _require(blob is not None, "recoverable",
                     f"result_ref {rref['ref']!r} does not resolve", seq=seq)
            _require(len(blob) == int(rref["bytes"]), "recoverable",
                     f"result_ref declares {rref['bytes']} bytes, resolver returned {len(blob)}",
                     seq=seq)
            if rref.get("digest") is not None:
                got = "sha256:" + hashlib.sha256(blob).hexdigest()
                _require(got == rref["digest"], "recoverable",
                         f"result_ref digest {rref['digest']} != recomputed {got}", seq=seq)
        else:
            unresolved_refs.append(rref["ref"])

        # --- measures inside the declared space
        meas = r.get("measures")
        _require(isinstance(meas, (list, tuple)) and len(meas) == dim, "measures",
                 f"measures must have length {dim}, got {meas!r}", seq=seq)
        for j, (m, (lo, hi)) in enumerate(zip(meas, ranges)):
            _require(lo <= m <= hi, "measures",
                     f"measure[{j}]={m} is outside the declared range [{lo}, {hi}]", seq=seq)

        pb = r.get("payload_bytes")
        _require(isinstance(pb, int) and pb >= 0, "caps",
                 f"payload_bytes must be a non-negative int, got {pb!r}", seq=seq)

        seen_ids[cid] = i
        seen_digests.setdefault(r["candidate_digest"], []).append(cid)
        rows.append(Row(
            seq=i, candidate_id=cid, candidate_digest=r["candidate_digest"], payload=payload,
            birth_status=status, parent_ids=parents, assay_ref=r["assay_ref"],
            measures=tuple(float(x) for x in meas),
            objective=None if r.get("objective") is None else float(r["objective"]),
            result_ref=rref, payload_bytes=pb, raw=r,
        ))

    # DETECTED, not refused: the same content under two ids. Legal, and it inflates every
    # per-candidate count a retention policy reports, so it is surfaced.
    dupes = {d: ids for d, ids in seen_digests.items() if len(ids) > 1}

    validation = {
        "schema": SCHEMA,
        "seam_mode": seam_mode,
        "digests_carried_not_recomputed": carried_digests,
        "result_refs_without_a_content_digest": undigested_refs,
        "stream_id": header["stream_id"],
        "n_rows": len(rows),
        "properties_checked": ["ordered_ids", "digests", "birth", "fixed_assay",
                              "recoverable", "measures", "caps"],
        "result_refs_resolved": resolver is not None,
        "recoverability_check": (("RESOLVED; LENGTH VERIFIED. Content digest NOT verified for "
                                  f"{undigested_refs} of {len(rows)} rows -- the producer "
                                  f"carries no result digest (seam W2)")
                                 if resolver is not None and undigested_refs else
                                 "BYTES AND DIGEST VERIFIED THROUGH THE RESOLVER"
                                 if resolver is not None else
                                 "STRUCTURAL ONLY -- no resolver supplied, so the declared "
                                 "bytes and digest are the producer's claim, not a "
                                 "verified fact"),
        "unresolved_result_refs": len(unresolved_refs),
        "duplicate_digests_under_distinct_ids": dupes,
        "n_duplicate_content_groups": len(dupes),
        "birth_status_counts": {s: sum(1 for r in rows if r.birth_status == s)
                                for s in BIRTH_STATUSES},
        "stream_digest": digest({"header": header, "rows": raw_rows}),
    }
    return Stream(header=header, rows=rows, validation=validation)


# --------------------------------------------------------------------------- io
def read_jsonl(path: str | pathlib.Path, *, resolver=None) -> Stream:
    lines = [ln for ln in pathlib.Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]
    header = json.loads(lines[0])
    rows = [json.loads(ln) for ln in lines[1:]]
    return validate(header, rows, resolver=resolver)


def write_jsonl(path: str | pathlib.Path, header: dict, rows: Iterable[dict]) -> pathlib.Path:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = [json.dumps(header, sort_keys=True)]
    body += [json.dumps(r, sort_keys=True) for r in rows]
    p.write_text("\n".join(body) + "\n", encoding="utf-8")
    return p
