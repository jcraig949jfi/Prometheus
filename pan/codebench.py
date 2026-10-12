"""PAN-33: local code benchmark on HumanEval+ (evalplus/humanevalplus), protocol frozen in
pan/tests/codebench_prereg.json. Model generation goes through pan.modelbench.generate
(Ollama); every verdict is an executed test suite, never a model's opinion.

python -m pan codebench controls          canonical / stub / prompt-only controls (CPU only)
python -m pan codebench run MODEL [--think --budget N]
"""
import datetime as dt
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from . import PKG, host, lake

PREREG = PKG / "tests" / "codebench_prereg.json"
SUFFIX = ("\n\nComplete the function above. Reply with ONLY one Python code block (```python ... ```) containing "
          "the complete function, including the signature. No explanation, no tests.")


def problems():
    import pyarrow.parquet as pq
    spec = json.loads(PREREG.read_text(encoding="utf-8"))["dataset"]
    path = lake() / "datasets" / "humanevalplus" / spec["file"]
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != spec["sha256"]:
        raise SystemExit("dataset sha256 {} != prereg {}".format(got, spec["sha256"]))
    excluded = {t for a in json.loads(PREREG.read_text(encoding="utf-8")).get("amendments", [])
                for t in a.get("excluded_tasks", [])}
    return [p for p in pq.read_table(str(path)).to_pylist() if p["task_id"] not in excluded]


def imports_of(prompt):
    return "\n".join(ln for ln in prompt.splitlines() if ln.startswith(("import ", "from ")))


def extract(response):
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", response or "", re.S)
    return m[-1] if m else (response or "")


def execute(p, code, timeout=60):
    """(passed, detail) for one problem and one candidate code string."""
    prog = "{}\n\n{}\n\n{}\n\ncheck({})\nprint('CB_PASS_SENTINEL')\n".format(imports_of(p["prompt"]), code, p["test"],
                                                                          p["entry_point"])
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "cand.py")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(prog)
        try:
            r = subprocess.run([sys.executable, "-I", f], cwd=d, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "timeout"
    ok = r.returncode == 0 and "CB_PASS_SENTINEL" in r.stdout
    return ok, "" if ok else ((r.stderr.strip().splitlines() or ["rc={}".format(r.returncode)])[-1])[:200]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(c - h, 3), round(c + h, 3))


def controls(out=print, workers=4):
    probs = problems()
    res = {}
    for name, make in (("POSITIVE_canonical", lambda p: p["prompt"] + p["canonical_solution"]),
                       ("CHEAT_stub", lambda p: re.sub(r'(\n\s*""".*?"""|\n\s*\'\'\'.*?\'\'\')\s*$', r"\1\n    pass\n",
                                                       p["prompt"].rstrip() + "\n", flags=re.S)
                        if '"""' in p["prompt"] or "'''" in p["prompt"] else p["prompt"] + "\n    pass\n"),
                       ("NEGATIVE_prompt_only", lambda p: p["prompt"])):
        t = time.time()
        with ThreadPoolExecutor(workers) as ex:
            oks = list(ex.map(lambda p: execute(p, make(p))[0], probs))
        res[name] = dict(passed=sum(oks), of=len(oks), seconds=round(time.time() - t, 1))
        out("{:<22} {}/{} ({}s)".format(name, sum(oks), len(oks), res[name]["seconds"]))
    res["verdict"] = dict(positive_all_pass=res["POSITIVE_canonical"]["passed"] == len(probs),
                          cheat_le_5=res["CHEAT_stub"]["passed"] <= 5,
                          negative_le_5=res["NEGATIVE_prompt_only"]["passed"] <= 5)
    p = PKG.parent / "roles" / "Pan" / "reports" / "codebench"
    p.mkdir(parents=True, exist_ok=True)
    (p / "CONTROLS_{}.json".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))).write_text(
        json.dumps(res, indent=1), encoding="utf-8")
    out(json.dumps(res["verdict"]))
    return res


def run(model, think=False, budget=1024, out=print, workers=3):
    from psycopg2.extras import execute_values
    from . import db
    from .modelbench import HF_MAP, generate, ollama_version, strip_thinking
    probs = problems()
    cfg = "@{}{}".format("think" if think else "nothink", budget)
    run_id = "codebench-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor() as cur:
        cur.execute("insert into pan.run (run_id, kind, host, params) values (%s,'codebench',%s,%s)",
                    (run_id, host(), json.dumps({"model": model, "think": think, "budget": budget, "n": len(probs),
                                                 "ollama": ollama_version()})))
    t0 = time.time()
    gens = []
    for i, p in enumerate(probs):            # generation is sequential (one GPU)
        t = time.time()
        try:
            g = generate(model, p["prompt"] + SUFFIX, think=think, budget=budget)
            text = strip_thinking(g.get("response", ""))
            ev, evd = g.get("eval_count") or 0, (g.get("eval_duration") or 0) / 1e9
            gens.append((p, text, ev, ev / evd if evd else None, time.time() - t, None))
        except Exception as e:
            gens.append((p, "", 0, None, time.time() - t, "{}: {}".format(type(e).__name__, e)[:200]))
        if (i + 1) % 41 == 0:
            out("  {} {}/{} generated, {:.0f}s".format(model, i + 1, len(probs), time.time() - t0))
    with ThreadPoolExecutor(workers) as ex:     # tests run in parallel on CPU
        verdicts = list(ex.map(lambda g: execute(g[0], extract(g[1])) if not g[5] else (False, g[5]), gens))
    rows = []
    for (p, text, ev, tps, lat, err), (ok, detail) in zip(gens, verdicts):
        if ev >= budget:
            detail = "TRUNCATED at {} tokens; {}".format(ev, detail)
        rows.append((run_id, "ollama:" + model + cfg, HF_MAP.get(model), p["task_id"], ok, detail, lat, ev, tps,
                     text[:12000]))
    with db.cursor() as cur:
        execute_values(cur, """insert into pan.code_bench (run_id, model, hf_repo, task_id, ok, detail, latency_s,
                               eval_tokens, tok_per_s, response) values %s""", rows)
        k = sum(1 for r in rows if r[4])
        tps = sorted(r[8] for r in rows if r[8])
        summ = dict(model=model, config=cfg, passed=k, of=len(rows), pass_at_1=round(k / len(rows), 3),
                    wilson95=wilson(k, len(rows)), truncated=sum(1 for r in rows if (r[5] or "").startswith("TRUNCATED")),
                    median_tok_s=round(tps[len(tps) // 2], 1) if tps else None, seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status='OK', counts=%s where run_id=%s",
                    (json.dumps(summ), run_id))
    subprocess.run(["ollama", "stop", model], capture_output=True, timeout=60)
    out(json.dumps(summ))
    return summ
