"""Ergon — sustained-rate reliability harness for the Metabolization Probe solver lane.

Single-shot preflight (ergon/probe_api_preflight.py) proves a model ANSWERS.
This proves it answers *repeatedly, at a rate, for a duration* — which is the property
2,800 batched calls actually depend on, and the one that failed on 2026-03-28 when this
endpoint hit a 91% timeout rate (roles/PipelineOrchestrator/in_api_emergency_break_glass.md).

Three modes:
  ladder  — step through target rates, short burst at each, find the cliff
  soak    — hold one rate for a duration, watch for degradation over time
  diurnal — one small sample, designed to be run on a schedule to map good/bad hours

stdlib only (urllib + threads). Never prints key values. Appends typed JSONL.

  python ergon/probe_api_soak.py ladder  --rates 10,20,40,60 --seconds 60
  python ergon/probe_api_soak.py soak    --rate 30 --minutes 15
  python ergon/probe_api_soak.py diurnal --calls 6
"""
from __future__ import annotations
import argparse, json, os, pathlib, socket, sys, threading, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "ergon" / "probe_logs"
BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1.5"


def _load_env(p: pathlib.Path) -> dict:
    env = {}
    if not p.exists():
        return env
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def api_key() -> str:
    for src in (os.environ, _load_env(ROOT / "agents" / "eos" / ".env"), _load_env(ROOT / ".env")):
        v = src.get("NVIDIA_API_KEY")
        if v:
            return v
    print("NVIDIA_API_KEY not found (env, agents/eos/.env, .env)", file=sys.stderr)
    sys.exit(2)


TASK = ("Claim: 8566 and 907 are coprime (share no common factor greater than 1).\n"
        "Is this claim true? Answer True or False, then justify in one sentence.")
_FILL = ("kill_signature: invariant_equality | margin: 0.0031 | falsifier: F17 | "
         "kill_pattern: asserted-equality-without-executing-computation | break_step: null\n")


def packet_prompt(approx_tokens: int = 8000) -> str:
    """Realistic F-prom-retrieved packet at the prereg 4.5 ceiling (~8K tokens)."""
    units = max(1, approx_tokens // 38)
    return ("Prior failure residue from earlier attempts on related problems.\n\n"
            + _FILL * units + "\n\n" + TASK)


_lock = threading.Lock()


def one_call(key: str, model: str, prompt: str, timeout: float, out_path: pathlib.Path,
             phase: str, target_rate: float) -> dict:
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 64, "temperature": 0.0}).encode()
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    now = datetime.now(timezone.utc)
    rec = {"ts_utc": now.isoformat(timespec="seconds"),
           "hour_utc": now.hour,
           "hour_local": datetime.now().hour,
           "phase": phase, "target_rate_rpm": target_rate,
           "model": model, "prompt_chars": len(prompt), "timeout_s": timeout}
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
        dt = time.monotonic() - t0
        u = j.get("usage") or {}
        txt = (((j.get("choices") or [{}])[0].get("message", {}) or {}).get("content") or "")
        rec.update(status="ok", latency_s=round(dt, 2),
                   prompt_tokens=u.get("prompt_tokens"),
                   completion_tokens=u.get("completion_tokens"),
                   parsed_verdict=("true" if "true" in txt[:200].lower()
                                   else "false" if "false" in txt[:200].lower() else None))
    except Exception as e:
        dt = time.monotonic() - t0
        et = type(e).__name__
        if isinstance(e, urllib.error.HTTPError):
            et = f"HTTP{e.code}"
        elif isinstance(e, (socket.timeout, TimeoutError)):
            et = "TIMEOUT"
        elif isinstance(e, urllib.error.URLError) and isinstance(getattr(e, "reason", None), socket.timeout):
            et = "TIMEOUT"
        rec.update(status="error", latency_s=round(dt, 2), error_type=et, error=str(e)[:160])
    with _lock, out_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def run_window(key, model, prompt, rate_rpm, seconds, timeout, out_path, phase, workers=8):
    """Dispatch at target rate for `seconds`; returns records."""
    interval = 60.0 / rate_rpm
    n = max(1, int(round(seconds / interval)))
    recs, t_start = [], time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = []
        for i in range(n):
            due = t_start + i * interval
            slack = due - time.monotonic()
            if slack > 0:
                time.sleep(slack)
            futures.append(ex.submit(one_call, key, model, prompt, timeout,
                                     out_path, phase, rate_rpm))
        for fu in futures:
            recs.append(fu.result())
    return recs


def summarize(recs, label):
    ok = [r for r in recs if r["status"] == "ok"]
    errs = {}
    for r in recs:
        if r["status"] == "error":
            errs[r["error_type"]] = errs.get(r["error_type"], 0) + 1
    lat = sorted(r["latency_s"] for r in ok)

    def pct(p):
        return lat[min(len(lat) - 1, int(p * len(lat)))] if lat else float("nan")

    rate = len(ok) / len(recs) * 100 if recs else 0.0
    print(f"  {label:28s} {len(ok):3d}/{len(recs):3d} ok ({rate:5.1f}%)  "
          f"p50 {pct(0.5):6.1f}s  p90 {pct(0.9):6.1f}s  max {(lat[-1] if lat else float('nan')):6.1f}s"
          + (f"  errors={errs}" if errs else ""))
    return {"label": label, "n": len(recs), "ok": len(ok), "ok_pct": round(rate, 1),
            "p50": pct(0.5), "p90": pct(0.9), "errors": errs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["ladder", "soak", "diurnal"])
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--rates", default="10,20,40,60")
    ap.add_argument("--rate", type=float, default=30.0)
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--minutes", type=float, default=15.0)
    ap.add_argument("--calls", type=int, default=6)
    ap.add_argument("--tokens", type=int, default=8000, help="approx packet size")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = pathlib.Path(args.out) if args.out else OUT_DIR / f"soak_{args.mode}.jsonl"
    key = api_key()
    prompt = packet_prompt(args.tokens)
    print(f"model={args.model}\npayload~{args.tokens} tok ({len(prompt)} chars)  "
          f"timeout={args.timeout}s  log={out_path.name}\n")

    if args.mode == "ladder":
        print("--- rate ladder (find the cliff) ---")
        rows = []
        for rate in [float(x) for x in args.rates.split(",")]:
            recs = run_window(key, args.model, prompt, rate, args.seconds,
                              args.timeout, out_path, f"ladder@{rate:g}")
            rows.append(summarize(recs, f"{rate:g} RPM x {args.seconds}s"))
        clean = [r for r in rows if r["ok_pct"] >= 99.0]
        print("\n  highest fully-clean rate: "
              + (clean[-1]["label"] if clean else "NONE — every rate degraded"))

    elif args.mode == "soak":
        seconds = int(args.minutes * 60)
        print(f"--- soak: {args.rate:g} RPM for {args.minutes:g} min "
              f"(~{int(seconds/(60/args.rate))} calls) ---")
        recs = run_window(key, args.model, prompt, args.rate, seconds,
                          args.timeout, out_path, f"soak@{args.rate:g}")
        # degradation check: split in quarters, compare success rate over time
        q = max(1, len(recs) // 4)
        print()
        for i in range(0, len(recs), q):
            summarize(recs[i:i + q], f"minute-block {i//q + 1}")
        print()
        summarize(recs, "OVERALL")

    else:  # diurnal
        recs = run_window(key, args.model, prompt, 20.0, max(1, int(args.calls * 3)),
                          args.timeout, out_path, "diurnal")
        recs = recs[:args.calls] if len(recs) > args.calls else recs
        h = datetime.now().hour
        summarize(recs, f"local hour {h:02d}")


if __name__ == "__main__":
    main()
