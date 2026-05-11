"""
Gemini Deep Research dispatcher — fires the prompt deck through the
client.interactions API at agent='deep-research-pro-preview-12-2025'.

Usage:
    python aporia/scripts/gemini_deep_research_dispatch.py \\
        --deck aporia/docs/gemini_deep_research_deck_2026-05-10.md \\
        --out  aporia/docs/deep_research_batch_2026-05-10 \\
        --batch-size 3 \\
        [--probe]                 # only fire prompt 01 sequentially
        [--only 1,2,3]            # only fire specified prompt numbers
        [--resume]                # skip prompts whose output already exists

Each prompt is fired with background=True; the dispatcher polls every
30 s for completion and writes the resulting text to
<out>/<NN>_<slug>.md. A run-summary JSON is appended after each batch.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from keys import get_key  # noqa: E402

from google import genai  # noqa: E402

AGENT = "deep-research-pro-preview-12-2025"
POLL_INTERVAL_SEC = 30
POLL_TIMEOUT_SEC = 60 * 60  # 1 h ceiling per prompt


# ---------------------------------------------------------------------------
# Deck parser
# ---------------------------------------------------------------------------

PROMPT_HEADER_RE = re.compile(r"^### Prompt (\d+):\s*(.+?)\s*$", re.MULTILINE)


def parse_deck(deck_path: Path) -> list[dict]:
    """Extract numbered prompts from the deck markdown.

    Each prompt is a `### Prompt N: <title>` heading followed by a
    fenced code block holding the prompt text.
    """
    text = deck_path.read_text(encoding="utf-8")
    prompts: list[dict] = []

    headers = list(PROMPT_HEADER_RE.finditer(text))
    for i, m in enumerate(headers):
        n = int(m.group(1))
        title = m.group(2).strip()

        # Find the next ``` fence after this header
        body_start = text.find("```", m.end())
        if body_start == -1:
            continue
        body_start_nl = text.find("\n", body_start) + 1
        body_end = text.find("```", body_start_nl)
        if body_end == -1:
            continue

        body = text[body_start_nl:body_end].strip()

        # If body is just a TBD placeholder note, skip
        if body.startswith("[Pick based on") or body.startswith("[TBD"):
            print(f"  [skip] Prompt {n}: TBD placeholder")
            continue

        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        slug = slug[:60]

        prompts.append({
            "num": n,
            "title": title,
            "slug": slug,
            "body": body,
        })

    prompts.sort(key=lambda p: p["num"])
    return prompts


# ---------------------------------------------------------------------------
# Single-prompt fire
# ---------------------------------------------------------------------------

def extract_text_from_interaction(interaction: Any) -> str:
    """Pull the report text out of a completed Interaction object."""
    parts: list[str] = []

    # The interactions API uses `outputs` (plural): list of content items, each with .text
    for attr in ("outputs", "output", "response", "result", "content", "contents"):
        if hasattr(interaction, attr):
            val = getattr(interaction, attr)
            if val is None:
                continue
            if isinstance(val, str):
                parts.append(val)
                continue
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        parts.append(item)
                    elif hasattr(item, "text"):
                        parts.append(getattr(item, "text") or "")
                    elif isinstance(item, dict) and "text" in item:
                        parts.append(item["text"])
            elif hasattr(val, "text"):
                parts.append(getattr(val, "text") or "")

    text = "\n".join(p for p in parts if p)
    if not text:
        # Fall back to model_dump and try to dig out outputs[].text
        try:
            d = interaction.model_dump()
            outputs = d.get("outputs") or d.get("output") or []
            if isinstance(outputs, list):
                for item in outputs:
                    if isinstance(item, dict) and "text" in item:
                        parts.append(item["text"])
            text = "\n".join(p for p in parts if p)
        except Exception:
            pass
    if not text:
        try:
            text = json.dumps(interaction.model_dump(), indent=2, default=str)
        except Exception:
            text = str(interaction)
    return text


def fire_one(client: genai.Client, prompt: dict, out_dir: Path) -> dict:
    """Fire one prompt, poll until done, save output. Returns status dict."""
    n = prompt["num"]
    slug = prompt["slug"]
    out_path = out_dir / f"{n:02d}_{slug}.md"

    t0 = time.time()
    print(f"[{n:02d}] Starting: {prompt['title']!r}")

    try:
        interaction = client.interactions.create(
            input=prompt["body"],
            agent=AGENT,
            background=True,
            store=True,
        )
    except Exception as e:
        msg = f"create() failed: {e}"
        print(f"[{n:02d}] {msg}")
        return {
            "num": n, "slug": slug, "status": "error", "stage": "create",
            "error": msg, "elapsed_s": time.time() - t0,
        }

    interaction_id = getattr(interaction, "id", None) or getattr(interaction, "interaction_id", None)
    print(f"[{n:02d}] Started, id={interaction_id}")

    deadline = time.time() + POLL_TIMEOUT_SEC
    last_status = None
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_SEC)
        try:
            interaction = client.interactions.get(interaction_id)
        except Exception as e:
            print(f"[{n:02d}] poll error (continuing): {e}")
            continue

        status = getattr(interaction, "status", None)
        if status != last_status:
            elapsed = int(time.time() - t0)
            print(f"[{n:02d}] status={status} (elapsed {elapsed}s)")
            last_status = status

        if status in ("completed", "succeeded", "success"):
            text = extract_text_from_interaction(interaction)
            out_path.write_text(
                f"# Prompt {n:02d}: {prompt['title']}\n\n"
                f"**Agent:** {AGENT}\n"
                f"**Interaction ID:** {interaction_id}\n"
                f"**Elapsed:** {int(time.time() - t0)}s\n\n"
                f"---\n\n{text}\n",
                encoding="utf-8",
            )
            print(f"[{n:02d}] DONE -> {out_path.name}")
            return {
                "num": n, "slug": slug, "status": "completed",
                "interaction_id": interaction_id,
                "output_path": str(out_path),
                "elapsed_s": time.time() - t0,
            }

        if status in ("failed", "cancelled", "error"):
            err = getattr(interaction, "error", None) or "unknown"
            msg = f"interaction status={status}, err={err}"
            print(f"[{n:02d}] {msg}")
            return {
                "num": n, "slug": slug, "status": status,
                "interaction_id": interaction_id,
                "error": str(err), "elapsed_s": time.time() - t0,
            }

    print(f"[{n:02d}] TIMEOUT after {POLL_TIMEOUT_SEC}s")
    return {
        "num": n, "slug": slug, "status": "timeout",
        "interaction_id": interaction_id,
        "elapsed_s": time.time() - t0,
    }


# ---------------------------------------------------------------------------
# Batch loop
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch-size", type=int, default=3)
    ap.add_argument("--probe", action="store_true",
                    help="fire only prompt 01 sequentially as a smoke test")
    ap.add_argument("--only", default="",
                    help="comma-separated prompt numbers to fire (others skipped)")
    ap.add_argument("--resume", action="store_true",
                    help="skip prompts whose output file already exists")
    args = ap.parse_args()

    deck_path = Path(args.deck)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    prompts = parse_deck(deck_path)
    print(f"Parsed {len(prompts)} prompts from {deck_path.name}")

    if args.only:
        wanted = {int(x) for x in args.only.split(",") if x.strip()}
        prompts = [p for p in prompts if p["num"] in wanted]
        print(f"  --only filter -> {len(prompts)} prompts: {[p['num'] for p in prompts]}")

    if args.probe:
        prompts = prompts[:1]
        print(f"  --probe -> firing only prompt {prompts[0]['num']:02d}")

    if args.resume:
        before = len(prompts)
        kept = []
        for p in prompts:
            out_path = out_dir / f"{p['num']:02d}_{p['slug']}.md"
            if out_path.exists() and out_path.stat().st_size > 500:
                print(f"  [resume] skip {p['num']:02d} (exists, {out_path.stat().st_size} bytes)")
                continue
            kept.append(p)
        prompts = kept
        print(f"  --resume -> {len(prompts)}/{before} prompts after skip")

    if not prompts:
        print("Nothing to fire.")
        return 0

    api_key = get_key("GEMINI")
    if not api_key:
        print("ERROR: GEMINI key not found via keys.get_key('GEMINI')")
        return 2

    client = genai.Client(api_key=api_key)

    summary_path = out_dir / "_dispatch_summary.jsonl"
    all_results: list[dict] = []

    if args.probe or args.batch_size <= 1:
        # Sequential
        for p in prompts:
            r = fire_one(client, p, out_dir)
            all_results.append(r)
            with summary_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(r, default=str) + "\n")
    else:
        # Batched parallel
        bs = args.batch_size
        for i in range(0, len(prompts), bs):
            batch = prompts[i:i + bs]
            print(f"\n=== Batch {i // bs + 1}: prompts {[p['num'] for p in batch]} ===")
            with ThreadPoolExecutor(max_workers=bs) as ex:
                futures = {ex.submit(fire_one, client, p, out_dir): p for p in batch}
                for fut in as_completed(futures):
                    p = futures[fut]
                    try:
                        r = fut.result()
                    except Exception as e:
                        traceback.print_exc()
                        r = {"num": p["num"], "slug": p["slug"],
                             "status": "exception", "error": str(e)}
                    all_results.append(r)
                    with summary_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(r, default=str) + "\n")

    # Final tally
    print("\n=== Summary ===")
    by_status: dict[str, int] = {}
    for r in all_results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    for s, n in sorted(by_status.items()):
        print(f"  {s}: {n}")
    print(f"\nSummary log: {summary_path}")
    return 0 if by_status.get("completed", 0) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
