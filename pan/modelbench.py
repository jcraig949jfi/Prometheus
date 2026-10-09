"""PAN-19: smoke-test locally runnable models with deterministic checks.

Runtime: the host's Ollama server (HTTP, localhost:11434), temperature 0, fixed seed,
thinking disabled where the runtime supports it. Checks:
  code  extract the ```python block, run it in a fresh `python -I` subprocess with
        HIDDEN test inputs (not shown in the prompt), 10 s timeout
  math  the LAST integer in the response must equal the exact answer
  json  the first {...} object must parse and carry the requested fields/values
No model judges another. Results: pan.model_bench (+ JSON report).

This is a smoke test (15 probes), not a benchmark: it answers "does this model
load on this card, how fast does it generate, and does it follow basic
instructions", which is what the intake's 16 GB fit estimate cannot answer.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import time

from . import host

OLLAMA = os.environ.get("OLLAMA_HOST_URL", "http://127.0.0.1:11434")
HF_MAP = {  # Ollama library tag -> Hugging Face repo (for joining pan.hf_model); best known mapping
    "qwen3:4b": "Qwen/Qwen3-4B", "qwen3:8b": "Qwen/Qwen3-8B", "qwen3:14b": "Qwen/Qwen3-14B",
    "deepseek-r1:8b": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "phi4-mini": "microsoft/Phi-4-mini-instruct",
    "gpt-oss:20b": "openai/gpt-oss-20b", "gemma3:12b": "google/gemma-3-12b-it",
    "granite3.3:8b": "ibm-granite/granite-3.3-8b-instruct", "qwen2.5-coder:14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
    "qwen2.5-coder:7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
}

CODE_SUFFIX = ("\nReply with ONLY one Python code block (```python ... ```) defining the function. "
               "No explanation, no tests, no input().")
PROBES = [
    dict(id="code_is_prime", kind="code", prompt="Write a Python function is_prime(n) that returns True if the integer n is prime and False otherwise (n may be negative, 0 or 1)." + CODE_SUFFIX,
         tests="assert [n for n in range(-3, 60) if is_prime(n)] == [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59]\nassert is_prime(7919) and not is_prime(7917)"),
    dict(id="code_rle", kind="code", prompt="Write a Python function rle(s) that run-length encodes a string: each maximal run of a character c of length k becomes c followed by k. Example: rle('aab') == 'a2b1'." + CODE_SUFFIX,
         tests="assert rle('') == ''\nassert rle('zzzzyx') == 'z4y1x1'\nassert rle('abba') == 'a1b2a1'"),
    dict(id="code_flatten", kind="code", prompt="Write a Python function flatten(xs) that takes an arbitrarily nested list of integers and returns a flat list of the integers in order." + CODE_SUFFIX,
         tests="assert flatten([]) == []\nassert flatten([1,[2,[3,[4]],5],[[6]]]) == [1,2,3,4,5,6]\nassert flatten([[[]],7]) == [7]"),
    dict(id="code_reverse_words", kind="code", prompt="Write a Python function reverse_words(s) that reverses the order of the words in s (words are separated by single spaces) and returns the new string." + CODE_SUFFIX,
         tests="assert reverse_words('alpha beta gamma') == 'gamma beta alpha'\nassert reverse_words('x') == 'x'"),
    dict(id="code_fib", kind="code", prompt="Write a Python function fib(n) returning the n-th Fibonacci number with fib(0)=0 and fib(1)=1, efficient enough for n up to 10000." + CODE_SUFFIX,
         tests="assert [fib(i) for i in range(10)] == [0,1,1,2,3,5,8,13,21,34]\nassert fib(90) == 2880067194370816120\nassert len(str(fib(10000))) == 2090"),
    dict(id="code_balanced", kind="code", prompt="Write a Python function balanced(s) that returns True if every bracket in s among ()[]{} is properly matched and nested, ignoring all other characters." + CODE_SUFFIX,
         tests="assert balanced('') and balanced('a(b[c]{d}e)f')\nassert not balanced('(]') and not balanced('((') and not balanced('}{')"),
    dict(id="math_arith", kind="math", prompt="Compute 17*23 + 4*19 - 6. Give only the final integer on the last line.", answer=461),
    dict(id="math_train", kind="math", prompt="A train travels at 72 km/h for 2 hours and 45 minutes. How many kilometres does it travel? Give only the final integer on the last line.", answer=198),
    dict(id="math_primes", kind="math", prompt="How many prime numbers are there between 1 and 100 inclusive? Give only the final integer on the last line.", answer=25),
    dict(id="math_gcd", kind="math", prompt="What is the greatest common divisor of 1071 and 462? Give only the final integer on the last line.", answer=21),
    # answer corrected 49 -> 45 on 2026-10-09: x=4, y=5 (the first key was wrong; every model "failed";
    # tests/test_modelbench.py now derives every math key independently)
    dict(id="math_system", kind="math", prompt="If 3x + 2y = 22 and x - y = -1, what is 10x + y? Give only the final integer on the last line.", answer=45),
    dict(id="math_combin", kind="math", prompt="How many ways are there to choose 4 items from 10 distinct items (order does not matter)? Give only the final integer on the last line.", answer=210),
    dict(id="json_basic", kind="json", prompt='Return ONLY a JSON object with exactly these keys: "name" set to the string "Pan", "count" set to the integer 3, and "tags" set to a list of the strings "a" and "b".',
         want={"name": "Pan", "count": 3, "tags": ["a", "b"]}),
    dict(id="json_nested", kind="json", prompt='Return ONLY a JSON object with key "seat" whose value is an object with keys "id" (integer 7) and "active" (boolean false).',
         want={"seat": {"id": 7, "active": False}}),
    dict(id="json_extract", kind="json", prompt='From the sentence "The run used 12 workers for 340 seconds on host M2", return ONLY a JSON object with integer keys "workers" and "seconds" and string key "host".',
         want={"workers": 12, "seconds": 340, "host": "M2"}),
]

THINK = re.compile(r"<think>.*?</think>", re.S)


def strip_thinking(text):
    return THINK.sub("", text or "").strip()


def check_code(response, tests, timeout=10):
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", response, re.S)
    code = m[-1] if m else response
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "probe.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(code + "\n\n" + tests + "\nprint('PROBE_OK')\n")
        try:
            r = subprocess.run([sys.executable, "-I", p], cwd=d, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "timeout"
    ok = r.returncode == 0 and "PROBE_OK" in r.stdout
    return ok, "" if ok else (r.stderr.strip().splitlines() or ["rc={}".format(r.returncode)])[-1][:200]


def check_math(response, answer):
    nums = re.findall(r"-?\d[\d,]*", response.replace(" ", ""))
    if not nums:
        return False, "no integer"
    got = int(nums[-1].replace(",", ""))
    return got == answer, "last integer {}".format(got)


def check_json(response, want):
    m = re.search(r"\{.*\}", response, re.S)
    if not m:
        return False, "no object"
    try:
        obj = json.loads(m.group(0))
    except ValueError as e:
        return False, "invalid json: {}".format(e)[:120]
    return obj == want, "" if obj == want else "got {}".format(json.dumps(obj))[:160]


def check(probe, response):
    if probe["kind"] == "code":
        return check_code(response, probe["tests"])
    if probe["kind"] == "math":
        return check_math(response, probe["answer"])
    return check_json(response, probe["want"])


def generate(model, prompt, timeout=900, think=False, budget=1024):
    import requests
    body = dict(model=model, prompt=prompt, stream=False, think=think,
                options=dict(temperature=0, seed=1, num_ctx=max(4096, budget + 1024), num_predict=budget))
    r = requests.post(OLLAMA + "/api/generate", json=body, timeout=timeout)
    if r.status_code == 400 and "think" in r.text:      # model without a thinking switch
        body.pop("think")
        r = requests.post(OLLAMA + "/api/generate", json=body, timeout=timeout)
    r.raise_for_status()
    return r.json()


def gpu_share(model):
    try:
        out = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=30).stdout
        for line in out.splitlines():
            if line.startswith(model):
                m = re.search(r"(\d+%\s*(?:GPU|CPU)(?:/\d+%\s*GPU)?)", line)
                return m.group(1) if m else line.strip()[:60]
    except Exception:
        pass
    return None


def run(models, pull=False, out=print, think=False, budget=1024):
    """think/budget select the configuration; the label stored with each row is
    ollama:<model>@<think|nothink><budget>, so configurations never mix."""
    from psycopg2.extras import execute_values
    from . import db
    run_id = "modelbench-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor() as cur:
        cur.execute("insert into pan.run (run_id, kind, host, params) values (%s,'modelbench',%s,%s)",
                    (run_id, host(), json.dumps({"models": models, "probes": len(PROBES), "think": think,
                                                 "budget": budget})))
    cfg = "@{}{}".format("think" if think else "nothink", budget)
    summary = {}
    for model in models:
        if pull:
            t = time.time()
            p = subprocess.run(["ollama", "pull", model], capture_output=True, text=True, timeout=7200)
            out("pull {} rc={} {:.0f}s".format(model, p.returncode, time.time() - t))
            if p.returncode != 0:
                summary[model] = dict(error="pull failed: " + (p.stderr or p.stdout)[-200:])
                continue
        rows, load_s, share = [], None, None
        for i, pr in enumerate(PROBES):
            t = time.time()
            try:
                g = generate(model, pr["prompt"], think=think, budget=budget)
                text = strip_thinking(g.get("response", ""))
                ok, detail = check(pr, text)
                ev, evd = g.get("eval_count") or 0, (g.get("eval_duration") or 0) / 1e9
                if ev >= budget:      # the answer may never have been reached: say so, do not hide it
                    detail = "TRUNCATED at {} tokens; {}".format(ev, detail)
                if i == 0:
                    load_s = (g.get("load_duration") or 0) / 1e9
                    share = gpu_share(model)
                rows.append((run_id, "ollama:" + model + cfg, HF_MAP.get(model), pr["id"], pr["kind"], ok, detail,
                             time.time() - t, ev, ev / evd if evd else None, load_s, share, text[:8000]))
            except Exception as e:
                rows.append((run_id, "ollama:" + model + cfg, HF_MAP.get(model), pr["id"], pr["kind"], False,
                             "{}: {}".format(type(e).__name__, e)[:200], time.time() - t, None, None, None, None, None))
        with db.cursor() as cur:
            execute_values(cur, """insert into pan.model_bench (run_id, model, hf_repo, probe_id, kind, ok, detail,
                                   latency_s, eval_tokens, tok_per_s, load_s, gpu_share, response) values %s""", rows)
        by = {}
        for r in rows:
            by.setdefault(r[4], []).append(r[5])
        tps = [r[9] for r in rows if r[9]]
        summary[model] = dict(config=cfg, passed=sum(r[5] for r in rows), of=len(rows),
                              truncated=sum(1 for r in rows if (r[6] or "").startswith("TRUNCATED")),
                              by_kind={k: "{}/{}".format(sum(v), len(v)) for k, v in by.items()},
                              median_tok_s=round(sorted(tps)[len(tps) // 2], 1) if tps else None,
                              load_s=round(load_s, 1) if load_s else None, gpu=share)
        out("{:<22} {}".format(model, json.dumps(summary[model])))
        subprocess.run(["ollama", "stop", model], capture_output=True, timeout=60)
    with db.cursor() as cur:
        cur.execute("update pan.run set finished_at=now(), status='OK', counts=%s where run_id=%s",
                    (json.dumps(summary), run_id))
    return run_id, summary
