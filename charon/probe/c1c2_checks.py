"""C1 and C2 of the Charon ruling of 2026-09-01 as executable, design-agnostic checks.

Source ruling: charon/probe/RULINGS_2026-09-01.md sections 1c (C1), 1d (C2), 1e (ordering).
Restated here on Archaeon's prompt (roles/Archaeon/prompts/2026-09-11_comms/CHARON.md item 2)
so that Aporia can apply them to any successor design of the metabolization probe, and Ergon
can wire them, without either reading the ruling's prose.

The two checks share one shape: each takes the RAW artifacts (pool bytes, prepass rows), never
the design's own summary of them, and returns a Verdict with the rows that produced it. A
verdict without rows is an assertion (base rule 4). Each verdict is PASS, FAIL or
INDETERMINATE, and INDETERMINATE is reported with the reason nothing could have fired.

    C1  POOL FINGERPRINT.  A run may read a residue arm only if its receipt names, for every
        pool it draws from, the sha256 and record count of that pool, AND those values equal
        what this check recomputes from the pool bytes, AND (when a preregistration is given)
        equal what the preregistration names. The receipt's quoted sha is never trusted on
        its own: the cheat where a receipt copies the preregistered sha over a pool whose
        bytes differ is a FAIL, because the check hashes the bytes itself.

    C2  TRANSPORT FAILURE IS NOT RESIDUE.  A row whose status is not "ok" records that no
        attempt was made. If the design's loader renders any such rep-1 row as a residue
        record, that is a fabrication and the check FAILS, naming the rows. The check is
        INDETERMINATE when the pool holds no transport-failed rep-1 row (nothing could have
        fired) -- which is why a gate-fire against a PLANTED failed row is the only way to
        make it decidable on a clean pool -- and INDETERMINATE when the loader admits nothing
        at all (excluding everything trivially renders no fabrication; that is a cheat, not a
        pass). A design that preregisters inclusion of failed rows as deliberate passes only
        if it supplies gate-fire evidence naming a planted row its own gate observed.

Neither check imports the probe's own code. The loader under test is passed in, so a
successor design supplies its own; the default used by the gate-fire script is
ergon.probe.assemble.load_prepass, the loader the ruling measured.

Design-agnostic contract (what a successor must expose to be checkable):
    - every input pool as a file whose records are one JSON object per line;
    - a run receipt (any JSON object) carrying `prepass_fingerprints`:
          {"<pool name>": {"sha256": <hex over LF-normalised bytes>, "record_count": <int>}}
    - optionally a preregistration object carrying the same field;
    - each raw row carrying a `status` field and an identity readable as (rep, uid), either
      FLAT {"rep": int, "uid": str} or KEY {"key": [rep, uid]} (the two wire forms the ruling
      found live);
    - a loader callable(path) -> iterable of objects with a `uid` and, so that a row and not
      a uid is judged, a `seq` (the 1-based line index of the raw row) attribute or key.

Line endings: the sha256 is computed over the bytes with CRLF normalised to LF, so the same
pool hashes the same on a CRLF checkout and an LF checkout. The record count is the number of
non-blank lines. Both are stated in the verdict.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

PASS = "PASS"
FAIL = "FAIL"
INDETERMINATE = "INDETERMINATE"

RULING = "charon/probe/RULINGS_2026-09-01.md"
CHECKS_VERSION = "c1c2_checks/1.0 (2026-09-11)"


@dataclass
class Verdict:
    check: str
    verdict: str
    reasons: list[str] = field(default_factory=list)
    rows: list[dict[str, Any]] = field(default_factory=list)
    eligible_count: Optional[int] = None
    fired_count: Optional[int] = None
    detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "verdict": self.verdict,
            "reasons": list(self.reasons),
            "eligible_count": self.eligible_count,
            "fired_count": self.fired_count,
            "rows": list(self.rows),
            "detail": dict(self.detail),
            "ruling": RULING,
            "checks_version": CHECKS_VERSION,
        }


# --------------------------------------------------------------------------------------------
# shared readers
# --------------------------------------------------------------------------------------------

def pool_fingerprint(path: pathlib.Path) -> dict[str, Any]:
    """sha256 over LF-normalised bytes and the count of non-blank lines. Reads bytes, not the
    design's summary of them."""
    data = pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")
    count = sum(1 for line in data.split(b"\n") if line.strip())
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "record_count": count,
        "normalisation": "CRLF->LF before hashing; record_count = non-blank lines",
    }


def row_identity(d: Mapping[str, Any]) -> tuple[int, Optional[str]]:
    """(rep, uid) from either wire form. Unreadable rep -> -1. Mirrors the contract the ruling
    found live (FLAT wins when present); reimplemented here so the check does not import the
    code under test."""
    if "rep" in d:
        rep, uid = d.get("rep"), d.get("uid")
    else:
        key = d.get("key")
        if isinstance(key, (list, tuple)) and len(key) >= 2:
            rep, uid = key[0], key[1]
        else:
            rep, uid = None, d.get("uid")
    try:
        rep = int(rep)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        rep = -1
    return rep, (str(uid) if uid is not None else None)


def read_rows(path: pathlib.Path) -> list[tuple[int, dict[str, Any]]]:
    out: list[tuple[int, dict[str, Any]]] = []
    with open(path, encoding="utf-8") as fh:
        for seq, line in enumerate(fh, start=1):
            if line.strip():
                out.append((seq, json.loads(line)))
    return out


def _field(rec: Any, name: str) -> Any:
    return rec.get(name) if isinstance(rec, Mapping) else getattr(rec, name, None)


def _uid_of(rec: Any) -> Optional[str]:
    v = _field(rec, "uid")
    return None if v is None else str(v)


def _seq_of(rec: Any) -> Optional[int]:
    """The 1-based line index of the raw row the record was rendered from, when the loader
    exposes it. A uid is not a row: the ruling's block A has 206 rep-1 rows under 200 uids
    because a failed call was retried under the same uid, so the check must key on the row."""
    v = _field(rec, "seq")
    try:
        return None if v is None else int(v)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------------------------
# C1 -- pool fingerprint
# --------------------------------------------------------------------------------------------

def check_c1_pool_fingerprint(
    receipt: Mapping[str, Any],
    pools: Mapping[str, pathlib.Path],
    preregistration: Optional[Mapping[str, Any]] = None,
    *,
    field_name: str = "prepass_fingerprints",
) -> Verdict:
    """C1. FAIL if the receipt does not fingerprint every pool, or any quoted fingerprint
    differs from the bytes, or (when given) the preregistration names a different one.
    INDETERMINATE only when everything decidable passed and the preregistration names no
    fingerprint for some pool, so the run-vs-prereg half could not be decided."""
    v = Verdict(check="C1_pool_fingerprint", verdict=PASS)
    quoted = receipt.get(field_name) if isinstance(receipt, Mapping) else None
    prereg_fp = (preregistration or {}).get(field_name) if preregistration else None
    fails = 0
    indet = 0
    for name, path in pools.items():
        path = pathlib.Path(path)
        row: dict[str, Any] = {"pool": name, "path": str(path).replace("\\", "/")}
        if not path.exists():
            row["result"] = FAIL
            row["reason"] = "POOL_ABSENT"
            fails += 1
            v.rows.append(row)
            continue
        actual = pool_fingerprint(path)
        row["actual"] = actual
        q = (quoted or {}).get(name) if isinstance(quoted, Mapping) else None
        if not isinstance(q, Mapping) or "sha256" not in q or "record_count" not in q:
            row["result"] = FAIL
            row["reason"] = "RECEIPT_UNFINGERPRINTED"
            fails += 1
            v.rows.append(row)
            continue
        row["quoted"] = {"sha256": q.get("sha256"), "record_count": q.get("record_count")}
        if str(q.get("sha256")).lower() != actual["sha256"] or int(q.get("record_count")) != actual["record_count"]:
            row["result"] = FAIL
            row["reason"] = "POOL_MOVED (quoted fingerprint != bytes)"
            fails += 1
            v.rows.append(row)
            continue
        if preregistration is not None:
            p = (prereg_fp or {}).get(name) if isinstance(prereg_fp, Mapping) else None
            if not isinstance(p, Mapping) or "sha256" not in p:
                row["result"] = INDETERMINATE
                row["reason"] = "PREREG_NAMES_NO_FINGERPRINT"
                indet += 1
                v.rows.append(row)
                continue
            row["preregistered"] = {"sha256": p.get("sha256"), "record_count": p.get("record_count")}
            if str(p.get("sha256")).lower() != actual["sha256"] or (
                "record_count" in p and int(p["record_count"]) != actual["record_count"]
            ):
                row["result"] = FAIL
                row["reason"] = "PREREG_MISMATCH (bytes != preregistered fingerprint)"
                fails += 1
                v.rows.append(row)
                continue
        row["result"] = PASS
        v.rows.append(row)
    v.eligible_count = len(pools)
    v.fired_count = fails
    if fails:
        v.verdict = FAIL
    elif indet:
        v.verdict = INDETERMINATE
    if not pools:
        v.verdict = INDETERMINATE
        v.reasons.append("NO_POOLS_DECLARED: nothing could have fired")
    v.reasons.extend(sorted({r["reason"] for r in v.rows if r.get("reason")}))
    v.detail["receipt_has_field"] = isinstance(quoted, Mapping)
    v.detail["preregistration_given"] = preregistration is not None
    return v


# --------------------------------------------------------------------------------------------
# C2 -- transport failure is not residue
# --------------------------------------------------------------------------------------------

def check_c2_transport_not_residue(
    pool_path: pathlib.Path,
    loader: Callable[[pathlib.Path], Iterable[Any]],
    *,
    ok_status: str = "ok",
    inclusion_preregistered: bool = False,
    gate_fire_evidence: Optional[Mapping[str, Any]] = None,
) -> Verdict:
    """C2. Enumerate the raw rep-1 rows whose status is not `ok_status` (transport-failed:
    no attempt was made). Run the loader. FAIL if any transport-failed uid is among the
    loader's admitted uids. INDETERMINATE if no rep-1 row is transport-failed (nothing could
    have fired), if any rep-1 row carries no status field (the check cannot classify it), or
    if the loader admits nothing while ok rows exist (excluding everything is not a pass).

    inclusion_preregistered=True is the ruling's other branch: the design declares it renders
    failed rows deliberately. Then the check passes only with gate_fire_evidence that names a
    `planted_uid` and shows `observed_by_gate` true; otherwise FAIL."""
    v = Verdict(check="C2_transport_not_residue", verdict=PASS)
    pool_path = pathlib.Path(pool_path)
    rows = read_rows(pool_path)
    rep1 = [(seq, d) for seq, d in rows if row_identity(d)[0] == 1]
    no_status = [(seq, d) for seq, d in rep1 if "status" not in d]
    failed = [(seq, d) for seq, d in rep1 if "status" in d and str(d.get("status")) != ok_status]
    ok_rows = [(seq, d) for seq, d in rep1 if str(d.get("status")) == ok_status]
    failed_uids = {row_identity(d)[1] for _, d in failed}
    failed_keys = {(row_identity(d)[1], seq) for seq, d in failed}
    ok_uids = {row_identity(d)[1] for _, d in ok_rows}

    admitted: list[Any] = list(loader(pool_path))
    admitted_uids = {u for u in (_uid_of(r) for r in admitted) if u is not None}
    admitted_keys = {(_uid_of(r), _seq_of(r)) for r in admitted if _uid_of(r) is not None}
    loader_exposes_seq = all(k[1] is not None for k in admitted_keys) if admitted_keys else False
    # Decide per failed ROW. With a seq on the loader's output the row is identified exactly.
    # Without one, a failed uid that is ALSO the uid of an ok row cannot be attributed
    # (the loader may have rendered only the retry): that row is UNATTRIBUTABLE, and the
    # check is INDETERMINATE for it rather than fired.
    rendered_failed_keys: set[tuple[Optional[str], int]] = set()
    unattributable_keys: set[tuple[Optional[str], int]] = set()
    for uid, seq in failed_keys:
        if loader_exposes_seq:
            if (uid, seq) in admitted_keys:
                rendered_failed_keys.add((uid, seq))
        elif uid in admitted_uids:
            if uid in ok_uids:
                unattributable_keys.add((uid, seq))
            else:
                rendered_failed_keys.add((uid, seq))
    rendered_failed = sorted({u for u, _ in rendered_failed_keys if u is not None})

    v.detail.update({
        "pool": str(pool_path).replace("\\", "/"),
        "fingerprint": pool_fingerprint(pool_path),
        "raw_rows": len(rows),
        "rep1_rows": len(rep1),
        "rep1_ok_rows": len(ok_rows),
        "rep1_transport_failed_rows": len(failed),
        "rep1_transport_failed_uids": len(failed_uids),
        "rep1_rows_without_status": len(no_status),
        "loader_admitted_records": len(admitted),
        "loader_admitted_uids": len(admitted_uids),
        "loader_exposes_seq": loader_exposes_seq,
        "transport_failed_rows_rendered": len(rendered_failed_keys),
        "transport_failed_uids_rendered": len(rendered_failed),
        "transport_failed_rows_unattributable": len(unattributable_keys),
        "failed_uids_shared_with_an_ok_row": len(failed_uids & ok_uids),
        "error_types": _count(str(d.get("error_type")) for _, d in failed),
        "inclusion_preregistered": inclusion_preregistered,
    })
    for seq, d in failed:
        rep, uid = row_identity(d)
        v.rows.append({
            "seq": seq, "uid": uid, "status": d.get("status"), "error_type": d.get("error_type"),
            "attempt_text_len": len(str(d.get("attempt_text") or "")),
            "uid_shared_with_ok_row": uid in ok_uids,
            "rendered_by_loader": (uid, seq) in rendered_failed_keys,
            "unattributable": (uid, seq) in unattributable_keys,
        })
    v.eligible_count = len(failed_keys)
    v.fired_count = len(rendered_failed_keys)

    if no_status:
        v.verdict = INDETERMINATE
        v.reasons.append(f"ROWS_WITHOUT_STATUS: {len(no_status)} rep-1 rows carry no status field")
    if not failed:
        v.verdict = INDETERMINATE
        v.reasons.append("NOTHING_COULD_HAVE_FIRED: no transport-failed rep-1 row in the pool; plant one")
        return v
    if not admitted and ok_rows:
        v.verdict = INDETERMINATE
        v.reasons.append("LOADER_ADMITS_NOTHING: excluding every row is not a pass")
        return v
    if unattributable_keys and not rendered_failed_keys:
        v.verdict = INDETERMINATE
        v.reasons.append(f"UNATTRIBUTABLE: {len(unattributable_keys)} failed rows share a uid with an ok row and the loader exposes no seq")
        return v
    if rendered_failed_keys:
        if inclusion_preregistered:
            ev = gate_fire_evidence or {}
            planted = ev.get("planted_uid")
            if planted and ev.get("observed_by_gate") is True and planted in failed_uids:
                v.verdict = PASS if v.verdict != INDETERMINATE else v.verdict
                v.reasons.append(f"INCLUSION_PREREGISTERED_AND_GATE_FIRED on {planted}")
                v.detail["gate_fire_evidence"] = dict(ev)
                return v
            v.verdict = FAIL
            v.reasons.append("INCLUSION_PREREGISTERED_WITHOUT_GATE_FIRE: no planted row observed by the design's gate")
            return v
        v.verdict = FAIL
        v.reasons.append(f"FABRICATION_RENDERED: {len(rendered_failed_keys)} transport-failed rows admitted as residue")
        v.detail["rendered_failed_uids"] = rendered_failed
        v.detail["rendered_failed_rows"] = sorted([u, s] for u, s in rendered_failed_keys)
        if unattributable_keys:
            v.reasons.append(f"UNATTRIBUTABLE_ALSO: {len(unattributable_keys)} further failed rows share a uid with an ok row")
        return v
    if v.verdict == PASS:
        v.reasons.append(f"EXCLUDED: {len(failed_keys)} transport-failed rows present, 0 rendered")
    return v


def _count(items: Iterable[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for it in items:
        out[it] = out.get(it, 0) + 1
    return dict(sorted(out.items()))


# --------------------------------------------------------------------------------------------
# ordering (1e) -- a receipt-level predicate, not a code-level one
# --------------------------------------------------------------------------------------------

def check_ordering_c1c2_before_collection(receipt: Mapping[str, Any], *, field_name: str = "c1c2") -> Verdict:
    """1e. A run that collected or read a residue arm must carry, in its own receipt, the C1
    and C2 verdicts it ran BEFORE collection, both PASS. A receipt without them is a run that
    collected under no guard, whatever the code looked like at the time. This is the executable
    form of 'C1 and C2 must land before or with the s4 repair'."""
    v = Verdict(check="ORDERING_c1c2_before_collection", verdict=PASS)
    block = receipt.get(field_name) if isinstance(receipt, Mapping) else None
    if not isinstance(block, Mapping):
        v.verdict = FAIL
        v.reasons.append("RECEIPT_CARRIES_NO_C1C2: collection ran under no guard")
        v.eligible_count, v.fired_count = 1, 1
        return v
    for name in ("C1_pool_fingerprint", "C2_transport_not_residue"):
        sub = block.get(name)
        verdict = sub.get("verdict") if isinstance(sub, Mapping) else None
        v.rows.append({"check": name, "verdict": verdict})
        if verdict != PASS:
            v.verdict = FAIL
            v.reasons.append(f"{name}: {verdict or 'ABSENT'}")
    v.eligible_count, v.fired_count = 2, sum(1 for r in v.rows if r["verdict"] != PASS)
    return v


__all__: Sequence[str] = (
    "PASS", "FAIL", "INDETERMINATE", "Verdict",
    "pool_fingerprint", "row_identity", "read_rows",
    "check_c1_pool_fingerprint", "check_c2_transport_not_residue",
    "check_ordering_c1c2_before_collection",
)
