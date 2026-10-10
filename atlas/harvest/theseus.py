"""Source adapter: Theseus (concept tensor / synthetic ancestry ecology).

Sources on a git ref:
    theseus/runs/<dir>/                 one directory per run or evaluation
    roles/Theseus/prereg/<dir>/PREREG.md one directory per preregistration
    roles/Theseus/BACKLOG_H0H5.md       THESEUS-NN rows with a depends-on column

Mapping (native ids only):
- every theseus/runs/<dir> is one experiment (native id = the directory
  name) with one attempt. A directory holding VERDICT.md is an evaluation
  (kind theseus.verdict); the others are ecology runs (kind theseus.run).
- the THESEUS-NN id is read from line 1 of VERDICT.md / PREREG.md (an id
  pattern in a heading; it never becomes a key, it is kept in extract).
- the prereg link is the `prereg roles/Theseus/prereg/<dir>/, <sha>` clause
  of VERDICT.md line 1: definition source + prereg_digest. A prereg
  directory no verdict cites becomes an experiment of kind theseus.prereg.
- an evaluation EVALUATES a run when it holds J_<run>.jsonl / KO_<run>.jsonl
  or its `Runs:` block names an existing run directory (directory names
  matched against the known set, nothing minted).
- the verdict word is the first `VERDICT...:` / `Verdict by the frozen
  rule:` line, kept verbatim. Class: SUPPORTED -> POSITIVE, NOT SUPPORTED ->
  NEGATIVE, INDETERMINATE -> INCONCLUSIVE, VOID -> INVALID, REPLICATED ->
  POSITIVE; Theseus's own words (RANDOM-BEATS-RECURSION, DETECTOR BLIND, ...)
  stay UNKNOWN with the word kept.
- host: run directories record none. Theseus's seat runs on DESKTOP-RUAPVAI
  (infra/FLEET_HOSTS.md); attempts carry that as INFERRED, labelled.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

from atlas import db, gitsrc
from atlas.harvest import common as C

VERSION = "theseus/1"
ENGINE = "theseus"
PROGRAM = "theseus"
CAMPAIGN = "concept-tensor"
RUNS = "theseus/runs"
PREREG = "roles/Theseus/prereg"
BACKLOG = "roles/Theseus/BACKLOG_H0H5.md"
HOST = "DESKTOP-RUAPVAI"
HOST_BASIS = "INFERRED: Theseus seat host per infra/FLEET_HOSTS.md; run directories record no host"

TID = re.compile(r"\bTHESEUS-(\d+[a-z]?)\b")
PREREG_REF = re.compile(r"prereg\s+roles/Theseus/prereg/([^/\s,]+)/?(?:,\s*([0-9a-f]{7,40}))?")
VERDICT_LINE = re.compile(r"(?:\bVERDICT(?:\s+Part\s+\d+)?|\bVerdict by the frozen rule)\s*:\s*([^\n]+)")
_CLASS = [("NEGATIVE", r"^\s*(?:H-[A-Z0-9-]+\s+)?NOT SUPPORTED"), ("INVALID", r"^\s*VOID\b"),
          ("INCONCLUSIVE", r"^\s*(?:H-[A-Z0-9-]+\s+)?INDETERMINATE"),
          ("POSITIVE", r"^\s*(?:H-[A-Z0-9-]+\s+)?(?:SUPPORTED|REPLICATED)\b")]


def verdict_class(word: Optional[str]):
    if not word:
        return "UNKNOWN", "LOW"
    for name, pat in _CLASS:
        if re.search(pat, word):
            return name, "MEDIUM"
    return "UNKNOWN", "LOW"


def run(args) -> dict:
    ref = args.ref
    rfiles = {p: (s, z) for p, s, z in gitsrc.ls_tree(ref, RUNS)}
    pfiles = {p: (s, z) for p, s, z in gitsrc.ls_tree(ref, PREREG)}
    bfiles = {p: (s, z) for p, s, z in gitsrc.ls_tree(ref, BACKLOG)}
    files = {**rfiles, **pfiles, **bfiles}
    newest, oldest = {}, {}
    for root in (RUNS, PREREG, BACKLOG):
        n, o, _t = gitsrc.path_commits(ref, root)
        newest.update(n)
        oldest.update(o)
    b = C.Batch("theseus", VERSION, "Theseus")
    ck = C.campaign_key(PROGRAM, CAMPAIGN)
    b.campaign(campaign_key=ck, program=PROGRAM, native_id=CAMPAIGN, engine_id=ENGINE, driver_seat="Theseus",
               title="Theseus concept tensor / synthetic ancestry ecology (charter 2026-09-30)",
               extract={"grouping": "one campaign for the seat's whole run tree (theseus/runs has no campaign level)"})

    def src(path, obj=None, text=None):
        s, z = files[path]
        return b.git_source(ref, path, s, z, newest.get(path), oldest.get(path), obj=obj, text=text)

    rundirs: Dict[str, List[str]] = {}
    for p in rfiles:
        parts = p.split("/")
        if len(parts) >= 4:
            rundirs.setdefault(parts[2], []).append(p)
    predirs: Dict[str, List[str]] = {}
    for p in pfiles:
        parts = p.split("/")
        if len(parts) >= 5:
            predirs.setdefault(parts[3], []).append(p)
    cited_prereg: Set[str] = set()
    by_tid: Dict[str, List[str]] = {}

    with gitsrc.CatFile() as cat:
        # preregs first: id + digest of PREREG.md
        pre_tid: Dict[str, Optional[str]] = {}
        pre_uri: Dict[str, str] = {}
        for d, ps in predirs.items():
            pp = "{}/{}/PREREG.md".format(PREREG, d)
            if pp in pfiles:
                text = cat.text(pfiles[pp][0]) or ""
                m = TID.search(text.split("\n", 1)[0])
                pre_tid[d] = m.group(1) if m else None
                pre_uri[d] = src(pp, text=text)
        for d, ps in sorted(rundirs.items()):
            ek = C.experiment_key(ck, d)
            names = {p.rsplit("/", 1)[-1]: p for p in ps}
            verdict = None
            if "VERDICT.md" in names:
                verdict = cat.text(rfiles[names["VERDICT.md"]][0]) or ""
            date = re.search(r"(\d{4}-\d{2}-\d{2})$", d)
            ex = {"files": sorted(names)[:60]}
            exp = dict(experiment_key=ek, campaign_key=ck, engine_id=ENGINE, native_id=d, driver_seat="Theseus",
                       kind="theseus.verdict" if verdict is not None else "theseus.run",
                       atlas_class="UNKNOWN", atlas_class_confidence="LOW", validity_state="UNKNOWN",
                       atlas_class_method="theseus/1 verdict-word map (SUPPORTED/NOT SUPPORTED/INDETERMINATE/VOID)")
            ak = C.attempt_key(ek, "run")
            att = dict(attempt_key=ak, experiment_key=ek, native_id="run", attempt_no=1, of_record=True,
                       host_id=HOST, host_basis=HOST_BASIS, operator_seat="Theseus",
                       worktree_path="{}/{}".format(RUNS, d))
            for fname, role in (("CONFIG.json", "config"), ("SUMMARY.json", "summary"), ("RESULT.json", "result"),
                                ("CONTROLS_RUN.json", "controls"), ("CAL.json", "calibration"), ("REPORT.json", "report")):
                if fname not in names:
                    continue
                try:
                    obj = cat.json(rfiles[names[fname]][0])
                except Exception:
                    obj = None
                u = src(names[fname], obj=obj)
                b.link(u, "attempt", ak, role)
                if not isinstance(obj, dict):
                    continue
                layer = "RAN" if role in ("config",) else "OBSERVED"
                kind = "parameter" if role == "config" else ("control" if role == "controls" else "metric_summary")
                for k, v in C.flatten(obj, depth=2, limit=80):
                    b.fact(layer, kind, "attempt", ak, "theseus.{}.{}".format(role, k), v, u, k)
                if role == "config" and obj.get("master_seed") is not None:
                    exp["seeds"] = [str(obj["master_seed"])]
                if role == "report" and isinstance(obj.get("verdicts"), dict):
                    for h, v in obj["verdicts"].items():
                        b.fact("CONCLUDED", "detector_firing", "experiment", ek, "theseus.verdicts." + h, v, u,
                               "verdicts." + h)
            if verdict is not None:
                vu = src(names["VERDICT.md"], text=verdict)
                head = verdict.split("\n", 2)
                head1 = " ".join(head[:2]) if not head[0].rstrip().endswith(")") else head[0]
                m = TID.search(head[0])
                tid = m.group(1) if m else None
                pm = PREREG_REF.search(head1)
                exp.update(title=head[0].lstrip("# ").strip()[:300], result_summary=None)
                if tid:
                    ex["theseus_id"] = "THESEUS-" + tid
                    by_tid.setdefault(tid, []).append(ek)
                if pm:
                    cited_prereg.add(pm.group(1))
                    exp["prereg_digest"] = pm.group(2)
                    ex["prereg_dir"] = pm.group(1)
                    if pm.group(1) in pre_uri:
                        b.link(pre_uri[pm.group(1)], "experiment", ek, "prereg")
                b.link(vu, "experiment", ek, "verdict")
                vm = VERDICT_LINE.search(verdict)
                rows = _verdict_table(verdict)
                for i, (hyp, word, ln) in enumerate(rows):
                    b.fact("CONCLUDED", "detector_firing", "experiment", ek, "theseus.verdict_table." + hyp, word, vu,
                           "line {}".format(ln))
                if not vm and rows:
                    classes = {verdict_class(w)[0] for _h, w, _l in rows}
                    word = "; ".join("{}: {}".format(h, w) for h, w, _l in rows)
                    cls = classes.pop() if len(classes) == 1 else "UNKNOWN"
                    exp.update(reported_disposition=word[:300], atlas_class=cls, atlas_class_confidence="LOW")
                    b.conclusion("experiment", ek, word[:300], None, vu, "verdict table line {}".format(rows[0][2]))
                if vm:
                    word = vm.group(1).strip()
                    cls, conf = verdict_class(word)
                    exp.update(reported_disposition=word[:300], atlas_class=cls, atlas_class_confidence=conf)
                    if cls == "INVALID":
                        exp["validity_state"] = "INVALID_ATTEMPT"
                    b.conclusion("experiment", ek, word[:300], _para(verdict, vm.start()), vu,
                                 "line {}".format(verdict[:vm.start()].count("\n") + 1))
                # evaluated runs: J_/KO_ files, then directory names in the text
                used = {re.sub(r"^(?:J|KO)_|\.jsonl$", "", n) for n in names if re.match(r"(?:J|KO)_.+\.jsonl$", n)}
                used |= {r for r in rundirs if r != d and re.search(r"\b" + re.escape(r) + r"\b", verdict)}
                for r in sorted(used & set(rundirs)):
                    b.edge(("experiment", ek), ("experiment", C.experiment_key(ck, r)), "EVALUATES", "EXECUTION",
                           reason="DECLARED_PARENT", basis="DECLARED", confidence="HIGH",
                           detail="per-run file or run directory named in VERDICT.md", uri=vu)
            if date:
                exp["first_seen_at"] = date.group(1)
            exp["extract"] = ex
            b.experiment(**exp)
            b.attempt(**att)
        for d, tid in pre_tid.items():
            if d in cited_prereg:
                continue
            ek = C.experiment_key(ck, "prereg/" + d)
            b.experiment(experiment_key=ek, campaign_key=ck, engine_id=ENGINE, native_id="prereg/" + d,
                         kind="theseus.prereg", driver_seat="Theseus", atlas_class="PLANNED",
                         atlas_class_confidence="LOW", validity_state="UNKNOWN",
                         atlas_class_method="preregistration no VERDICT.md cites (may be running, superseded or pooled)",
                         extract={"theseus_id": "THESEUS-" + tid if tid else None})
            b.link(pre_uri[d], "experiment", ek, "prereg")
            if tid:
                by_tid.setdefault(tid, []).append(ek)
        # backlog depends-on: THESEUS-NN rows -> DEPENDS_ON between experiments carrying those ids
        if BACKLOG in bfiles:
            text = cat.text(bfiles[BACKLOG][0]) or ""
            bu = src(BACKLOG, text=text)
            for ln, line in enumerate(text.splitlines(), 1):
                m = re.match(r"THESEUS-(\d+[a-z]?)(?:-[A-Z]+)?\s*\|", line)
                if not m:
                    continue
                cols = [c.strip() for c in line.split("|")]
                deps = TID.findall(cols[5]) if len(cols) > 5 else []
                for src_ek in by_tid.get(m.group(1), []):
                    for dep in deps:
                        for dst_ek in by_tid.get(dep, []):
                            b.edge(("experiment", src_ek), ("experiment", dst_ek), "DEPENDS_ON", "SCIENTIFIC",
                                   reason="DECLARED_PARENT", basis="DECLARED", confidence="MEDIUM",
                                   detail="BACKLOG_H0H5 THESEUS-{} depends-on THESEUS-{}".format(m.group(1), dep),
                                   uri=bu, locator="line {}".format(ln))
    with db.harvest("theseus", VERSION, source_ref="{}:{},{}".format(ref, RUNS, PREREG)) as h:
        return b.flush(h)


def _verdict_table(text: str):
    """Rows of a markdown table whose header has a `verdict` column: (first cell, verdict cell, line no)."""
    out, col = [], None
    for ln, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            col = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        low = [c.lower() for c in cells]
        if "verdict" in low:
            col = low.index("verdict")
            continue
        if col is None or set(line.strip()) <= set("|-: ") or len(cells) <= col:
            continue
        hyp = re.sub(r"[^A-Za-z0-9_.+-]+", "_", cells[0])[:80] or "row{}".format(ln)
        if cells[col]:
            out.append((hyp, cells[col].strip("* "), ln))
    return out


def _para(text: str, start: int) -> str:
    end = text.find("\n\n", start)
    return C.trunc(text[start:end if end > 0 else None].strip(), 2000)
