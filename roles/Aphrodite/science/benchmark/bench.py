"""Bounded throughput benchmark for the Campaign 1 host path (operator item 8, 2026-09-18).

Runs the ACTUAL loop shape of Campaign 1 at a tiny, capped scale -- an
improvement operator proposes worker variants (one model call each), each
variant is evaluated on short procedural tasks (one model call per task,
answers checked by code), the best is kept -- and MEASURES tokens/task,
wall time/eval, evals/generation, GPU utilisation, lineage cost, and the
projected full-campaign wall time. It authorises no Campaign 1 evolution:
2 lineages x 2 generations by default, hard caps on calls and wall time.

Usage on the M1/M2 host (an OpenAI-compatible server already serving the
candidate model, e.g. llama.cpp server, vLLM or Ollama):
    python bench.py --base-url http://127.0.0.1:8000 --model <name> --out result.json
Dry run anywhere (no model, no GPU; validates the harness only):
    python bench.py --stub --out stub.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import subprocess
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# ------------------------------------------------------------------ procedural tasks (checkable)
FAMILIES = ("arith", "sortkey", "strops", "numtheory")


def make_task(family: str, rng: random.Random):
    if family == "arith":
        a, b, c, d = (rng.randint(2, 99) for _ in range(4))
        expr = f"({a} + {b}) * {c} - {d}"
        return f"Compute the value of {expr}.", str((a + b) * c - d)
    if family == "sortkey":
        xs = [rng.randint(0, 999) for _ in range(8)]
        return (f"Sort these numbers by their last digit, ties by value ascending, and list them comma-separated: "
                f"{', '.join(map(str, xs))}"), ",".join(map(str, sorted(xs, key=lambda x: (x % 10, x))))
    if family == "strops":
        words = [rng.choice(["alpha", "delta", "sigma", "omega", "kappa", "theta", "gamma"]) for _ in range(5)]
        return (f"Reverse the order of these words and uppercase the first letter of each: {' '.join(words)}",
                " ".join(w.capitalize() for w in reversed(words)))
    a, b = rng.randint(12, 999), rng.randint(12, 999)
    import math
    return f"Give gcd({a}, {b}) + lcm({a}, {b}) as an integer.", str(math.gcd(a, b) + a * b // math.gcd(a, b))


def check(answer_text: str, gold: str) -> bool:
    m = re.search(r"<answer>(.*?)</answer>", answer_text or "", re.S)
    got = (m.group(1) if m else "").strip().replace(" ,", ",").replace(", ", ",")
    return got == gold.replace(", ", ",")


# ------------------------------------------------------------------ model clients
class OpenAIClient:
    def __init__(self, base_url: str, model: str, timeout: float = 120.0):
        self.url = base_url.rstrip("/") + "/v1/chat/completions"
        self.model = model
        self.timeout = timeout

    def chat(self, system: str, user: str, max_tokens: int, temperature: float):
        body = json.dumps({"model": self.model, "max_tokens": max_tokens, "temperature": temperature,
                           "messages": [{"role": "system", "content": system},
                                        {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            d = json.loads(r.read())
        dt = time.time() - t0
        u = d.get("usage") or {}
        return d["choices"][0]["message"]["content"], u.get("prompt_tokens", 0), u.get("completion_tokens", 0), dt


class StubClient:
    """Deterministic fake model for dry runs: answers correctly half the time, reports token counts."""

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)
        self.lock = threading.Lock()

    def chat(self, system: str, user: str, max_tokens: int, temperature: float):
        with self.lock:
            ok = self.rng.random() < 0.5
            n_out = self.rng.randint(40, min(max_tokens, 400))
        gold = user.split("GOLD=")[-1] if "GOLD=" in user else ""
        text = f"reasoning... <answer>{gold if ok else 'x'}</answer>" if gold else "Revised system prompt: be exact."
        return text, len(system.split()) + len(user.split()), n_out, 0.0


# ------------------------------------------------------------------ GPU sampler
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
            except Exception:  # noqa: BLE001 -- no GPU visible: recorded as no samples
                pass
            time.sleep(self.period)


# ------------------------------------------------------------------ the bounded loop
BASE_SYSTEM = "Solve the task. Put only the final answer between <answer> and </answer>."


def run(args, client):
    rng = random.Random(args.seed)
    calls = {"n": 0}
    lock = threading.Lock()
    t_start = time.time()
    evals = []          # one record per task evaluation
    improver_calls = []

    def budget_ok():
        return calls["n"] < args.max_calls and time.time() - t_start < args.max_wall_s

    def call(system, user, max_tokens, temperature):
        with lock:
            if not budget_ok():
                raise RuntimeError("benchmark cap reached")
            calls["n"] += 1
        return client.chat(system, user, max_tokens, temperature)

    def eval_task(system, fam, seed):
        r = random.Random(seed)
        prompt, gold = make_task(fam, r)
        user = prompt + (f"\nGOLD={gold}" if args.stub else "")
        text, tin, tout, dt = call(system, user, args.max_tokens, 0.0)
        return {"family": fam, "ok": check(text, gold), "tin": tin, "tout": tout, "wall": dt}

    per_gen = []
    for lineage in range(args.lineages):
        system = BASE_SYSTEM
        for gen in range(args.generations):
            g0 = time.time()
            # improver proposes variants (one model call each), from recent failures
            variants = [system]
            for v in range(args.variants - 1):
                text, tin, tout, dt = call("You improve instructions for a solver.",
                                           f"Current instructions:\n{system}\nPropose improved instructions.",
                                           256, 0.7)
                improver_calls.append({"tin": tin, "tout": tout, "wall": dt})
                variants.append(text.strip()[:1500] or system)
            scores = []
            with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
                for vi, sysmsg in enumerate(variants):
                    seeds = [(lineage, gen, vi, t) for t in range(args.tasks_per_eval)]
                    futs = [ex.submit(eval_task, sysmsg, FAMILIES[t % len(FAMILIES)],
                                      hash(s) & 0xFFFFFFFF) for t, s in enumerate(seeds)]
                    res = [f.result() for f in futs]
                    evals.extend(res)
                    scores.append(sum(x["ok"] for x in res) / len(res))
            system = variants[max(range(len(variants)), key=lambda i: scores[i])]
            per_gen.append({"lineage": lineage, "generation": gen, "wall_s": time.time() - g0,
                            "evaluations": len(variants) * args.tasks_per_eval, "best_score": max(scores)})
    return evals, improver_calls, per_gen, time.time() - t_start, calls["n"]


def summarize(args, evals, improver_calls, per_gen, wall, n_calls, gpu):
    toks = [e["tin"] + e["tout"] for e in evals]
    walls = [e["wall"] for e in evals]
    evals_per_gen = statistics.mean(g["evaluations"] for g in per_gen)
    gen_wall = statistics.mean(g["wall_s"] for g in per_gen)
    lineage_tokens = (sum(toks) + sum(c["tin"] + c["tout"] for c in improver_calls)) / args.lineages
    lineage_wall = sum(g["wall_s"] for g in per_gen) / args.lineages
    eval_throughput = len(evals) / max(wall, 1e-9)  # task evaluations per second at this concurrency

    def project(L, G, evo_evals_per_gen):
        assay = 1760 + 20480 / 64  # primary assay per lineage + secondary confirm share per lineage (upper bound)
        per_lineage_evals = G * evo_evals_per_gen + assay
        return {"lineages": L, "generations": G, "evo_evals_per_gen": evo_evals_per_gen,
                "task_evaluations": L * per_lineage_evals,
                "projected_wall_days_single_host": L * per_lineage_evals / max(eval_throughput, 1e-9) / 86400}

    return {
        "measured": {
            "task_evaluations": len(evals), "model_calls": n_calls, "wall_s": round(wall, 1),
            "tokens_per_task": {"mean": round(statistics.mean(toks), 1), "p50": statistics.median(toks),
                                "p95": sorted(toks)[int(0.95 * (len(toks) - 1))]},
            "wall_s_per_eval": {"mean": round(statistics.mean(walls), 3), "p95": round(sorted(walls)[int(0.95 * (len(walls) - 1))], 3)},
            "evaluations_per_generation": evals_per_gen, "wall_s_per_generation": round(gen_wall, 1),
            "eval_throughput_per_s": round(eval_throughput, 3), "concurrency": args.concurrency,
            "lineage_cost": {"tokens": round(lineage_tokens), "wall_s": round(lineage_wall, 1)},
            "gpu": None if not gpu else {"util_mean": round(statistics.mean(u for u, _ in gpu), 1),
                                         "util_max": max(u for u, _ in gpu),
                                         "mem_used_max_mib": max(m for _, m in gpu), "samples": len(gpu)},
            "task_accuracy": round(sum(e["ok"] for e in evals) / len(evals), 3),
        },
        "projection": [project(L, 8, e) for L in (32, 64) for e in (evals_per_gen, 200, 1000)],
        "config": vars(args),
        "notes": "Projection = measured eval throughput at this concurrency, one host; excludes scheduling "
                 "gaps and failures. Accuracy is recorded only to show tasks are not trivially failed; it is "
                 "not a result.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url")
    ap.add_argument("--model")
    ap.add_argument("--stub", action="store_true")
    ap.add_argument("--lineages", type=int, default=2)
    ap.add_argument("--generations", type=int, default=2)
    ap.add_argument("--variants", type=int, default=4)
    ap.add_argument("--tasks-per-eval", type=int, default=20)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--max-calls", type=int, default=2000)
    ap.add_argument("--max-wall-s", type=int, default=3600)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    assert args.lineages <= 4 and args.generations <= 3, "bounded benchmark: no Campaign 1 evolution"
    client = StubClient(args.seed) if args.stub else OpenAIClient(args.base_url, args.model)
    gpu = GpuSampler()
    gpu.start()
    evals, imp, per_gen, wall, n = run(args, client)
    gpu.stop_flag = True
    out = summarize(args, evals, imp, per_gen, wall, n, gpu.samples)
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["measured"], indent=1))


if __name__ == "__main__":
    main()
