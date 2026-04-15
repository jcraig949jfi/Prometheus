"""
Aporia — Math Problem Solver Battery

Feeds each open math question to an LLM and asks it to:
1. Classify: known-solved / partially-solved / open / open-but-approachable
2. Attempt a solution sketch or proof outline
3. Rate confidence (0-10)
4. Identify key references or approaches

Usage:
    python scripts/solve_battery.py                     # all problems
    python scripts/solve_battery.py --limit 10          # first 10
    python scripts/solve_battery.py --start 100 --limit 20  # problems 100-119
    python scripts/solve_battery.py --dry-run           # preview prompts
    python scripts/solve_battery.py --model deepseek    # model choice

Results saved to aporia/mathematics/solutions.jsonl (append mode).
"""

import argparse, json, os, pathlib, sys, time, traceback

# Add repo root for keys.py
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))
from keys import get_key

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATH_JSONL = ROOT / "mathematics" / "questions.jsonl"
SOLUTIONS_JSONL = ROOT / "mathematics" / "solutions.jsonl"

# ── LLM client (Nous-style with backoff) ─────────────────────────────

def call_llm(system_prompt, user_prompt, model="deepseek", max_retries=5,
             temperature=0.3, max_tokens=4096):
    """Call an LLM with exponential backoff on rate limits."""
    from openai import OpenAI

    CONFIGS = {
        "deepseek": ("https://api.deepseek.com", "DEEPSEEK", "deepseek-chat"),
        "openai":   ("https://api.openai.com/v1", "OPENAI", "gpt-4.1"),
        "nvidia":   ("https://integrate.api.nvidia.com/v1", "NVIDIA", "nvidia/llama-3.3-nemotron-super-49b-v1"),
        "gemini":   ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI", "gemini-2.5-flash"),
    }
    base_url, key_name, model_id = CONFIGS[model]
    cfg = {"base_url": base_url, "api_key": get_key(key_name), "model": model_id}
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"], timeout=120.0)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=cfg["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            }
            return text, usage
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                wait = 2 ** (attempt + 1)
                print(f"    [429] Rate limited, waiting {wait}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            elif attempt < max_retries - 1:
                print(f"    [ERR] {err[:100]}, retrying...")
                time.sleep(2)
            else:
                print(f"    [FAIL] {err[:200]}")
                return None, None
    return None, None


# ── Prompt template ──────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a research mathematician evaluating open problems.
For each problem, provide a structured analysis. Be rigorous and honest — if a problem
is genuinely open and hard, say so. If you believe progress has been made that isn't
reflected in the problem status, note it.

Respond in this EXACT JSON format (no markdown, no code blocks, just raw JSON):
{
  "classification": "one of: solved | partially_solved | open_approachable | open_hard | open_unknown",
  "confidence": 0-10,
  "status_note": "Brief note on current status — has this been solved recently? Partially resolved?",
  "approach_sketch": "Key mathematical approach or proof strategy, 2-5 sentences",
  "key_techniques": ["list", "of", "relevant", "techniques"],
  "key_references": ["Author Year - brief description"],
  "connections": "Connections to other problems or areas of mathematics",
  "assessment": "Your honest assessment: is this solvable in the next 10 years? Why or why not?"
}"""

def build_user_prompt(q):
    parts = [
        f"PROBLEM: {q['title']}",
        f"DOMAIN: {q['subdomain']}",
        f"STATEMENT: {q['statement']}",
    ]
    if q.get("posed_by"):
        parts.append(f"POSED BY: {q['posed_by']}")
    if q.get("year_posed"):
        parts.append(f"YEAR: {q['year_posed']}")
    if q.get("notes"):
        parts.append(f"NOTES: {q['notes']}")
    return "\n".join(parts)


# ── Parse response ───────────────────────────────────────────────────

def parse_response(text):
    """Try to parse JSON from LLM response, handling common issues."""
    if not text:
        return None
    # Strip markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # skip ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {"raw_response": text[:2000], "parse_error": True}


# ── Main loop ────────────────────────────────────────────────────────

def load_already_solved():
    """Load IDs already in solutions.jsonl to skip them."""
    done = set()
    if SOLUTIONS_JSONL.exists():
        with open(SOLUTIONS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        done.add(entry.get("id", ""))
                    except json.JSONDecodeError:
                        pass
    return done


def main():
    parser = argparse.ArgumentParser(description="Aporia math solver battery")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--model", default="nvidia", choices=["deepseek", "openai", "nvidia", "gemini"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between calls")
    args = parser.parse_args()

    # Load questions
    questions = []
    with open(MATH_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    # Skip already solved
    done = load_already_solved()
    questions = [q for q in questions if q["id"] not in done]

    # Apply start/limit
    questions = questions[args.start:]
    if args.limit:
        questions = questions[:args.limit]

    print(f"{'='*60}")
    print(f"  APORIA SOLVER BATTERY")
    print(f"  Model: {args.model}")
    print(f"  Questions: {len(questions)}")
    print(f"  Already solved: {len(done)}")
    print(f"{'='*60}\n")

    if args.dry_run:
        for q in questions[:5]:
            print(f"  [{q['id']}] {q['title']}")
            print(f"    prompt: {build_user_prompt(q)[:200]}...")
            print()
        print(f"  [DRY RUN] Would process {len(questions)} questions")
        return

    solved_count = 0
    partial_count = 0
    approachable_count = 0

    with open(SOLUTIONS_JSONL, "a", encoding="utf-8") as out:
        for i, q in enumerate(questions):
            qid = q["id"]
            title = q["title"]
            print(f"  [{i+1}/{len(questions)}] {qid}: {title}")

            user_prompt = build_user_prompt(q)
            t0 = time.time()
            text, usage = call_llm(SYSTEM_PROMPT, user_prompt, model=args.model)
            elapsed = time.time() - t0

            if text is None:
                print(f"    -> FAILED ({elapsed:.1f}s)")
                continue

            parsed = parse_response(text)
            if parsed is None:
                print(f"    -> PARSE FAILED ({elapsed:.1f}s)")
                continue

            classification = parsed.get("classification", "unknown")
            confidence = parsed.get("confidence", 0)

            result = {
                "id": qid,
                "title": title,
                "model": args.model,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "elapsed_s": round(elapsed, 1),
                "usage": usage,
                "result": parsed,
            }
            out.write(json.dumps(result, ensure_ascii=False) + "\n")
            out.flush()

            # Stats
            if classification == "solved":
                solved_count += 1
                marker = "SOLVED!"
            elif classification == "partially_solved":
                partial_count += 1
                marker = "PARTIAL"
            elif classification == "open_approachable":
                approachable_count += 1
                marker = "APPROACHABLE"
            else:
                marker = classification.upper()

            print(f"    -> {marker} (confidence {confidence}/10, {elapsed:.1f}s)")

            if args.delay > 0:
                time.sleep(args.delay)

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"  Solved:       {solved_count}")
    print(f"  Partial:      {partial_count}")
    print(f"  Approachable: {approachable_count}")
    print(f"  Total:        {len(questions)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
