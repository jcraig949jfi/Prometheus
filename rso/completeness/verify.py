"""C-018-T011 completeness verifier: an analyzer calls verify() BEFORE it reads a verdict.

    verify(manifest, presented, sources=None, native_digest=None, pinned_manifest_sha256=None) -> Result

presented     list of {"id": str, "rows": [dict], "meta": dict}; the loader (an engine wrapper) fixes the id.
sources       {path: sha256} of the code actually present now; the manifest's `sources` must all be supplied and equal.
native_digest the engine's own rows digest (e.g. receipt.sha256_hex) when its meta carries one in `rows_sha256`: it lets the
              verifier tell ALTERED (bytes no longer match what the writer recorded) from SUBSTITUTED (a different but
              internally consistent artifact, e.g. a re-run or a dev shard under a frozen identity).
status        COMPLETE | COMPLETE_EARLY_STOP | INCOMPLETE | REFUSED.  REFUSED outranks INCOMPLETE; `missing` is still filled.
Only COMPLETE and COMPLETE_EARLY_STOP license reading a verdict; COMPLETE_EARLY_STOP only through a rule declared in the sealed
manifest whose trigger is observed in VERIFIED rows (README s early stop).
"""
from collections import Counter

from rso.completeness import manifest as M

COMPLETE, COMPLETE_EARLY_STOP, INCOMPLETE, REFUSED = "COMPLETE", "COMPLETE_EARLY_STOP", "INCOMPLETE", "REFUSED"
DUPLICATE, CONFLICTING, SUBSTITUTED, ALTERED, UNEXPECTED = "DUPLICATE", "CONFLICTING", "SUBSTITUTED", "ALTERED", "UNEXPECTED"
SEED_PARTITION, COUNT_MISMATCH, SOURCE_MISMATCH, MANIFEST_ALTERED = "SEED_PARTITION", "COUNT_MISMATCH", "SOURCE_MISMATCH", "MANIFEST_ALTERED"


class Result:
    def __init__(self, status, missing, findings, early_stop=None, manifest_sha256=None):
        self.status, self.missing, self.findings = status, missing, findings
        self.early_stop, self.manifest_sha256 = early_stop, manifest_sha256

    def kinds(self):
        return {f["kind"] for f in self.findings}

    @property
    def licenses_verdict(self):
        return self.status in (COMPLETE, COMPLETE_EARLY_STOP)

    def to_dict(self):
        return dict(status=self.status, missing=self.missing, findings=self.findings, early_stop=self.early_stop,
                    manifest_sha256=self.manifest_sha256)

    def __repr__(self):
        return "Result(%s, missing=%s, findings=%s)" % (self.status, self.missing, [(f["kind"], f.get("shard")) for f in self.findings])


def _finding(kind, shard, detail):
    return {"kind": kind, "shard": shard, "detail": detail}


def _check_shard(spec, shard, m, native_digest):
    out = []
    rows, meta, sid = shard["rows"], shard["meta"], spec["id"]
    rows_d, meta_d = M.digest(rows), M.digest(meta)
    consistent = None
    if native_digest is not None and "rows_sha256" in meta:
        consistent = native_digest(rows) == meta["rows_sha256"]
        if not consistent:
            out.append(_finding(ALTERED, sid, "rows no longer match the rows_sha256 recorded in the shard's own meta"))
    if rows_d != spec["rows_sha256"]:
        if consistent is not False:
            out.append(_finding(SUBSTITUTED if consistent else ALTERED, sid,
                                "rows sha256 %s != frozen %s%s" % (rows_d[:12], spec["rows_sha256"][:12],
                                                                   "" if consistent else " (no internal-consistency evidence)")))
    elif meta_d != spec["meta_sha256"]:
        out.append(_finding(ALTERED, sid, "a meta field differs from the frozen meta (meta sha256 %s != %s)" % (meta_d[:12], spec["meta_sha256"][:12])))
    seeds, sf = set(spec["seeds"]), m["seed_field"]
    stray = sorted({r.get(sf) for r in rows if r.get(sf) not in seeds}, key=str)
    if stray:
        out.append(_finding(SEED_PARTITION, sid, "%d seed(s) outside this shard's assignment, e.g. %s" % (len(stray), stray[:3])))
    got = Counter(M.row_key(r, m["row_key_fields"]) for r in rows)
    if len(rows) != spec["rows"] or dict(got) != {k: v for k, v in spec["arm_counts"].items() if v}:
        out.append(_finding(COUNT_MISMATCH, sid, "rows %d != expected %d; per-key counts differ: %s" % (
            len(rows), spec["rows"], sorted(k for k in set(got) | set(spec["arm_counts"]) if got.get(k, 0) != spec["arm_counts"].get(k, 0))[:6])))
    return out


def _trigger(trigger, rows):
    n = sum(1 for r in rows if all(r.get(k) == v for k, v in trigger["where"].items()))
    return n, n >= trigger["at_least"]


def verify(manifest, presented, sources=None, native_digest=None, pinned_manifest_sha256=None):
    m = manifest
    if not M.is_sealed(m):
        return Result(REFUSED, [], [_finding(MANIFEST_ALTERED, None, "manifest_sha256 does not match the manifest's content")])
    if pinned_manifest_sha256 is not None and m["manifest_sha256"] != pinned_manifest_sha256:
        return Result(REFUSED, [], [_finding(MANIFEST_ALTERED, None, "sealed manifest %s is not the pinned %s" % (
            m["manifest_sha256"][:12], pinned_manifest_sha256[:12]))], manifest_sha256=m["manifest_sha256"])
    specs = {s["id"]: s for s in m["shards"]}
    findings, missing, trusted = [], [], []
    by_id = {}
    for sh in presented:
        by_id.setdefault(sh["id"], []).append(sh)
    for sid, group in sorted(by_id.items()):
        if sid not in specs:
            findings.append(_finding(UNEXPECTED, sid, "shard id is not in the manifest (expected %s)" % sorted(specs)))
            continue
        distinct = {}
        for sh in group:
            distinct.setdefault(M.digest([sh["rows"], sh["meta"]]), sh)
        if len(group) > 1:
            findings.append(_finding(CONFLICTING if len(distinct) > 1 else DUPLICATE, sid, "%d copies presented, %d distinct" % (len(group), len(distinct))))
        bad = False
        for sh in distinct.values():
            f = _check_shard(specs[sid], sh, m, native_digest)
            findings += f
            bad = bad or bool(f)
        if len(group) == 1 and not bad:
            trusted.append(group[0])
    missing = [sid for sid in specs if sid not in by_id]
    for path, want in sorted(m["sources"].items()):
        if sources is None or path not in sources:
            missing.append("source:" + path)
        elif sources[path] != want:
            findings.append(_finding(SOURCE_MISMATCH, None, "%s sha256 %s != frozen %s" % (path, sources[path][:12], want[:12])))
    early = None
    es = m.get("early_stop")
    if es:
        observed, met = _trigger(es["trigger"], [r for sh in trusted for r in sh["rows"]])
        skipped = [s for s in missing if s in es["skippable"]] if met else []     # excused only when the trigger is observed
        early = dict(rule_id=es["rule_id"], preregistered_in=es["preregistered_in"], skippable=es["skippable"], skipped=skipped,
                     observed=observed, at_least=es["trigger"]["at_least"], trigger_met=met)
        if skipped and not findings:
            missing = [s for s in missing if s not in skipped]
    if findings:
        return Result(REFUSED, missing, findings, early, m["manifest_sha256"])
    if missing:
        return Result(INCOMPLETE, missing, [], early, m["manifest_sha256"])
    return Result(COMPLETE_EARLY_STOP if early and early["skipped"] else COMPLETE, [], [], early, m["manifest_sha256"])
