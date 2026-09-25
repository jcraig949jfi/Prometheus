"""Bounded throughput benchmark for the Campaign 1 host path -- FROZEN harness v2 (2026-09-18).

Operator directives of 2026-09-18 (items 8 and "BENCHMARK EXECUTION"): run
host-locally by Nestor on M1 and Archaeon on M2, identical harness commit,
fixtures, settings, caps and schema; executors do not alter this file
(its sha256 is recorded in every receipt and checked by economics.py).

It runs the ACTUAL loop shape of Campaign 1 at a tiny, capped scale and
MEASURES cost; it authorises no Campaign 1 evolution.
  phase 1  STARTING ACCURACY: the unmodified base worker on a fixed set of
           200 tasks (50 per family, fixed seeds identical on every host),
           temperature 0 -- the input to the 15-70% selection rule.
  phase 2  LOOP: 2 lineages x 2 generations; per generation the improver
           makes 3 model calls proposing worker instructions; 4 variants
           x 20 tasks are evaluated (one call per task, answers checked by
           code); the best variant is kept.

Usage on the host (an OpenAI-compatible server already serving the model):
  python bench.py --host-label M1 --base-url http://127.0.0.1:<port> --model <served-name> \
      --checkpoint "<exact file or tag>" --quant "<e.g. Q4_K_M>" --runtime "<e.g. llama.cpp server b5000>" \
      [--extra-body '{"chat_template_kwargs": {"enable_thinking": false}}'] --out <receipt.json>
Dry run anywhere: python bench.py --stub --host-label STUB --out stub.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import statistics
import subprocess
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HARNESS_VERSION = "bench-v2-2026-09-18"
FAMILIES = ("arith", "sortkey", "strops", "numtheory")
FROZEN = {"lineages": 2, "generations": 2, "variants": 4, "tasks_per_eval": 20, "concurrency": 8,
          "max_tokens": 512, "max_calls": 2000, "max_wall_s": 3600, "retries": 2,
          "baseline_per_family": 50, "baseline_seed": 20260918, "loop_seed": 0}
CAMPAIGN = {"generations": 8, "assay_evals_per_lineage": 1760, "secondary_confirm_evals_per_lineage": 320,
            "evo_evals_per_gen_options": ["measured", 200, 1000], "lineages": [32, 64]}


# ------------------------------------------------------------------ procedural tasks (checkable)
def make_task(family: str, rng: random.Random):
    if family == "arith":
        a, b, c, d = (rng.randint(2, 99) for _ in range(4))
        return f"Compute the value of ({a} + {b}) * {c} - {d}.", str((a + b) * c - d)
    if family == "sortkey":
        xs = [rng.randint(0, 999) for _ in range(8)]
        return (f"Sort these numbers by their last digit, ties by value ascending, and list them comma-separated: "
                f"{', '.join(map(str, xs))}"), ",".join(map(str, sorted(xs, key=lambda x: (x % 10, x))))
    if family == "strops":
        words = [rng.choice(["alpha", "delta", "sigma", "omega", "kappa", "theta", "gamma"]) for _ in range(5)]
        return (f"Reverse the order of these words and uppercase the first letter of each: {' '.join(words)}",
                " ".join(w.capitalize() for w in reversed(words)))
    a, b = rng.randint(12, 999), rng.randint(12, 999)
    return f"Give gcd({a}, {b}) + lcm({a}, {b}) as an integer.", str(math.gcd(a, b) + a * b // math.gcd(a, b))


def parse_answer(text: str):
    m = re.search(r"<answer>(.*?)</answer>", text or "", re.S)
    return None if not m else m.group(1).strip().replace(" ,", ",").replace(", ", ",")


def task_seed(*parts) -> int:
    return int(hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:12], 16)


# ------------------------------------------------------------------ model clients
class OpenAIClient:
    def __init__(self, base_url, model, extra_body=None, timeout=180.0):
        self.base = base_url.rstrip("/")
        self.model, self.extra, self.timeout = model, extra_body or {}, timeout

    def served_models(self):
        try:
            with urllib.request.urlopen(self.base + "/v1/models", timeout=20) as r:
                return [m.get("id") for m in json.loads(r.read()).get("data", [])]
        except Exception as e:  # noqa: BLE001
            return [f"unavailable: {e!r}"]

    def chat(self, system, user, max_tokens, temperature):
        body = {"model": self.model, "max_tokens": max_tokens, "temperature": temperature,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        body.update(self.extra)
        req = urllib.request.Request(self.base + "/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            d = json.loads(r.read())
        u = d.get("usage") or {}
        return d["choices"][0]["message"]["content"], int(u.get("prompt_tokens", 0)), int(u.get("completion_tokens", 0))


class StubClient:
    """Deterministic fake model for dry runs only."""

    def __init__(self, seed=0):
        self.rng, self.lock = random.Random(seed), threading.Lock()

    def served_models(self):
        return ["stub"]

    def chat(self, system, user, max_tokens, temperature):
        with self.lock:
            ok, n_out, fail = self.rng.random() < 0.4, self.rng.randint(40, min(max_tokens, 400)), self.rng.random() < 0.01
        if fail:
            raise TimeoutError("stub transient failure")
        gold = user.split("GOLD=")[-1] if "GOLD=" in user else ""
        text = (f"<answer>{gold if ok else 'x'}</answer>" if gold else "Revised instructions: be exact.")
        return text, len(system.split()) + len(user.split()), n_out


# ------------------------------------------------------------------ GPU
def gpu_identity():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                              "--format=csv,noheader"], capture_output=True, text=True, timeout=10).stdout.strip()
        return [line.strip() for line in out.splitlines() if line.strip()] or ["nvidia-smi: no GPU listed"]
    except Exception as e:  # noqa: BLE001
        return [f"nvidia-smi unavailable: {e!r}"]


class GpuSampler(threading.Thread):
    def __init__(self, period=1.0):
        super().__init__(daemon=True)
        self.period, self.samples, self.stop_flag = period, [], False

    def run(self):
        while not self.stop_flag:
            try:
                out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                                      "--format=csv,noheader,nounits"], capture_output=True, text=True,
                                     timeout=5).stdout.strip().splitlines()
                for line in out:
                    u, m = (float(x) for x in line.split(","))
                    self.samples.append((u, m))
            except Exception:  # noqa: BLE001
                pass
            time.sleep(self.period)


# ------------------------------------------------------------------ calls with retries
class Caller:
    def __init__(self, client, stub):
        self.client, self.stub = client, stub
        self.lock = threading.Lock()
        self.n_calls = self.n_retries = self.n_failed = 0
        self.t0 = time.time()

    def __call__(self, system, user, max_tokens, temperature):
        for attempt in range(FROZEN["retries"] + 1):
            with self.lock:
                if self.n_calls >= FROZEN["max_calls"] or time.time() - self.t0 > FROZEN["max_wall_s"]:
                    raise RuntimeError("benchmark cap reached")
                self.n_calls += 1
                if attempt:
                    self.n_retries += 1
            t = time.time()
            try:
                text, tin, tout = self.client.chat(system, user, max_tokens, temperature)
                return {"text": text, "tin": tin, "tout": tout, "wall": time.time() - t, "ok_call": True}
            except RuntimeError:
                raise
            except Exception:  # noqa: BLE001 -- counted, retried, then recorded as failed
                continue
        with self.lock:
            self.n_failed += 1
        return {"text": "", "tin": 0, "tout": 0, "wall": 0.0, "ok_call": False}


BASE_SYSTEM = "Solve the task. Put only the final answer between <answer> and </answer>."


def eval_task(caller, system, fam, seed, stub):
    prompt, gold = make_task(fam, random.Random(seed))
    r = caller(system, prompt + (f"\nGOLD={gold}" if stub else ""), FROZEN["max_tokens"], 0.0)
    ans = parse_answer(r["text"])
    r.update({"family": fam, "format_ok": ans is not None, "correct": ans == gold.replace(", ", ",")})
    del r["text"]
    return r


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host-label", required=True)
    ap.add_argument("--base-url")
    ap.add_argument("--model")
    ap.add_argument("--checkpoint", default="")
    ap.add_argument("--quant", default="")
    ap.add_argument("--runtime", default="")
    ap.add_argument("--extra-body", default="{}")
    ap.add_argument("--stub", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    here = Path(__file__).resolve()
    receipt = {"harness_version": HARNESS_VERSION,
               "harness_sha256": hashlib.sha256(here.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
               "harness_git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                                                  cwd=here.parent).stdout.strip(),
               "host_label": a.host_label, "frozen_settings": FROZEN, "campaign_assumptions": CAMPAIGN,
               "model": {"requested": a.model, "checkpoint": a.checkpoint, "quant": a.quant, "runtime": a.runtime,
                         "extra_body": json.loads(a.extra_body)},
               "gpu_identity": gpu_identity(), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    client = StubClient() if a.stub else OpenAIClient(a.base_url, a.model, json.loads(a.extra_body))
    receipt["model"]["served_models"] = client.served_models()
    caller = Caller(client, a.stub)
    gpu = GpuSampler()
    gpu.start()

    # phase 1: frozen starting accuracy
    base = []
    with ThreadPoolExecutor(max_workers=FROZEN["concurrency"]) as ex:
        futs = [ex.submit(eval_task, caller, BASE_SYSTEM, fam, task_seed("baseline", FROZEN["baseline_seed"], fam, i),
                          a.stub) for fam in FAMILIES for i in range(FROZEN["baseline_per_family"])]
        base = [f.result() for f in futs]
    nb, kb = len(base), sum(r["correct"] for r in base)
    receipt["starting_accuracy"] = {"n": nb, "correct": kb, "accuracy": round(kb / nb, 4), "wilson95": wilson(kb, nb),
                                    "by_family": {f: round(sum(r["correct"] for r in base if r["family"] == f) /
                                                           FROZEN["baseline_per_family"], 4) for f in FAMILIES},
                                    "format_failure_rate": round(sum(not r["format_ok"] for r in base) / nb, 4)}

    # phase 2: the bounded loop
    rng = random.Random(FROZEN["loop_seed"])
    evals, gens = [], []
    for lin in range(FROZEN["lineages"]):
        system = BASE_SYSTEM
        for gen in range(FROZEN["generations"]):
            g0, calls0 = time.time(), caller.n_calls
            variants = [system]
            for _ in range(FROZEN["variants"] - 1):
                r = caller("You improve instructions for a solver.",
                           f"Current instructions:\n{system}\nPropose improved instructions. Keep the rule that the "
                           f"final answer goes between <answer> and </answer>.", 256, 0.7)
                variants.append((r["text"] or system).strip()[:1500])
            scores = []
            with ThreadPoolExecutor(max_workers=FROZEN["concurrency"]) as ex:
                for vi, sysmsg in enumerate(variants):
                    futs = [ex.submit(eval_task, caller, sysmsg, FAMILIES[t % 4], task_seed("loop", lin, gen, vi, t),
                                      a.stub) for t in range(FROZEN["tasks_per_eval"])]
                    res = [f.result() for f in futs]
                    evals += res
                    scores.append(sum(x["correct"] for x in res) / len(res))
            system = variants[max(range(len(variants)), key=lambda i: scores[i])]
            wall = time.time() - g0
            n_ev = len(variants) * FROZEN["tasks_per_eval"]
            gens.append({"lineage": lin, "generation": gen, "wall_s": round(wall, 2), "evaluations": n_ev,
                         "model_calls": caller.n_calls - calls0, "evals_per_s": round(n_ev / max(wall, 1e-9), 4)})
    gpu.stop_flag = True
    wall_total = time.time() - caller.t0

    tin = [e["tin"] for e in evals if e["ok_call"]]
    tout = [e["tout"] for e in evals if e["ok_call"]]
    walls = [e["wall"] for e in evals if e["ok_call"]]
    thr = [g["evals_per_s"] for g in gens]
    thr_mean = statistics.mean(thr)
    thr_cons = min(thr) if len(thr) < 3 else max(min(thr), thr_mean - 1.2816 * statistics.stdev(thr))
    epg = statistics.mean(g["evaluations"] for g in gens)
    tok_task = statistics.mean(i + o for i, o in zip(tin, tout)) if tin else 0.0

    def proj(L, e, t):
        per_lin = CAMPAIGN["generations"] * e + CAMPAIGN["assay_evals_per_lineage"] + \
            CAMPAIGN["secondary_confirm_evals_per_lineage"]
        days = L * per_lin / max(t, 1e-9) / 86400
        return {"lineages": L, "evo_evals_per_gen": e, "task_evaluations": L * per_lin,
                "tokens": round(L * per_lin * tok_task), "single_host_days": round(days, 3),
                "lineages_per_day": round(L / days, 3) if days else None}

    receipt["measured"] = {
        "wall_s_total": round(wall_total, 1), "model_calls": caller.n_calls, "retries": caller.n_retries,
        "failed_calls": caller.n_failed,
        "failure_rate": round(caller.n_failed / max(caller.n_calls, 1), 5),
        "retry_rate": round(caller.n_retries / max(caller.n_calls, 1), 5),
        "format_failure_rate_loop": round(sum(not e["format_ok"] for e in evals) / len(evals), 4),
        "tokens_in_per_task": {"mean": round(statistics.mean(tin), 1), "p95": sorted(tin)[int(0.95 * (len(tin) - 1))]},
        "tokens_out_per_task": {"mean": round(statistics.mean(tout), 1), "p95": sorted(tout)[int(0.95 * (len(tout) - 1))]},
        "tokens_per_task_mean": round(tok_task, 1),
        "wall_s_per_eval": {"mean": round(statistics.mean(walls), 3), "p95": round(sorted(walls)[int(0.95 * (len(walls) - 1))], 3)},
        "evaluations_per_generation": epg,
        "model_calls_per_generation": statistics.mean(g["model_calls"] for g in gens),
        "per_generation": gens,
        "eval_throughput_per_s": {"mean": round(thr_mean, 4), "conservative": round(thr_cons, 4),
                                  "rule": "min of per-generation throughputs (fewer than 3) else "
                                          "max(min, mean - 1.2816 sd)"},
        "gpu": None if not gpu.samples else {"util_mean": round(statistics.mean(u for u, _ in gpu.samples), 1),
                                              "util_max": max(u for u, _ in gpu.samples),
                                              "mem_used_high_water_mib": max(m for _, m in gpu.samples),
                                              "samples": len(gpu.samples)},
    }
    receipt["projection_single_host"] = [
        dict(proj(L, epg if e == "measured" else e, t), throughput=which)
        for L in CAMPAIGN["lineages"] for e in CAMPAIGN["evo_evals_per_gen_options"]
        for which, t in (("mean", thr_mean), ("conservative", thr_cons))]
    receipt["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    Path(a.out).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    print(json.dumps({"starting_accuracy": receipt["starting_accuracy"], "measured": {
        k: receipt["measured"][k] for k in ("model_calls", "failure_rate", "tokens_per_task_mean",
                                            "eval_throughput_per_s")}}, indent=1))


if __name__ == "__main__":
    main()
