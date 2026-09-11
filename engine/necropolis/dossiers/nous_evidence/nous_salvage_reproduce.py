"""Q5: Does the prior salvage certificate (CONSUMPTION.jsonl 2026-08-20
SALVAGE-NOUS, commit fbd94b997) reproduce, and does the second execution
channel (agora.intelligence_outputs census captured by the Keeper) hold any
Nous rows?

(a) Runs techne/registry/build_concepts_index.main() with its OUT redirected to
a scratch file (never writes into techne/), then compares the produced rows to
the committed techne/registry/concepts_index.jsonl and to an independent census
of agents/nous/src/concepts.py.
(b) Reads engine/necropolis/dossiers/_keeper_evidence/intelligence_outputs_census_result.json
and reports the nous block verbatim (cited, not re-queried; no DB access).
Output: nous_salvage_reproduce_result.json next to this file.
"""
import importlib.util, json, os, pathlib, sys, tempfile, collections, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *([".."] * 4)))
OUT = {}
# (a) reproduce the salvage build into scratch
spec = importlib.util.spec_from_file_location("build_concepts_index", os.path.join(ROOT, "techne", "registry", "build_concepts_index.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
scratch = pathlib.Path(tempfile.mkdtemp(prefix="nous_salvage_")) / "concepts_index.jsonl"
mod.OUT = scratch
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = mod.main()
fresh = [json.loads(l) for l in scratch.read_text(encoding="utf-8").splitlines() if l.strip()]
committed_path = os.path.join(ROOT, "techne", "registry", "concepts_index.jsonl")
committed = [json.loads(l) for l in open(committed_path, encoding="utf-8") if l.strip()]
sys.path.insert(0, os.path.join(ROOT, "agents", "nous", "src"))
import concepts  # noqa: E402
indep = {"n_concepts": len(concepts.CONCEPTS), "n_fields": len({c["field"] for c in concepts.CONCEPTS}),
         "n_mechanisms_in_dict": len({c["mechanism"] for c in concepts.CONCEPTS}),
         "n_MECHANISM_TYPES": len(concepts.MECHANISM_TYPES),
         "mechanism_counts": dict(collections.Counter(c["mechanism"] for c in concepts.CONCEPTS))}
OUT["salvage_reproduction"] = {
    "build_script": "techne/registry/build_concepts_index.py", "return_code": rc, "stdout": buf.getvalue().strip(),
    "scratch_out": str(scratch), "wrote_into_techne": False,
    "fresh_rows": len(fresh), "committed_rows": len(committed),
    "fresh_equals_committed_rowwise": fresh == committed,
    "fresh_fields": len({r["field"] for r in fresh}), "fresh_mechanisms": len({r["mechanism"] for r in fresh}),
    "independent_census_of_concepts_py": indep,
    "certificate_claim_95_20_4": (len(fresh) == 95 and len({r["field"] for r in fresh}) == 20 and len({r["mechanism"] for r in fresh}) == 4),
    "docstring_says_18_fields": "18-field" in open(os.path.join(ROOT, "techne", "registry", "build_concepts_index.py"), encoding="utf-8").read(),
}
# (b) keeper census (cited)
kp = os.path.join(ROOT, "engine", "necropolis", "dossiers", "_keeper_evidence", "intelligence_outputs_census_result.json")
k = json.load(open(kp, encoding="utf-8"))
OUT["keeper_intelligence_outputs_census"] = {"path": os.path.relpath(kp, ROOT).replace(os.sep, "/"), "table": k.get("table"),
                                             "total_rows": k.get("total_rows"), "nous_block": k["graves"].get("nous"),
                                             "pollux_rows": k["graves"]["pollux"]["rows"], "erebos_rows": k["graves"]["erebos"]["rows"]}
# does nous.py ever write to intelligence_outputs / agora at all, and since when?
src = open(os.path.join(ROOT, "agents", "nous", "src", "nous.py"), encoding="utf-8").read()
OUT["nous_agora_surface"] = {"mentions_intelligence_outputs": "intelligence_outputs" in src,
                             "mentions_agora": "agora" in src.lower(), "mentions_heartbeat": "heartbeat" in src.lower()}
json.dump(OUT, open(os.path.join(HERE, "nous_salvage_reproduce_result.json"), "w"), indent=1)
print(json.dumps(OUT, indent=1))
