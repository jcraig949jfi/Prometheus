"""Checker for the Cosmos research workspace (roles/Cosmos/research/, directive 2026-09-28).

python -m prometheus.cosmos.research_check [research_dir]      exit 1 on any ERROR

THREADS.md    required keys, status/zone vocabularies, unique ids; thread_id = "thr-" + sha256(id_rule)[:12]
              (the ops/threads convention; id_rule = genesis|<commit>|<path>|<title>)
RESULTS.md    four layers present and non-empty (observation / law / domain / falsifier), never merged;
              baselines must report the zero-parameter definition rung (or say NOT MEASURED);
              a KILLED result must name its GRAVEYARD entry, which must exist
GRAVEYARD.md  required keys; killed_by beginning UNRECOVERED is counted, not an error
FREEZES.md    every file freeze RE-HASHED (comms.manifest convention); supersedes must name an earlier
              entry, which must be marked SUPERSEDED; git freezes checked against the local object
              store (absent -> UNVERIFIABLE_HERE, not an error)
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from comms.manifest import artifact_hash

THREAD_KEYS = ("thread_id", "id_rule", "status", "zone", "question", "instruments", "first_experiment",
               "kill_criterion", "depends_on")
THREAD_STATUS = {"OPEN", "DESIGNED", "REVIEWED", "FROZEN", "RUN", "SURVIVED_PROVISIONAL", "KILLED",
                 "INCONCLUSIVE", "PARKED", "SPAWNED", "BLOCKED"}
ZONES = {"Z1", "Z2", "Z3"}
RESULT_KEYS = ("status", "observation", "law", "domain", "falsifier", "baselines")
DEFINITION_RUNG = re.compile(r"definition rung", re.I)
RESULT_STATUS = {"PROVISIONAL", "SURVIVED_Z2", "SURVIVED_Z3", "RESTRICTED", "KILLED"}
GRAVE_KEYS = ("law", "campaign", "killed_by", "evidence", "fragments")
FREEZE_KEYS = ("kind", "target", "sha256", "supersedes", "review", "status")
FREEZE_STATUS = {"ACTIVE", "SUPERSEDED", "SPENT"}

HEAD = re.compile(r"^### (\S+) \|")
KV = re.compile(r"^- ([a-z0-9_]+): (.*)$")


def parse(path):
    """-> list of (id, {key: value}) in file order; duplicate keys inside an entry are an error."""
    entries, errors, cur = [], [], None
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        m = HEAD.match(line)
        if m:
            cur = (m.group(1), {})
            entries.append(cur)
            continue
        m = KV.match(line)
        if m and cur is not None:
            k, v = m.group(1), m.group(2).strip()
            if k in cur[1]:
                errors.append(f"{Path(path).name}:{n} {cur[0]} duplicate key {k}")
            cur[1][k] = v
        elif line.startswith("## "):
            cur = None
    return entries, errors


def _need(name, eid, d, keys, errors):
    for k in keys:
        if not d.get(k):
            errors.append(f"{name} {eid}: missing or empty '{k}'")


def _dupes(name, entries, errors):
    seen = set()
    for eid, _ in entries:
        if eid in seen:
            errors.append(f"{name}: duplicate id {eid}")
        seen.add(eid)


def check_threads(p, errors):
    entries, e = parse(p)
    errors += e
    _dupes("THREADS", entries, errors)
    for eid, d in entries:
        _need("THREADS", eid, d, THREAD_KEYS, errors)
        if d.get("status") and d["status"] not in THREAD_STATUS:
            errors.append(f"THREADS {eid}: status {d['status']!r} not in vocabulary")
        if d.get("zone") and d["zone"] not in ZONES:
            errors.append(f"THREADS {eid}: zone {d['zone']!r} not in Z1/Z2/Z3")
        rule, tid = d.get("id_rule", ""), d.get("thread_id", "")
        if rule and tid and "thr-" + hashlib.sha256(rule.encode()).hexdigest()[:12] != tid:
            errors.append(f"THREADS {eid}: thread_id {tid} does not re-derive from id_rule")
    ids = [d.get("thread_id") for _, d in entries if d.get("thread_id")]
    if len(ids) != len(set(ids)):
        errors.append("THREADS: duplicate thread_id")
    return entries


def check_graveyard(p, errors):
    entries, e = parse(p)
    errors += e
    _dupes("GRAVEYARD", entries, errors)
    for eid, d in entries:
        _need("GRAVEYARD", eid, d, GRAVE_KEYS, errors)
    unrec = [eid for eid, d in entries if d.get("killed_by", "").startswith("UNRECOVERED")]
    return entries, unrec


def check_results(p, grave_ids, errors):
    entries, e = parse(p)
    errors += e
    _dupes("RESULTS", entries, errors)
    for eid, d in entries:
        _need("RESULTS", eid, d, RESULT_KEYS, errors)
        if d.get("status") and d["status"] not in RESULT_STATUS:
            errors.append(f"RESULTS {eid}: status {d['status']!r} not in vocabulary")
        if d.get("baselines") and not DEFINITION_RUNG.search(d["baselines"]):
            errors.append(f"RESULTS {eid}: baselines must report the zero-parameter DEFINITION RUNG "
                          f"(or say 'definition rung NOT MEASURED')")
        layers = [d.get(k, "") for k in ("observation", "law", "domain", "falsifier")]
        if all(layers) and len(set(layers)) < 4:
            errors.append(f"RESULTS {eid}: two layers are identical (layers collapsed)")
        if d.get("status") == "KILLED":
            g = d.get("graveyard", "")
            if not g or g not in grave_ids:
                errors.append(f"RESULTS {eid}: KILLED but graveyard entry {g!r} not found")
    return entries


def _git_has(commit, repo):
    r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"],
                       capture_output=True)
    return r.returncode == 0


def check_freezes(p, repo, errors):
    entries, e = parse(p)
    errors += e
    _dupes("FREEZES", entries, errors)
    report, order = {}, [eid for eid, _ in entries]
    superseded_by = {}
    for i, (eid, d) in enumerate(entries):
        _need("FREEZES", eid, d, FREEZE_KEYS, errors)
        if d.get("status") and d["status"] not in FREEZE_STATUS:
            errors.append(f"FREEZES {eid}: status {d['status']!r} not in vocabulary")
        sup = d.get("supersedes", "-")
        if sup != "-":
            if sup not in order[:i]:
                errors.append(f"FREEZES {eid}: supersedes {sup!r}, which is not an EARLIER entry")
            superseded_by[sup] = eid
        kind, target = d.get("kind"), d.get("target", "")
        if kind == "file":
            f = Path(repo) / target
            if not f.is_file():
                errors.append(f"FREEZES {eid}: frozen file {target} is MISSING")
                report[eid] = "MISSING"
            elif artifact_hash(f) != d.get("sha256"):
                errors.append(f"FREEZES {eid}: {target} hash {artifact_hash(f)[:16]} != frozen "
                              f"{d.get('sha256', '')[:16]} (a frozen file was edited)")
                report[eid] = "MISMATCH"
            else:
                report[eid] = "VERIFIED"
        elif kind == "git":
            report[eid] = "VERIFIED" if _git_has(target, repo) else "UNVERIFIABLE_HERE"
        else:
            errors.append(f"FREEZES {eid}: kind {kind!r} not file/git")
    for old, new in superseded_by.items():
        st = dict(entries).get(old, {}).get("status")
        if st is not None and st != "SUPERSEDED":
            errors.append(f"FREEZES {old}: superseded by {new} but status is {st}")
    return report


def check(research_dir, repo=None):
    rd = Path(research_dir)
    repo = Path(repo) if repo else rd.resolve().parents[2]
    errors = []
    threads = check_threads(rd / "THREADS.md", errors)
    graves, unrec = check_graveyard(rd / "GRAVEYARD.md", errors)
    results = check_results(rd / "RESULTS.md", {g for g, _ in graves}, errors)
    freezes = check_freezes(rd / "FREEZES.md", repo, errors)
    summary = {"threads": len(threads), "results": len(results), "graves": len(graves),
               "graves_unrecovered": unrec, "freezes": freezes}
    return errors, summary


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    rd = argv[0] if argv else "roles/Cosmos/research"
    errors, s = check(rd)
    print(f"threads {s['threads']}  results {s['results']}  graves {s['graves']} "
          f"(killed_by UNRECOVERED: {len(s['graves_unrecovered'])} {s['graves_unrecovered']})")
    for fid, st in s["freezes"].items():
        print(f"freeze {fid}: {st}")
    for e in errors:
        print("ERROR", e)
    print("PASS" if not errors else f"FAIL ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
