"""Cross-pollination REPLAY with 2026-09 models over the extracted 1.0 packets.

Nothing under agents/ is written. All output goes to hephaestus/xpol_2026/runs/<run>/.

Stages (per packet x arm):
  O       deterministic: re-score the ORIGINAL code (if any) on the honest 186-trap ruler
          (no LLM; the March-era tools were only ever certified on 15 traps)
  N       Nous replay: the era-matched Nous prompt (reconstructed verbatim) -> new model
          -> Nous scorer (ratings / composite / novelty label)
  C_new   code-gen replay: the era-matched CODE_GEN template (+ the frame suffix the
          original forge drew) filled with the arm's OWN stage-N analysis -> code
  C_orig  code-gen replay with the ORIGINAL 2026-03 Nous analysis held constant ->
          isolates the code-generation step from the analysis step
Every generated tool goes through the 1.0 post-processing byte-for-byte (extract_code,
_sanitize_unicode, _inject_missing_imports, _fix_common_errors, validate) and is then
scored on the honest ruler in a child process with a timeout. Read every number against
floors.json (position-majority decoy 0.4032 > NCD 0.3925 > random 0.325).

Arms:
  fable51    claude -p --model claude-fable-5-1 (subscription CLI, tools off). Deviation
             from the 1.0 protocol: this is an agent harness, not a raw API (the raw
             Anthropic key is unfunded, 2026-09-19); temperature not settable.
  gpt6astra  openrouter:openai/gpt-6-astra -- BLOCKED 402 (no credits) on 2026-09-19;
             the arm is defined so it runs unchanged once funded.
  gemini     gemini-3.6-flash (free, live) -- 2026-09 cheap-model contrast
  groq       openai/gpt-oss-120b on groq (free, live) -- 2026-09 cheap-model contrast

Usage (from the worktree root, PYTHONPATH must include the worktree root and D:/Prometheus
for keys.py -- never read that file):
  python hephaestus/xpol_2026/replay.py --run pilot --arms fable51 --stages O N C_new C_orig --ids XP-001 XP-002
  python hephaestus/xpol_2026/replay.py --run pilot --score <file.py>      (internal)
"""
from __future__ import annotations
import argparse, collections, hashlib, json, os, re, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEGACY = ROOT / "agents/hephaestus/src"
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(LEGACY)); sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agents/nous/src"))

ARMS = {
    "fable51": {"kind": "claude_cli", "model": "claude-fable-5-1"},
    "gpt6astra": {"kind": "llm", "target": "openrouter:openai/gpt-6-astra"},
    "gemini": {"kind": "llm", "target": "gemini:gemini-3.6-flash"},
    "groq": {"kind": "llm", "target": "groq:openai/gpt-oss-120b"},
    "qwen14b": {"kind": "llm", "target": "ollama:qwen2.5-coder:14b"},   # local 14B, free: the size-controlled arm
}
NOUS_TEMP, NOUS_MAX = 0.7, 2048      # agents/nous/src/nous.py:329-330
CODE_TEMP, CODE_MAX = 0.4, 4096      # agents/hephaestus/src/hephaestus.py:234-235
SCORE_TIMEOUT = 300


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- model calls
def call_claude_cli(prompt: str, model: str, system: str, timeout: int = 900) -> dict:
    t0 = time.time()
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--no-session-persistence",
           "--tools", "", "--system-prompt", system, prompt]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timeout {timeout}s", "seconds": round(time.time() - t0, 1)}
    try:
        d = json.loads(p.stdout)
    except Exception:
        return {"ok": False, "error": f"non-json stdout rc={p.returncode}: {p.stdout[:300]} {p.stderr[:300]}", "seconds": round(time.time() - t0, 1)}
    u = d.get("usage", {})
    return {"ok": (not d.get("is_error")) and bool(d.get("result")), "text": d.get("result", ""), "seconds": round(time.time() - t0, 1),
            "served": next(iter(d.get("modelUsage", {}).keys()), model), "usage": {"in": u.get("input_tokens"), "cache_read": u.get("cache_read_input_tokens"),
            "cache_create": u.get("cache_creation_input_tokens"), "out": u.get("output_tokens"), "thinking": (u.get("output_tokens_details") or {}).get("thinking_tokens")},
            "list_cost_usd": d.get("total_cost_usd"), "error": None if not d.get("is_error") else d.get("result", "")[:300]}


LLM_BUDGET_MULT = 4   # hosted 2026 models spend the 1.0 token budget on thinking (gemini pilot: code cut at 2.5 kB
                      # under 4096); the budget is an instrument parameter, not the experiment, so llm arms get 4x.


def call_llm(prompt: str, target: str, system: str, temperature: float, max_tokens: int) -> dict:
    from prometheus_llm import complete
    t0 = time.time(); attempts = []
    for i, backoff in enumerate((0, 20, 45, 90)):
        if backoff:
            time.sleep(backoff)
        c = complete(prompt, target=target, system=system, temperature=temperature, max_tokens=max_tokens * LLM_BUDGET_MULT, retries=1, timeout=300)
        attempts.append({"status": getattr(c, "status", None), "ok": bool(c.ok), "finish_reason": getattr(c, "finish_reason", None)})
        if c.ok or getattr(c, "status", None) not in (429, 503, 502, 500):
            break
    out = {"ok": bool(c.ok), "text": c.text or "", "seconds": round(time.time() - t0, 1), "served": c.model_served or c.model or target,
           "finish_reason": c.finish_reason, "attempts": attempts, "max_tokens": max_tokens * LLM_BUDGET_MULT,
           "usage": {"in": c.prompt_tokens, "out": c.completion_tokens, "empty_content": c.empty_content}}
    if not c.ok:
        out["error"] = c.summary()[:400]
    return out


def call(arm: str, prompt: str, system: str, temperature: float, max_tokens: int) -> dict:
    a = ARMS[arm]
    if a["kind"] == "claude_cli":
        r = call_claude_cli(prompt, a["model"], system)
        r["temperature"] = "not settable (CLI)"
        return r
    r = call_llm(prompt, a["target"], system, temperature, max_tokens)
    r["temperature"] = temperature
    return r


# ---------------------------------------------------------------- scoring child
def score_file(path: str) -> dict:
    """Child process: load a tool file, run the honest ruler, print JSON."""
    import collections as _c
    from trap_generator_extended import generate_full_battery
    from test_harness import _run_battery, load_tool_from_file, CATEGORY_TIER
    b = generate_full_battery(n_per_category=2, seed=42)
    tool = load_tool_from_file(path)
    r = _run_battery(tool, b)
    tiers = _c.defaultdict(lambda: [0, 0])
    cats = _c.defaultdict(lambda: [0, 0])
    picks = []
    for res, trap in zip(r["trap_results"], b):
        k = CATEGORY_TIER.get(trap["category"], "?"); tiers[k][1] += 1; tiers[k][0] += int(res["is_correct"])
        cats[trap["category"]][1] += 1; cats[trap["category"]][0] += int(res["is_correct"])
        picks.append(str(res.get("top_candidate")))
    idx_of_pick = [trap["candidates"].index(p) if p in trap["candidates"] else -1 for p, trap in zip(picks, b)]
    # agreement with the two published counterfeits: does it merely echo NCD, or the position-majority decoy?
    from test_harness import _NCDBaseline
    ncd_picks = [str(x.get("top_candidate")) for x in _run_battery(_NCDBaseline(), b)["trap_results"]]
    maj_picks = [trap["candidates"][min(1, len(trap["candidates"]) - 1)] for trap in b]
    agree_ncd = sum(p == q for p, q in zip(picks, ncd_picks)) / len(b)
    agree_maj = sum(p == q for p, q in zip(picks, maj_picks)) / len(b)
    return {"accuracy": round(r["accuracy"], 4), "calibration": round(r["calibration"], 4), "n_traps": r["n_traps"],
            "agreement_with_ncd_picks": round(agree_ncd, 4), "agreement_with_position_majority": round(agree_maj, 4),
            "evaluate_errors": sum("evaluate_error" in x for x in r["trap_results"]),
            "by_tier": {k: {"correct": v[0], "n": v[1], "acc": round(v[0] / v[1], 4)} for k, v in sorted(tiers.items())},
            "by_category": {k: v[0] for k, v in sorted(cats.items())},
            "pick_index_hist": dict(sorted(_c.Counter(idx_of_pick).items())),
            "answer_vector_sha256": sha("|".join(picks))}


def score_in_child(path: Path) -> dict:
    env = dict(os.environ); env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(LEGACY), env.get("PYTHONPATH", "")])
    try:
        p = subprocess.run([sys.executable, str(Path(__file__)), "--score", str(path)], capture_output=True, text=True,
                           timeout=SCORE_TIMEOUT, encoding="utf-8", errors="replace", env=env, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return {"error": f"score_timeout {SCORE_TIMEOUT}s"}
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return {"error": f"score_child rc={p.returncode}: {p.stderr[-600:]}"}


def source_ncd_vs_forge(code: str) -> dict:
    """Same arithmetic as hephaestus._compute_novelty, read-only over agents/hephaestus/forge."""
    import zlib
    cb = code.encode("utf-8"); cn = len(zlib.compress(cb)); best = (1.0, None); tot = 0.0; n = 0
    for f in (ROOT / "agents/hephaestus/forge").glob("*.py"):
        ob = f.read_bytes(); co = len(zlib.compress(ob)); cboth = len(zlib.compress(cb + ob))
        ncd = (cboth - min(cn, co)) / max(cn, co); tot += ncd; n += 1
        if ncd < best[0]:
            best = (ncd, f.name)
    return {"min_ncd": round(best[0], 4), "nearest": best[1], "mean_ncd": round(tot / n, 4) if n else None, "library_size": n}


# ---------------------------------------------------------------- prompts
_ncd15 = None


def ncd15() -> tuple[int, int]:
    """The 1.0 prompt quoted the NCD baseline on the STATIC 15 traps (prompts._get_ncd_baseline_scores)."""
    global _ncd15
    if _ncd15 is None:
        from test_harness import run_ncd_baseline
        r = run_ncd_baseline(); _ncd15 = (int(r["accuracy"] * 100), int(r["calibration"] * 100))
    return _ncd15


def codegen_prompt(pk: dict, analysis: str, ratings: dict) -> tuple[str, dict]:
    L = pk["ledger"] or {}
    era = L.get("codegen_template") or "codegen_v3"     # never-forged packets use the final template
    tpl = (HERE / "templates" / f"{era}.txt").read_text(encoding="utf-8")
    names = pk["concept_names"]
    fields = {"concept_1": names[0], "concept_2": names[1], "concept_3": names[2], "nous_response_text": analysis,
              "r": ratings.get("reasoning", "?"), "m": ratings.get("metacognition", "?"), "h": ratings.get("hypothesis_generation", "?")}
    if era != "codegen_v1":
        a, c = ncd15(); fields.update({"coeus_section": "", "ncd_accuracy": a, "ncd_calibration": c})
    prompt = tpl.format(**fields)
    frame = L.get("frame")
    if frame and frame != "A" and (HERE / "templates" / f"frame_{frame}.txt").exists():
        prompt += (HERE / "templates" / f"frame_{frame}.txt").read_text(encoding="utf-8")
    return prompt, {"codegen_template": era, "frame": frame or "A", "coeus_section": "omitted (not replayed)"}


def postprocess(raw: str) -> tuple[str | None, str, dict]:
    from code_extractor import extract_code
    from validator import validate
    import legacy_helpers as L
    code, status = extract_code(raw)
    if code is None:
        return None, status, {}
    code = L._fix_common_errors(L._inject_missing_imports(L._sanitize_unicode(code)))
    ok, reason = validate(code)
    return code, ("ok" if ok else f"validation:{reason}"), {"lines": code.count("\n") + 1, "code_sha256": sha(code)}


# ---------------------------------------------------------------- run loop
def load_done(results: Path) -> set:
    if not results.exists():
        return set()
    return {(json.loads(l)["packet_id"], json.loads(l)["arm"], json.loads(l)["stage"]) for l in open(results, encoding="utf-8") if l.strip()}


def emit(results: Path, rec: dict) -> None:
    with open(results, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n"); f.flush(); os.fsync(f.fileno())


def stage_O(pk: dict, rundir: Path) -> dict:
    oc = pk.get("original_code")
    if not oc:
        return {"skipped": "no original code file"}
    p = ROOT / oc["path"]
    if sha(p.read_text(encoding="utf-8", errors="replace")) != oc["sha256"] and hashlib.sha256(p.read_bytes()).hexdigest() != oc["sha256"]:
        return {"error": "original code sha mismatch vs packet"}
    return {"path": oc["path"], "score": score_in_child(p)}


def stage_N(pk: dict, arm: str, calldir: Path) -> dict:
    from scorer import score_response
    prompt = pk["nous"]["prompt_reconstructed"]
    r = call(arm, prompt, "You are a computational engineer designing reasoning evaluation tools." if pk["nous"]["template"] == "nous_v2"
             else "You are a computational theorist exploring novel intersections of ideas.", NOUS_TEMP, NOUS_MAX)
    rec = {"prompt_sha256": pk["nous"]["prompt_sha256"], "call": {k: v for k, v in r.items() if k != "text"}}
    (calldir / "N.txt").write_text(r.get("text", ""), encoding="utf-8")
    if r.get("ok"):
        s = score_response(r["text"])
        rec.update({"ratings": s.get("ratings"), "composite_score": s.get("composite_score"), "novelty_label": s.get("novelty"),
                    "is_unproductive": s.get("is_unproductive"), "response_chars": len(r["text"]), "response_sha256": sha(r["text"])})
    return rec


def stage_C(pk: dict, arm: str, calldir: Path, analysis: str, ratings: dict, tag: str) -> dict:
    prompt, meta = codegen_prompt(pk, analysis, ratings)
    r = call(arm, prompt, "You are a computational engineer building reasoning tools.", CODE_TEMP, CODE_MAX)
    rec = {"prompt_sha256": sha(prompt), "prompt_chars": len(prompt), **meta, "analysis_sha256": sha(analysis), "call": {k: v for k, v in r.items() if k != "text"}}
    (calldir / f"{tag}.raw.txt").write_text(r.get("text", ""), encoding="utf-8")
    if not r.get("ok"):
        rec["outcome"] = "api_call_failed"; return rec
    code, status, info = postprocess(r["text"])
    rec["postprocess"] = status; rec.update(info)
    if code is None:
        rec["outcome"] = f"scrap:{status}"; return rec
    cp = calldir / f"{tag}.tool.py"; cp.write_text(code, encoding="utf-8")
    rec["tool_path"] = str(cp.relative_to(HERE))
    if status != "ok":
        rec["outcome"] = f"scrap:{status}"; return rec
    rec["score"] = score_in_child(cp)
    rec["source_ncd_vs_forge_1p0"] = source_ncd_vs_forge(code)
    rec["outcome"] = "scored" if "error" not in rec["score"] else f"scrap:{rec['score']['error'][:80]}"
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="pilot"); ap.add_argument("--arms", nargs="*", default=["fable51"])
    ap.add_argument("--stages", nargs="*", default=["O", "N", "C_new", "C_orig"]); ap.add_argument("--ids", nargs="*")
    ap.add_argument("--limit", type=int); ap.add_argument("--score")
    ap.add_argument("--shard", help="i/n: take packets whose index mod n == i (parallel workers, one run dir each)")
    ap.add_argument("--print-prompt", choices=["N", "C_orig"], help="print the exact prompt for the single --ids packet and exit")
    ap.add_argument("--ingest-raw", help="SESSION ARM: a file holding a model response produced outside this runner (e.g. the "
                    "interactive Fable session); it is post-processed and scored exactly like a live call and recorded under --arms[0] "
                    "for the single --ids packet at --ingest-stage. The record carries call.kind='session' and a contamination note.")
    ap.add_argument("--ingest-stage", default="C_orig", choices=["C_new", "C_orig"])
    ap.add_argument("--ingest-note", default="")
    a = ap.parse_args()
    if a.score:
        print(json.dumps(score_file(a.score))); return
    if a.print_prompt or a.ingest_raw:
        sel = json.loads((HERE / "packets/selection.json").read_text(encoding="utf-8"))
        pk = next(p for p in sel["packets"] if p["packet_id"] == a.ids[0])
        if a.print_prompt == "N":
            print(pk["nous"]["prompt_reconstructed"]); return
        prompt, meta = codegen_prompt(pk, pk["nous"]["response_text"], pk["nous"]["ratings"])
        if a.print_prompt:
            print(prompt); print("\n[meta]", json.dumps(meta), "sha256", sha(prompt)); return
        arm = a.arms[0]; rundir = HERE / "runs" / a.run; rundir.mkdir(parents=True, exist_ok=True)
        results = rundir / "results.jsonl"; calldir = rundir / "calls" / pk["packet_id"] / arm; calldir.mkdir(parents=True, exist_ok=True)
        raw = Path(a.ingest_raw).read_text(encoding="utf-8")
        tag = a.ingest_stage
        (calldir / f"{tag}.raw.txt").write_text(raw, encoding="utf-8")
        rec = {"packet_id": pk["packet_id"], "arm": arm, "stage": tag, "ts": now(), "prompt_sha256": sha(prompt), "prompt_chars": len(prompt), **meta,
               "analysis_sha256": sha(pk["nous"]["response_text"]),
               "call": {"kind": "session", "ok": True, "seconds": None, "served": "claude-fable-5-1 (interactive Claude Code session, not claude -p)",
                        "note": a.ingest_note or "author had seen floors.json, tier profiles and category names before writing; battery source not opened"}}
        code, status, info = postprocess(raw)
        rec["postprocess"] = status; rec.update(info)
        if code is None:
            rec["outcome"] = f"scrap:{status}"
        else:
            cp = calldir / f"{tag}.tool.py"; cp.write_text(code, encoding="utf-8"); rec["tool_path"] = str(cp.relative_to(HERE))
            if status != "ok":
                rec["outcome"] = f"scrap:{status}"
            else:
                rec["score"] = score_in_child(cp); rec["source_ncd_vs_forge_1p0"] = source_ncd_vs_forge(code)
                rec["outcome"] = "scored" if "error" not in rec["score"] else f"scrap:{rec['score']['error'][:80]}"
        emit(results, rec)
        s = rec.get("score") or {}
        print(json.dumps({k: rec.get(k) for k in ("packet_id", "arm", "stage", "outcome", "postprocess", "lines")}),
              "acc", s.get("accuracy"), "cal", s.get("calibration"), "by_tier", {k: v["acc"] for k, v in (s.get("by_tier") or {}).items()},
              "agree_ncd", s.get("agreement_with_ncd_picks"), "agree_maj", s.get("agreement_with_position_majority"), "eval_errors", s.get("evaluate_errors"))
        return
    sel = json.loads((HERE / "packets/selection.json").read_text(encoding="utf-8"))
    packets = sel["packets"]
    if a.ids:
        packets = [p for p in packets if p["packet_id"] in set(a.ids)]
    if a.shard:
        i, n = (int(x) for x in a.shard.split("/")); packets = [p for j, p in enumerate(packets) if j % n == i]
    if a.limit:
        packets = packets[: a.limit]
    rundir = HERE / "runs" / a.run; rundir.mkdir(parents=True, exist_ok=True)
    results = rundir / "results.jsonl"; done = load_done(results)
    ws = {"worktree": str(ROOT), "host": os.environ.get("COMPUTERNAME"), "started": now(),
          "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()}
    (rundir / "RUN.json").write_text(json.dumps({**ws, "arms": a.arms, "stages": a.stages, "n_packets": len(packets),
                                                 "selection_sha256": hashlib.sha256((HERE / "packets/selection.json").read_bytes()).hexdigest()}, indent=1), encoding="utf-8")
    for pk in packets:
        pid = pk["packet_id"]
        if "O" in a.stages and (pid, "-", "O") not in done:
            rec = {"packet_id": pid, "arm": "-", "stage": "O", "ts": now(), **stage_O(pk, rundir)}
            emit(results, rec); done.add((pid, "-", "O"))
            print(pid, "O", (rec.get("score") or {}).get("accuracy", rec.get("skipped", rec.get("error"))), flush=True)
        for arm in a.arms:
            calldir = rundir / "calls" / pid / arm; calldir.mkdir(parents=True, exist_ok=True)
            n_rec = None
            if "N" in a.stages:
                if (pid, arm, "N") in done:
                    n_rec = next((json.loads(l) for l in open(results, encoding="utf-8") if json.loads(l)["packet_id"] == pid and json.loads(l)["arm"] == arm and json.loads(l)["stage"] == "N"), None)
                else:
                    n_rec = {"packet_id": pid, "arm": arm, "stage": "N", "ts": now(), **stage_N(pk, arm, calldir)}
                    emit(results, n_rec); done.add((pid, arm, "N"))
                    print(pid, arm, "N", n_rec.get("composite_score"), n_rec.get("novelty_label"), n_rec["call"].get("seconds"), "s", flush=True)
            if "C_new" in a.stages and (pid, arm, "C_new") not in done:
                if n_rec and n_rec.get("ratings") is not None and (calldir / "N.txt").exists():
                    rec = {"packet_id": pid, "arm": arm, "stage": "C_new", "ts": now(),
                           **stage_C(pk, arm, calldir, (calldir / "N.txt").read_text(encoding="utf-8"), n_rec["ratings"], "C_new")}
                else:
                    rec = {"packet_id": pid, "arm": arm, "stage": "C_new", "ts": now(), "outcome": "skipped:no_stage_N_analysis"}
                emit(results, rec); done.add((pid, arm, "C_new"))
                print(pid, arm, "C_new", rec.get("outcome"), (rec.get("score") or {}).get("accuracy"), flush=True)
            if "C_orig" in a.stages and (pid, arm, "C_orig") not in done:
                rec = {"packet_id": pid, "arm": arm, "stage": "C_orig", "ts": now(),
                       **stage_C(pk, arm, calldir, pk["nous"]["response_text"], pk["nous"]["ratings"], "C_orig")}
                emit(results, rec); done.add((pid, arm, "C_orig"))
                print(pid, arm, "C_orig", rec.get("outcome"), (rec.get("score") or {}).get("accuracy"), flush=True)
    (rundir / "DONE.json").write_text(json.dumps({"finished": now(), "records": len(load_done(results))}), encoding="utf-8")


if __name__ == "__main__":
    main()
