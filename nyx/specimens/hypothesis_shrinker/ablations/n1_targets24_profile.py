"""NYX-38 (2026-09-12, in-lane under the HOLD ruling; attacks an existing claim, produces no inventory).
Question: is c19 (pass_to_descendant makes 0 calls on Proteus's solving_programs strategy) the
explanation of Techne's 24/45 non-minimal cases, or of 1/45? Method: for every target Techne scored
(fixture rows), reproduce the find() with the same settings Techne used (derandomize, max_examples 300)
with the shrink-pass profile on; record final size vs ground truth and, per target, which passes made
calls / shrank, and whether pass_to_descendant appears at all. Nothing is changed in Proteus or Techne.
Run with the isolated env from the repo root."""
from __future__ import annotations
import datetime as _dt, io, json, re, sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "techne" / "acquisition" / "checks"))
from hypothesis import Phase, find, settings, HealthCheck, Verbosity  # noqa: E402
from hypothesis.errors import NoSuchExample, Unsatisfiable  # noqa: E402
from hypothesis_program_minimiser import target_expr  # noqa: E402
from proteus.eval.hypothesis_strategy import solving_programs  # noqa: E402
from proteus.eval.shrink import size_key, canonical, minimal_by_enumeration, still_solves  # noqa: E402

fixture = json.loads((ROOT / "techne/acquisition/fixtures/hypothesis_program_minimiser.json").read_text(encoding="utf-8"))
rows = [r for r in fixture["rows"] if r.get("ground_truth")]
LINE = re.compile(r"\*\s+(\S+) made (\d+) calls? of which (\d+) shrank")
out = {"date": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "n_rows_with_ground_truth": len(rows), "targets": []}
for r in rows:
    f = r["target"]; tgt = target_expr(f)
    buf = io.StringIO(); rec = {"target": f}
    with redirect_stdout(buf), redirect_stderr(buf):
        try:
            prog = find(solving_programs(tgt), lambda p: still_solves(p, tgt),
                        settings=settings(database=None, deadline=None, suppress_health_check=list(HealthCheck),
                                          max_examples=300, derandomize=True, verbosity=Verbosity.debug,
                                          phases=[Phase.generate, Phase.shrink]))
            rec["found"] = canonical(prog); rec["size_key"] = list(size_key(prog))
        except (NoSuchExample, Unsatisfiable) as e:
            rec["found"] = None; rec["error"] = type(e).__name__
    gt = minimal_by_enumeration(tgt)
    rec["ground_truth"] = gt["canonical"] if gt else None
    rec["gt_size"] = gt["size"] if gt else None
    rec["excess_nodes"] = (rec["size_key"][0] - gt["size"]) if (gt and rec.get("size_key")) else None
    passes = {m.group(1): (int(m.group(2)), int(m.group(3))) for m in LINE.finditer(buf.getvalue())}
    rec["passes_calls_shrinks"] = passes
    rec["pass_to_descendant_calls"] = passes.get("pass_to_descendant", (0, 0))[0]
    rec["techne_excess"] = r.get("excess_nodes")
    out["targets"].append(rec)
nm = [t for t in out["targets"] if t.get("excess_nodes") not in (None, 0)]
out["summary"] = {
    "scored": sum(1 for t in out["targets"] if t.get("size_key")),
    "not_minimal_here": len(nm),
    "not_minimal_with_pass_to_descendant_zero_calls": sum(1 for t in nm if t["pass_to_descendant_calls"] == 0),
    "not_minimal_with_pass_to_descendant_some_calls": sum(1 for t in nm if t["pass_to_descendant_calls"] > 0),
    "minimal_here": sum(1 for t in out["targets"] if t.get("excess_nodes") == 0),
    "pass_to_descendant_zero_calls_over_all_scored": sum(1 for t in out["targets"] if t.get("size_key") and t["pass_to_descendant_calls"] == 0),
    "agreement_with_techne_excess": sum(1 for t in out["targets"] if t.get("excess_nodes") is not None and t.get("techne_excess") is not None and t["excess_nodes"] == t["techne_excess"]),
    "passes_that_shrank_anything_counts": {},
}
for t in out["targets"]:
    for p, (c, s) in t["passes_calls_shrinks"].items():
        if s:
            out["summary"]["passes_that_shrank_anything_counts"][p] = out["summary"]["passes_that_shrank_anything_counts"].get(p, 0) + 1
(HERE / "RECEIPT_N1_targets24_2026-09-12.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
print(json.dumps(out["summary"], indent=1))
