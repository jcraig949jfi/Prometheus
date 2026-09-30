"""Run subject models on the frozen alien-lawful dataset.

    python -m hecate.alien.runner <model> <task> [--limit N]
    model: claude | gemini | gptoss      task: blind fam reveal active pair prose

Every call is recorded (raw text, parsed JSON, prompt sha256, attempts,
timestamps) to hecate/alien/runs/<model>/<task>.jsonl, flushed per row,
resumable (rows with ok=true are skipped). Transport failures (rate
limits, 5xx, timeouts) are retried with backoff; content is never retried,
except ONE form-only re-ask when the reply contains no parseable JSON.
Gemini and gpt-oss calls go through prometheus_llm (needs the canonical
checkout's keys module on PYTHONPATH; no credential is read here).
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from hecate.alien import tasks
from hecate.alien.dataset import OUT
from hecate.alien.rules import describe
from hecate.alien.systems import clamp_run, parse_state, show, trajectory
from hecate.llm import call as claude_call, extract_json, sha256

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.environ.get("HECATE_ALIEN_RUNS") or os.path.join(HERE, "runs")
MODELS = {"claude": "claude-opus-5-5", "gemini": "gemini:gemini-3.6-flash",
          "gptoss": "groq:openai/gpt-oss-120b"}
WORKERS = {"claude": 4, "gemini": 1, "gptoss": 1}
SUBSET_SEED = 20260930


def load():
    with open(os.path.join(OUT, "public.json"), encoding="utf-8") as fh:
        pub = {e["id"]: e for e in json.load(fh)}
    with open(os.path.join(OUT, "answer_key.json"), encoding="utf-8") as fh:
        key = json.load(fh)
    return pub, key


def subsets(key):
    """Deterministic task subsets (chosen by Hecate from the answer key;
    subjects never see the key). Standard aliens only for reveal/active."""
    rng = random.Random(SUBSET_SEED)
    by = {}
    for sid, e in sorted(key.items()):
        grp = ("K" if e["class"] == "KNOWN_LAWFUL" else
               "A" if e["class"] == "ALIEN_LAWFUL" and not e.get("adversarial") else
               "AADV" if e["class"] == "ALIEN_LAWFUL" else "N_" + e["null_type"])
        by.setdefault((grp, e["family"]), []).append(sid)
    for v in by.values():
        rng.shuffle(v)
    fams = ["tab", "graph", "rewrite", "vm", "map"]
    reveal = [s for f in fams for s in by.get(("K", f), [])[:2] + by.get(("A", f), [])[:3] +
              by.get(("N_DESTROY", f), [])[:1]]
    active = [s for f in fams for s in by.get(("A", f), [])[3:5]]          # 10 A
    active += [s for f in ["tab", "graph", "vm", "map", "rewrite"] for s in by.get(("K", f), [])[2:3]][:4]
    noise = [s for g in ("N_CONJ", "N_DSCRAMBLE", "N_SCRAMBLE", "N_SEDUCTIVE") for f in fams
             for s in by.get((g, f), [])]
    rng.shuffle(noise)
    active += noise[:6]
    prose = [s for f in fams for s in by.get(("K", f), [])[:2] + by.get(("A", f), [])[:2]] + noise[6:16]
    pairs = sorted([(sid, e["matched_to"]) for sid, e in key.items() if e["class"] == "ALIEN_LAWFUL"])
    return {"reveal": reveal, "active": active, "prose": prose, "pairs": pairs}


# ---- transport ----------------------------------------------------------------

def _api(model, prompt):
    from prometheus_llm import complete
    return complete(prompt, target=MODELS[model], system=tasks.SYSTEM,
                    max_tokens=16000, temperature=0.0, retries=1, timeout=300)


def ask(model, prompt):
    t0 = time.time()
    attempts = []
    for k in range(8):
        if model == "claude":
            r = claude_call(prompt, MODELS["claude"], tasks.SYSTEM, timeout=900)
            ok, text, err = r["ok"], r.get("text", ""), (r.get("stderr_head") or "")[:300]
        else:
            c = _api(model, prompt)
            ok, text, err = bool(c.ok), c.text or "", (c.error or "")[:300] if hasattr(c, "error") else ""
            if not ok:
                err = str(getattr(c, "summary", lambda: "")())[:300]
        attempts.append({"ok": ok, "err": err, "t": round(time.time() - t0, 1)})
        if ok:
            return text, attempts
        time.sleep(min(300, 15 * 2 ** k) * (0.5 + random.random()))
    return "", attempts


def ask_json(model, prompt):
    text, att = ask(model, prompt)
    obj = extract_json(text) if text else None
    reasked = False
    if text and obj is None:
        reasked = True
        text2, att2 = ask(model, prompt + "\n\nYour previous reply could not be parsed. "
                                          "Reply with exactly one JSON object and nothing else.")
        att += att2
        obj = extract_json(text2) if text2 else None
        text = text + "\n\n[REASK]\n" + text2
    return text, obj, att, reasked


# ---- tasks --------------------------------------------------------------------

def _row(model, task, sid, prompt, text, obj, att, reasked, **extra):
    return {"sid": sid, "task": task, "model": MODELS[model], "prompt_sha256": sha256(prompt),
            "raw": text, "parsed": obj, "ok": obj is not None, "attempts": att,
            "reasked": reasked, "utc": datetime.now(timezone.utc).isoformat(), **extra}


def do_single(model, task, sid, pub, key):
    p = pub[sid]
    if task == "blind":
        prompt = tasks.blind(p)
    elif task == "fam":
        prompt = tasks.familiarity(p)
    elif task == "reveal":
        prompt = tasks.reveal(p, describe(key[sid]["params"]))
    elif task == "prose":
        prompt = tasks.prose_t2(p)
    else:
        raise ValueError(task)
    return _row(model, task, sid, prompt, *ask_json(model, prompt))


def do_pair(model, pair, pub, key):
    a_id, n_id = pair
    rng = random.Random(f"{SUBSET_SEED}-{a_id}")
    first, second = (a_id, n_id) if rng.random() < 0.5 else (n_id, a_id)
    prompt = tasks.pair(pub[first], pub[second])
    return _row(model, "pair", a_id, prompt, *ask_json(model, prompt),
                order=[first, second], lawful=("A" if first == a_id else "B"))


def _fmt(p, states):
    return " -> ".join(show(p, s) for s in states)


def do_active(model, sid, pub, key, budget=10):
    p = key[sid]["params"]
    pb = pub[sid]
    runs = pb["observations"][:2]
    history, turns = [], []
    for used in range(budget):
        prompt = tasks.active_turn(pb, runs, history, budget - used)
        text, obj, att, reasked = ask_json(model, prompt)
        turns.append({"raw": text, "parsed": obj, "attempts": att})
        if not obj or obj.get("query") == "done":
            break
        try:
            start = parse_state(p, obj["start"])
            steps = max(1, min(6, int(obj.get("steps", 6))))
            if obj["query"] == "run":
                res = trajectory(p, start, steps)
            elif obj["query"] == "clamp":
                pos, val = int(obj["position"]), int(obj["value"])
                s0 = list(start)
                s0[pos] = val
                res = [tuple(s0)] + clamp_run(p, start, pos, val, steps)
            else:
                raise ValueError("unknown query")
            if len(res[0]) != len(start):
                raise ValueError("bad state")
            history.append({"query": obj, "result": _fmt(p, res)})
        except Exception as e:                          # malformed experiment: spent, recorded
            history.append({"query": obj, "result": f"invalid experiment ({type(e).__name__})"})
    prompt = tasks.active_final(pb, runs, history)
    row = _row(model, "active", sid, prompt, *ask_json(model, prompt))
    row.update(turns=turns, history=history, n_experiments=len(history))
    return row


def main(model, task, limit=None):
    pub, key = load()
    sub = subsets(key)
    os.makedirs(os.path.join(RUNS, model), exist_ok=True)
    path = os.path.join(RUNS, model, f"{task}.jsonl")
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            done = {json.loads(l)["sid"] for l in fh if l.strip() and json.loads(l)["ok"]}
    if task == "pair":
        items = [pr for pr in sub["pairs"] if pr[0] not in done]
        fn = lambda it: do_pair(model, it, pub, key)
    elif task == "active":
        items = [s for s in sub["active"] if s not in done]
        fn = lambda it: do_active(model, it, pub, key)
    else:
        ids = sorted(pub) if task in ("blind", "fam") else sub[task]
        items = [s for s in ids if s not in done]
        fn = lambda it: do_single(model, task, it, pub, key)
    if limit:
        items = items[:limit]
    with open(path, "a", encoding="utf-8", newline="\n") as fh, \
            ThreadPoolExecutor(max_workers=WORKERS[model]) as ex:
        for row in ex.map(fn, items):
            fh.write(json.dumps(row, ensure_ascii=True, default=str) + "\n")
            fh.flush()
    print(model, task, "wrote", len(items))


if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    main(sys.argv[1], sys.argv[2], lim)
