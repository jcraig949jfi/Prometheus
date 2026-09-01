"""Apprentice model job (charter §8). Cheap/local models only. NEVER escalates to premium.

For each APPRENTICE-TESTING packet (max 2): ask each cheap model for a mechanism hypothesis,
a minimal implementation, and its own counterexamples. Execute the implementation in a
subprocess against the wall harness. Record everything under mint_queue/<ID>/attempts/.
Explanations are stored, never trusted; only executed behaviour updates the packet.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hephaestus.src import packet as P  # noqa: E402

# Cheap models available on this station (verified 2026-09-01 via prometheus_llm health).
# Premium targets (claude_cli, anthropic) are deliberately absent. Charter §3.
APPRENTICE_MODELS: list[tuple[str, int]] = [
    ("nvidia:nvidia/nemotron-3-super-120b-a12b", 180),   # NIM free tier, ~1-20 s
    ("ollama:phi3", 900),                               # local, GTX 1070, ~1-10 min
]
FORBIDDEN_TARGET_PREFIXES = ("claude", "anthropic", "openai:gpt-5", "openai:o")
MAX_PACKETS_PER_RUN = 2


def _assert_cheap(target: str) -> None:
    if target.lower().startswith(FORBIDDEN_TARGET_PREFIXES):
        raise RuntimeError(f"charter §3: premium target refused in apprentice job: {target}")


def build_prompt(p: dict, wall) -> str:
    ex = wall.build_examples()
    train, _ = wall.split(ex)
    iface = p["DESIRED_TYPED_INTERFACE"]
    shown = "\n".join(f"- [{e['kind']}] PROMPT: {e['prompt']}\n  CORRECT: {e['correct'] if e['gold'] != 'und' else 'ABSTAIN (leave comparison None)'}"
                      for e in train)
    prior = "\n".join(f"- {a.get('model')}: {a.get('verdict')} {a.get('failure_families', '')}" for a in p["CHEAP_MODEL_ATTEMPTS"][-6:]) or "- none yet"
    return f"""You are writing ONE small, deterministic Python function for a typed reasoning blackboard.

WALL: {p['FAILURE_FAMILY']}
WHAT SHOULD HAPPEN: {p['WHAT_SHOULD_HAVE_HAPPENED']}

INTERFACE (must match exactly):
    def op_vacuous_truth(state):
        # reads:  state.problem_text  (str)
        # writes: state.comparison    (True = claim true, False = claim false, None = abstain)
        # never read or modify state.candidates
        return state
Allowed imports: {', '.join(iface['allowed_imports'])}. Pure Python, no I/O, no network, < 1 s.

FORBIDDEN SHORTCUTS (each is tested and will fail you):
{chr(10).join('- ' + s for s in p['FORBIDDEN_SHORTCUTS'])}
Known shortcut scores on the hidden dev set (so you know they do NOT work): {json.dumps({c['shortcut']: c['accuracy_decidable'] for c in p['COUNTERFEIT_TESTS']})}

TRAINING EXAMPLES (a hidden set of ~80 more, with varied wording and order, will be executed):
{shown}

PREVIOUS CHEAP-MODEL ATTEMPTS ON THIS WALL (do not repeat their failure families):
{prior}

Respond in exactly this format. THE CODE BLOCK COMES FIRST. Do not think out loud before it; keep
everything outside the code block under 250 words in total.
```python
<the complete code, defining op_vacuous_truth; include every import you use>
```
HYPOTHESIS: <one paragraph: what computation decides the truth value, and what it must extract from the text>
SUBSTRATE_SUFFICES: <YES or NO, one sentence: could the existing primitives (modus_ponens, negate, solve_constraints, check_transitivity, ...) already express this?>
COUNTEREXAMPLES: <three prompts, one per line, on which you expect YOUR OWN code above to fail>"""


def extract_code(text: str) -> str | None:
    m = re.search(r"```python\s*(.*?)```", text, re.S | re.I)
    if not m:
        m = re.search(r"```\s*((?:import|from|def op_).*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    # unfenced fallback: take from the first import/def to the next field label or end
    m = re.search(r"((?:^|\n)(?:import [a-z_]+|from [a-z_]+ import [^\n]+|def op_[a-z_]+\(.*?)(?=\n[A-Z_]{5,}:|\Z))", text, re.S)
    return m.group(1).strip() if m else None


def extract_field(text: str, name: str) -> str:
    m = re.search(rf"{name}:\s*(.*?)(?=\n[A-Z_]+:|\n```|$)", text, re.S)
    return m.group(1).strip()[:1200] if m else ""


def run_attempt(p: dict, wall, target: str, timeout: int) -> dict:
    _assert_cheap(target)
    from prometheus_llm import complete  # local import: keys.py shim must be present
    mint = p["MINT_ID"]
    adir = P.packet_dir(mint) / "attempts"
    adir.mkdir(parents=True, exist_ok=True)
    n = len([f for f in adir.glob("*.json") if not f.name.endswith("_result.json")]) + 1
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    base = adir / f"{n:04d}_{stamp}_{re.sub(r'[^A-Za-z0-9]+', '-', target)[:40]}"
    prompt = build_prompt(p, wall)
    rec: dict = {"n": n, "ts": P.now_iso(), "model": target, "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:12],
                 "regime": "apprentice", "cost": 0.0}
    t0 = time.time()
    # 6000: reasoning models (nemotron) spend content tokens planning before the fence; 1800 produced NO_CODE.
    r = complete(prompt, target=target, max_tokens=6000, temperature=0.2, timeout=timeout, retries=1)
    rec["latency_s"] = round(time.time() - t0, 1)
    rec["model_served"] = r.model_served or r.model
    rec["llm_ok"] = bool(r.ok)
    if not r.ok:
        rec["verdict"] = "NO_RESPONSE"
        rec["llm_summary"] = r.summary() if hasattr(r, "summary") else str(r)
        base.with_suffix(".json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
        return rec
    (base.with_suffix(".txt")).write_text(r.text, encoding="utf-8")
    rec["hypothesis"] = extract_field(r.text, "HYPOTHESIS")
    rec["substrate_suffices_claim"] = extract_field(r.text, "SUBSTRATE_SUFFICES")
    rec["self_counterexamples"] = extract_field(r.text, "COUNTEREXAMPLES")
    code = extract_code(r.text)
    if not code:
        rec["verdict"] = "NO_CODE"
        base.with_suffix(".json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
        return rec
    cand = base.with_suffix(".py")
    cand.write_text(code, encoding="utf-8")
    out = base.with_name(base.name + "_result.json")
    try:
        subprocess.run([sys.executable, "-m", "hephaestus.src.run_candidate", wall.WALL_ID, str(cand), str(out)],
                       cwd=str(ROOT), timeout=120, capture_output=True, text=True, check=False,
                       env={**__import__("os").environ, "PYTHONPATH": str(ROOT)})
        res = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {"verdict": "RUNNER_NO_OUTPUT"}
    except subprocess.TimeoutExpired:
        res = {"verdict": "TIMEOUT"}
    rec["verdict"] = res.get("verdict")
    rec["failure_families"] = res.get("failure_families", [])
    rec["static_gate"] = res.get("static_gate", [])
    rec["holdout"] = res.get("holdout")
    rec["train"] = res.get("train")
    rec["input_mutants"] = res.get("input_mutants")
    rec["candidate_file"] = str(cand.relative_to(ROOT))
    rec["result_file"] = str(out.relative_to(ROOT)) if out.exists() else None
    base.with_suffix(".json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec


def summarize(rec: dict) -> dict:
    h = rec.get("holdout") or {}
    return {"n": rec["n"], "ts": rec["ts"], "model": rec["model"], "verdict": rec.get("verdict"),
            "holdout_acc": h.get("accuracy_decidable"), "boundary_false_commit": h.get("boundary_false_commit_rate"),
            "failure_families": rec.get("failure_families", []), "latency_s": rec.get("latency_s"),
            "file": rec.get("candidate_file")}


# ── Parser-widening mode (Addendum 1 §11: "parser widening with cheap models"). ────────────────
# Applies to packets that carry a candidate of record and are marked as a REPRESENTATION problem.
# The cheap model is shown the candidate and the phrasings on which it abstained, and asked to widen
# the ADAPTER only (the kernel is frozen). Measured on dev v2 + the adversarial set. This is
# representation work, labelled as such; it is never reported as a mint.

def build_widen_prompt(p: dict, cand_src: str, failing: list[dict]) -> str:
    rows = "\n".join(f"- gold {r['gold']}: {r['prompt']}" for r in failing[:16])
    return f"""You are widening the PARSER of an existing, working Python function. Do NOT change the
function `quantified_truth` (the kernel). Only extend how the text is read: emptiness idioms, claim
framings, cardinality phrasings. Keep the domain-equality rule (a premise counts only if its noun
phrase equals the claim's domain). If you cannot parse a sentence, ABSTAIN (leave comparison None);
never guess.

CURRENT CODE:
```python
{cand_src}
```

PHRASINGS ON WHICH IT CURRENTLY ABSTAINS (gold answer shown):
{rows}

Return ONLY the complete revised code in one ```python block, defining op_vacuous_truth and keeping
quantified_truth byte-identical."""


def run_widen_attempt(p: dict, wall, target: str, timeout: int) -> dict:
    _assert_cheap(target)
    import os
    from prometheus_llm import complete
    mint = p["MINT_ID"]
    cand_path = ROOT / p["_meta"]["candidate_of_record"]
    adv_path = ROOT / p["_meta"]["adversarial_script"]
    adir = P.packet_dir(mint) / "widen_attempts"; adir.mkdir(parents=True, exist_ok=True)
    n = len([f for f in adir.glob("*.json") if not f.name.endswith("_result.json")]) + 1
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    base = adir / f"{n:04d}_{stamp}_{re.sub(r'[^A-Za-z0-9]+', '-', target)[:40]}"
    prev = json.loads((ROOT / p["_meta"]["adversarial_result"]).read_text(encoding="utf-8"))
    failing = [{"prompt": r.get("prompt", ""), "gold": r["gold"]} for r in prev["records"] if not r["ok"]]
    if not failing or not failing[0]["prompt"]:
        # adversarial records store ids only; recover prompts from the script's literal ADV list
        # (a list of tuples of string literals — evaluated with ast.literal_eval, never exec).
        import ast
        src = adv_path.read_text(encoding="utf-8")
        adv_literal = src.split("ADV = ", 1)[1].split("\nrecs = []", 1)[0]
        byid = {i: (pr, g) for i, pr, g, _ in ast.literal_eval(adv_literal)}
        failing = [{"prompt": byid[r["id"]][0], "gold": byid[r["id"]][1]} for r in prev["records"] if not r["ok"] and r["id"] in byid]
    prompt = build_widen_prompt(p, cand_path.read_text(encoding="utf-8"), failing)
    rec = {"n": n, "ts": P.now_iso(), "model": target, "regime": "apprentice-widen", "cost": 0.0, "kind": "REPRESENTATION (not a mint)"}
    t0 = time.time()
    r = complete(prompt, target=target, max_tokens=8000, temperature=0.2, timeout=timeout, retries=1)
    rec["latency_s"] = round(time.time() - t0, 1); rec["llm_ok"] = bool(r.ok)
    if not r.ok:
        rec["verdict"] = "NO_RESPONSE"; base.with_suffix(".json").write_text(json.dumps(rec, indent=2)); return rec
    base.with_suffix(".txt").write_text(r.text, encoding="utf-8")
    code = extract_code(r.text)
    if not code or "def quantified_truth" not in code:
        rec["verdict"] = "NO_CODE" if not code else "KERNEL_MISSING"; base.with_suffix(".json").write_text(json.dumps(rec, indent=2)); return rec
    cand = base.with_suffix(".py"); cand.write_text(code, encoding="utf-8")
    out = base.with_name(base.name + "_result.json"); advout = base.with_name(base.name + "_adv.json")
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    subprocess.run([sys.executable, "-m", "hephaestus.src.run_candidate", wall.WALL_ID, str(cand), str(out)], cwd=str(ROOT), timeout=180, capture_output=True, env=env, check=False)
    subprocess.run([sys.executable, str(adv_path), str(cand), str(advout)], cwd=str(ROOT), timeout=180, capture_output=True, env=env, check=False)
    res = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {"verdict": "RUNNER_NO_OUTPUT"}
    adv = json.loads(advout.read_text(encoding="utf-8")) if advout.exists() else {}
    rec.update({"verdict": res.get("verdict"), "holdout": res.get("holdout"), "failure_families": res.get("failure_families", []),
                "adversarial": {"ok": adv.get("ok"), "n": adv.get("n")}, "candidate_file": str(cand.relative_to(ROOT))})
    base.with_suffix(".json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec


def widen(models: list[tuple[str, int]]) -> None:
    import importlib
    todo = [p for p in P.iter_packets() if p.get("_meta", {}).get("routing") == "representation"
            and p.get("_meta", {}).get("candidate_of_record")][:MAX_PACKETS_PER_RUN]
    for p in todo:
        wall = importlib.import_module("hephaestus.src.wall_vacuous_truth")
        for target, timeout in models:
            try:
                rec = run_widen_attempt(p, wall, target, timeout)
            except Exception as e:  # noqa: BLE001
                rec = {"ts": P.now_iso(), "model": target, "verdict": "JOB_ERROR", "error": f"{type(e).__name__}: {str(e)[:200]}"}
            p = P.load(p["MINT_ID"])
            p["_meta"].setdefault("widen_attempts", []).append({k: rec.get(k) for k in ("n", "ts", "model", "verdict", "adversarial", "candidate_file", "error")})
            P.log_event(p["MINT_ID"], "widen_attempt", **{k: rec.get(k) for k in ("n", "model", "verdict", "adversarial")})
            P.save(p)
            print(p["MINT_ID"], "widen", target, "->", rec.get("verdict"), rec.get("adversarial"))


def main(models: list[tuple[str, int]] | None = None) -> None:
    import importlib
    models = models or APPRENTICE_MODELS
    todo = [p for p in P.iter_packets() if p["STATUS"] == "APPRENTICE-TESTING"][:MAX_PACKETS_PER_RUN]
    if not todo:
        print("apprentice: nothing in APPRENTICE-TESTING")
        widen(models)
        return
    for p in todo:
        wall_id = "vacuous_truth" if p["MINT_ID"] == "MINT-0001" else None
        if not wall_id:
            print(p["MINT_ID"], "no wall module; skipping"); continue
        wall = importlib.import_module(f"hephaestus.src.wall_{wall_id}")
        for target, timeout in models:
            try:
                rec = run_attempt(p, wall, target, timeout)
            except Exception as e:  # noqa: BLE001
                rec = {"n": len(p["CHEAP_MODEL_ATTEMPTS"]) + 1, "ts": P.now_iso(), "model": target,
                       "verdict": "JOB_ERROR", "error": f"{type(e).__name__}: {str(e)[:200]}"}
            p = P.load(p["MINT_ID"])  # re-read: avoid clobbering concurrent refinement
            p["CHEAP_MODEL_ATTEMPTS"].append(summarize(rec))
            P.log_event(p["MINT_ID"], "apprentice_attempt", **summarize(rec))
            P.save(p)
            print(p["MINT_ID"], target, "->", rec.get("verdict"), (rec.get("holdout") or {}).get("accuracy_decidable"), rec.get("failure_families"))


if __name__ == "__main__":
    main()
