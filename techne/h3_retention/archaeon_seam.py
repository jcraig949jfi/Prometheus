"""Seam: Archaeon's `Candidate` records -> Techne's STREAM_CONTRACT_V0 rows.

Archaeon's format is `archaeon/docs/h0h5/H3_STREAM_FORMAT.md`, written against my contract and
listing the diff itself. This implements exactly that diff and nothing more. Where the seam
WEAKENS a check, it says so in the seam record rather than reporting the strong check as passed
-- two of the five properties are weaker on the real stream than on my fixture, and pretending
otherwise would make the fixture qualification look like it transferred when it partly does not.

The diff, as Archaeon listed it:

  birth status   Archaeon: evaluated | failed (what happened at birth) + parent_ids.
                 Mine: SEEDED / MUTATED / RECOMBINED / REPLAYED (lineage kind).
                 ADOPTED: keep Archaeon's two-valued status, DERIVE lineage kind from
                 parent_ids (0 = SEEDED, 1 = MUTATED, 2+ = RECOMBINED). "REPLAYED" is dropped
                 from the derived vocabulary because Archaeon is right that it is a property of
                 the replay, not of the candidate.

  assay_ref      Archaeon: one string. Mine: {assay_id, assay_version, digest}.
                 ADOPTED: Techne's structured form at the seam. The digest is taken over the
                 ORIGINAL STRING, so the refusal is over the same object Archaeon refuses over.

  result_ref     Archaeon: replay_ref + byte_size. Mine: {kind, ref, digest, bytes}.
                 The resolver check is kept -- but see WEAKENED below.

  caps / ties    already agree; nothing to translate.

WEAKENED AT THE SEAM, and both are recorded in the seam report:

  W1  candidate_digest is CARRIED, NOT RECOMPUTED. My validator recomputes the digest from the
      payload it holds. Archaeon's digest is over the sealed spec (rule_hex + parameters),
      which does not travel in the record, so the consumer cannot recompute it. The digest is
      still an identity -- duplicates are detected, and a changed record is detectable against
      the stream digest -- but it is upstream's assertion rather than our verification.

  W2  result_ref carries NO CONTENT DIGEST. Archaeon's replay_ref resolves through SFE and the
      record declares byte_size, not a hash of the result. So recoverability is checked as
      "resolves, and the resolved length matches the declared byte_size" when a resolver is
      supplied, and structurally otherwise. It is not the digest check the fixture passed.
"""
from __future__ import annotations

import hashlib
from typing import Any, Iterable, Sequence

from . import stream as S

LINEAGE_BY_PARENT_COUNT = {0: "SEEDED", 1: "MUTATED"}   # 2+ -> RECOMBINED
ARCHAEON_BIRTH = ("evaluated", "failed")


class SeamError(ValueError):
    pass


def lineage_kind(n_parents: int) -> str:
    return LINEAGE_BY_PARENT_COUNT.get(n_parents, "RECOMBINED")


def structured_assay(assay_ref: str) -> dict:
    """Archaeon's single string -> my {assay_id, assay_version, digest}.

    The C3 form is 'ca_density_v0@<kind_version>:seed_root=...:n_ic=...:steps=...'. The split is
    on the FIRST '@' only; everything after it is the version, because the parameter tail is
    part of what identifies the instrument and dropping it would let two different measurement
    configurations share an assay identity -- exactly the mixture the fixed-assay rule exists to
    prevent. The digest is over the original string, unparsed, so the refusal is over the same
    object Archaeon refuses over.
    """
    if not isinstance(assay_ref, str) or not assay_ref:
        raise SeamError("assay_ref must be a non-empty string")
    assay_id, sep, version = assay_ref.partition("@")
    return {
        "assay_id": assay_id,
        "assay_version": version if sep else None,
        "digest": "sha256:" + hashlib.sha256(assay_ref.encode("utf-8")).hexdigest(),
        "original": assay_ref,
        "version_includes_parameter_tail": bool(sep) and ":" in version,
    }


def ranges_from_edges(edges: Sequence[Sequence[float]],
                      descriptors: Sequence[Sequence[float]]) -> list[list[float]]:
    """Archaeon bins descriptors by declared EDGES; my archive takes ranges + dims.

    A descriptor with k edges has k+1 bins. The range must cover every observed value, so it is
    taken from the edges EXTENDED by the observed min and max -- and the extension is reported,
    because a value outside the declared edges is a real thing to know about the descriptor
    declaration, not a formatting detail to absorb silently.
    """
    out = []
    for j, es in enumerate(edges):
        col = [d[j] for d in descriptors] or [0.0]
        lo = min(list(es) + col)
        hi = max(list(es) + col)
        pad = (hi - lo) * 1e-9 or 1e-9
        out.append([float(lo - pad), float(hi + pad)])
    return out


def dims_from_edges(edges: Sequence[Sequence[float]]) -> list[int]:
    return [len(es) + 1 for es in edges]


def from_candidates(candidates: Iterable[Any], *, edges: Sequence[Sequence[float]],
                    stream_id: str, resolver=None) -> tuple[S.Stream, dict]:
    """Build a validated Techne Stream from Archaeon Candidate records.

    Accepts the dataclass or a plain dict with the same fields, so this does not require
    importing archaeon.producer inside Techne's package.
    """
    rows_in = []
    for c in candidates:
        g = (lambda k: c.get(k) if isinstance(c, dict) else getattr(c, k))
        rows_in.append({k: g(k) for k in
                        ("stream_id", "candidate_digest", "birth_status", "assay_ref", "score",
                         "descriptors", "byte_size", "replay_ref", "parent_ids")})
    rows_in.sort(key=lambda r: r["stream_id"])
    if [r["stream_id"] for r in rows_in] != list(range(len(rows_in))):
        raise SeamError("stream_ids must be contiguous from 0; a gap is a missing candidate")

    for r in rows_in:
        if r["birth_status"] not in ARCHAEON_BIRTH:
            raise SeamError(f"birth_status {r['birth_status']!r} not in {ARCHAEON_BIRTH}")
        if (r["score"] is None) != (r["birth_status"] == "failed"):
            raise SeamError(f"stream_id {r['stream_id']}: a failed candidate has no score and an "
                            f"evaluated one has one")

    assays = {r["assay_ref"] for r in rows_in}
    if len(assays) > 1:
        raise SeamError(f"assay_ref changes mid-stream ({sorted(assays)}); a retention "
                        f"comparison needs one instrument")
    assay = structured_assay(next(iter(assays))) if assays else None

    descriptors = [tuple(float(x) for x in r["descriptors"]) for r in rows_in]
    dims = dims_from_edges(edges)
    ranges = ranges_from_edges(edges, descriptors)
    out_of_declared_edges = sum(
        1 for d in descriptors
        for j, es in enumerate(edges)
        if es and (d[j] < min(es) or d[j] > max(es)))

    cid = lambda sid: f"cand-{sid:05d}"
    raw_rows = []
    for r, desc in zip(rows_in, descriptors):
        parents = tuple(r["parent_ids"] or ())
        raw_rows.append({
            "seq": r["stream_id"],
            "candidate_id": cid(r["stream_id"]),
            "candidate_digest": r["candidate_digest"],
            "payload": None,                     # not carried; see W1
            "birth": {
                "status": lineage_kind(len(parents)),          # DERIVED lineage kind
                "archaeon_birth_status": r["birth_status"],    # kept verbatim
                "parent_ids": [cid(p) for p in parents],
                "birth_seq": r["stream_id"],
            },
            "assay_ref": assay,
            "measures": list(desc),
            "objective": r["score"],
            "result_ref": {"kind": "sfe_replay_ref", "ref": r["replay_ref"],
                           "digest": None, "bytes": int(r["byte_size"])},
            "payload_bytes": int(r["byte_size"]),
        })

    header = {
        "schema": S.SCHEMA, "stream_id": stream_id, "n_rows": len(raw_rows),
        "measure_dim": len(dims), "measure_ranges": ranges, "assay_ref": assay,
        "declared_order": "seq ascending, 0-based, contiguous",
        "produced_by": "techne/h3_retention/archaeon_seam.py from archaeon Candidate records",
        "descriptor_edges": [list(map(float, es)) for es in edges],
        "grid_dims": dims,
    }
    st = S.validate(header, raw_rows, resolver=resolver, seam_mode=True)

    n_failed = sum(1 for r in rows_in if r["birth_status"] == "failed")
    scores = [r["score"] for r in rows_in if r["score"] is not None]
    from collections import Counter
    score_hist = Counter(scores)
    modal_score, modal_n = (score_hist.most_common(1)[0] if score_hist else (None, 0))
    seam = {
        "seam": "archaeon.h3.stream.v0 -> techne.h3.stream/0",
        "format_doc": "archaeon/docs/h0h5/H3_STREAM_FORMAT.md",
        "n": len(raw_rows), "n_failed": n_failed,
        "assay_ref_structured": assay,
        "lineage_kind_derived_from_parent_ids": {
            k: sum(1 for r in raw_rows if r["birth"]["status"] == k)
            for k in ("SEEDED", "MUTATED", "RECOMBINED")},
        "grid_dims": dims, "measure_ranges": ranges,
        "descriptors_outside_declared_edges": out_of_declared_edges,
        "objective_degeneracy": {
            "n_scored": len(scores), "n_distinct_scores": len(score_hist),
            "modal_score": modal_score, "modal_count": modal_n,
            "modal_fraction": round(modal_n / len(scores), 4) if scores else None,
            "why_it_matters": ("exact ties are resolved FIRST_WRITER_WINS, so a stream whose "
                               "objective is mostly one value makes retention a function of "
                               "ARRIVAL ORDER rather than of quality, for that mass. That is a "
                               "property of the stream to report, not a parameter to tune."),
        },
        "WEAKENED_AT_THE_SEAM": [
            {"id": "W1", "property": "candidate digests",
             "fixture": "recomputed from the payload the row carries",
             "real_stream": "CARRIED ONLY -- the digest is over the sealed spec, which does not "
                            "travel in the record, so the consumer cannot recompute it",
             "still_holds": "duplicate detection, and tamper-detection against the stream digest",
             "lost": "independent verification that the digest matches the candidate"},
            {"id": "W2", "property": "recoverable results",
             "fixture": "resolver returns bytes; length AND sha256 both checked",
             "real_stream": "replay_ref carries no content digest, so with a resolver the check "
                            "is resolves-and-length-matches, and without one it is structural",
             "still_holds": "every non-retained candidate keeps a resolvable reference",
             "lost": "content verification of the resolved result"},
        ],
    }
    return st, seam
