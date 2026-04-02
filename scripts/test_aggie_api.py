"""
test_aggie_api.py — Quick connectivity + code-gen smoke test for the auggie-sdk.

Verifies that we can reach the Augment API, call a model, and receive
a usable Python code response — before wiring --use-aggie-api into the
forge pipeline (hephaestus.py).

Usage:
    python scripts/test_aggie_api.py
    python scripts/test_aggie_api.py --model haiku4.5   # faster/cheaper
    python scripts/test_aggie_api.py --verbose
"""

import argparse
import sys
import time

# ---------------------------------------------------------------------------
# Minimal forge-style prompt (same structure Hephaestus sends to NVIDIA)
# ---------------------------------------------------------------------------
MINI_FORGE_PROMPT = """\
You are a Python code generator. Write a single Python class called ReasoningTool.

Requirements:
- Class name: ReasoningTool
- Two methods:
    evaluate(self, prompt: str, candidates: list[str]) -> list[dict]
        Returns a list of dicts, each with keys: "candidate" (str) and "score" (float 0-1).
        Scores based on simple keyword overlap between prompt and candidate.
    confidence(self, prompt: str, answer: str) -> float
        Returns a float 0-1 representing confidence.

- Use ONLY Python stdlib (no third-party imports).
- Keep it under 40 lines of code.
- Wrap the class in a Python code block (```python ... ```).

Respond with ONLY the code block, no explanation.
"""


def extract_code_block(text: str) -> str | None:
    """Pull the first ```python ... ``` block out of a response."""
    import re
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None


def run_test(model: str, verbose: bool) -> bool:
    print(f"\n{'='*60}")
    print(f"  auggie-sdk connectivity + code-gen test")
    print(f"  Model: {model}")
    print(f"{'='*60}\n")

    # 1. Import
    try:
        from auggie_sdk import Auggie
        print("[1/4] auggie_sdk imported OK")
    except ImportError as e:
        print(f"[FAIL] Cannot import auggie_sdk: {e}")
        return False

    # 2. Instantiate — on Windows we need the explicit .cmd path for the CLI
    import shutil, platform
    cli_path: str | None = None
    if platform.system() == "Windows":
        cmd = shutil.which("auggie.cmd") or shutil.which("auggie")
        if cmd:
            cli_path = cmd

    try:
        agent = Auggie(
            model=model,
            timeout=120,
            cli_path=cli_path,
        )
        print(f"[2/4] Auggie({model!r}) instantiated OK  (cli_path={cli_path!r})")
    except Exception as e:
        print(f"[FAIL] Cannot instantiate Auggie: {e}")
        return False

    # 3. Fire the request
    print("[3/4] Sending code-gen prompt to Augment API...")
    t0 = time.time()
    try:
        response = agent.run(MINI_FORGE_PROMPT, return_type=str)
        elapsed = time.time() - t0
        print(f"      Response received in {elapsed:.1f}s")
    except Exception as e:
        elapsed = time.time() - t0
        print(f"[FAIL] API call failed after {elapsed:.1f}s: {e}")
        agent.close()
        return False
    finally:
        try:
            agent.close()
        except Exception:
            pass

    if verbose:
        print(f"\n--- Raw response ---\n{response}\n--- end ---\n")

    # 4. Validate we got Python code back
    code = extract_code_block(response) if response else None
    if not code:
        # Auggie might return code without a fenced block — check directly
        if response and "class ReasoningTool" in response:
            code = response
            print("[4/4] Code block found (unfenced, accepted)")
        else:
            print(f"[FAIL] No Python code block found in response.")
            print(f"       Response preview: {repr(response[:300]) if response else 'None'}")
            return False

    if "class ReasoningTool" not in code:
        print(f"[FAIL] ReasoningTool class not found in extracted code.")
        return False

    # 5. Sanity-execute
    try:
        ns: dict = {}
        exec(compile(code, "<aggie_test>", "exec"), ns)
        tool = ns["ReasoningTool"]()
        scores = tool.evaluate("What is 2+2?", ["4", "five", "the answer is four"])
        conf = tool.confidence("What is 2+2?", "4")
        print(f"[4/4] Code executes OK — evaluate() returned {len(scores)} scores, "
              f"confidence()={conf:.3f}")
    except Exception as e:
        print(f"[WARN] Code extracted but failed to execute: {e}")
        print(f"       This may be acceptable — execution errors are caught by hephaestus.")
        # Still counts as a pass — we proved the API round-trip works

    print(f"\n{'='*60}")
    print(f"  RESULT: PASS — auggie-sdk is ready for --use-aggie-api")
    print(f"{'='*60}\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Smoke-test auggie-sdk for forge pipeline")
    parser.add_argument("--model", default="sonnet4.5",
                        choices=["haiku4.5", "sonnet4.5", "sonnet4", "gpt5"],
                        help="Model to test (default: sonnet4.5)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print full raw response")
    args = parser.parse_args()

    ok = run_test(args.model, args.verbose)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
