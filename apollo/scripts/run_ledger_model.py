"""run_ledger_model.py — hit a local LLM HTTP server with ledger prompts.

Reads ledger_prompts.json, sends each prompt to a /generate_batch endpoint
(default localhost:8800), records full output + extraction + validation
results. Output is one JSONL per model in ledger_runs/<model_tag>.jsonl
so we can interrupt and resume.

Usage:
    python run_ledger_model.py <prompts_json> <model_tag> [--url http://localhost:8800] [--limit N]
"""
import sys
import json
import time
import re
import ast
import argparse
import urllib.request
import urllib.error
from pathlib import Path


def extract_code_body(text):
    m = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r'```\s*\n(.*?)```', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = text.strip().split('\n')
    code_lines = []
    started = False
    for line in lines:
        s = line.strip()
        if s.startswith('#') or s.startswith('scores') or s.startswith('return') or s.startswith('for ') or s.startswith('if ') or '=' in s:
            started = True
        if started:
            code_lines.append(line)
    return '\n'.join(code_lines) if code_lines else None


def validate_router_code(code):
    if not code:
        return False
    try:
        test = "def _route(prompt, candidates, outputs, params):\n"
        for line in code.strip().split('\n'):
            test += f"    {line}\n"
        ast.parse(test)
        return True
    except (SyntaxError, ValueError):
        return False


def extract_wiring_json(text):
    m = re.search(r'\{[^{}]+\}', text, re.DOTALL)
    return m.group(0) if m else None


def validate_wiring_json(text):
    if not text:
        return False
    try:
        d = json.loads(text)
        if not isinstance(d, dict):
            return False
        for k, v in d.items():
            if not (isinstance(k, str) and k.startswith('n') and isinstance(v, dict)):
                return False
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def extract_primitive(text):
    from genome import ALL_PRIMITIVES
    for p in ALL_PRIMITIVES:
        if p in text:
            return p
    return None


def score_response(prompt_dict, output):
    """Return a scoring dict for one prompt+output pair."""
    kind = prompt_dict["kind"]
    out_len = len(output)
    rec = {
        "id": prompt_dict["id"],
        "kind": kind,
        "variant": prompt_dict.get("variant", "base"),
        "out_chars": out_len,
        "output": output[:2000],  # truncate for storage
    }
    if kind == "route":
        code = extract_code_body(output)
        rec["extracted"] = code is not None
        rec["code_chars"] = len(code) if code else 0
        rec["valid"] = validate_router_code(code) if code else False
    elif kind == "wiring":
        js = extract_wiring_json(output)
        rec["extracted"] = js is not None
        rec["code_chars"] = len(js) if js else 0
        rec["valid"] = validate_wiring_json(js) if js else False
    elif kind == "swap":
        prim = extract_primitive(output)
        rec["extracted"] = prim is not None
        rec["code_chars"] = len(prim) if prim else 0
        rec["valid"] = prim is not None  # for swap, extracted == valid
        rec["primitive"] = prim
    return rec


def call_server(url, prompt, max_tokens=512, temperature=0.7, timeout=180):
    body = json.dumps({"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}).encode("utf-8")
    req = urllib.request.Request(f"{url}/generate", data=body, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        elapsed = time.time() - t0
        return data.get("text", ""), elapsed, None
    except urllib.error.URLError as e:
        return "", time.time() - t0, str(e)
    except Exception as e:
        return "", time.time() - t0, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompts_json")
    ap.add_argument("model_tag")
    ap.add_argument("--url", default="http://localhost:8800")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-tokens", type=int, default=512)
    args = ap.parse_args()

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    prompts_path = Path(args.prompts_json)
    out_dir = Path(__file__).parent.parent / "ledger_runs"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{args.model_tag}.jsonl"

    # Resume: skip already-done IDs
    done_ids = set()
    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    done_ids.add(d["id"])
                except: pass
        print(f"Resuming: {len(done_ids)} prompts already done in {out_path}")

    with open(prompts_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)["prompts"]
    if args.limit > 0:
        prompts = prompts[:args.limit]

    print(f"Running {args.model_tag} on {len(prompts)} prompts (skipping {len(done_ids)} done)")

    n_done = 0
    n_skip = 0
    with open(out_path, "a", encoding="utf-8") as f:
        for i, p in enumerate(prompts):
            if p["id"] in done_ids:
                n_skip += 1
                continue
            output, elapsed, err = call_server(
                args.url, p["prompt"],
                max_tokens=args.max_tokens, temperature=args.temperature,
            )
            rec = score_response(p, output)
            rec["model_tag"] = args.model_tag
            rec["elapsed_s"] = round(elapsed, 2)
            rec["error"] = err
            f.write(json.dumps(rec) + "\n")
            f.flush()
            n_done += 1
            if n_done % 10 == 0:
                print(f"  [{i+1}/{len(prompts)}] {p['kind']:6s} {p['id']} | extracted={rec.get('extracted')} valid={rec.get('valid')} | {elapsed:.1f}s")

    print(f"Done. {n_done} new, {n_skip} skipped. Output: {out_path}")


if __name__ == "__main__":
    main()
