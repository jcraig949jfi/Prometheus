"""Extract the answer text from a Deep Research interaction dump.

The dispatcher persists the whole `client.interactions` object (steps, config,
usage, tools). Every downstream consumer wants one thing: the model_output text.
Without this, each consumer re-implements JSON spelunking -- and the 442-report
back-corpus stays unread because reading it is annoying.

Usage:
    python engine/sdk/dr_extract.py <report.md> [...]        # print answer
    python engine/sdk/dr_extract.py --dir <batch_dir>        # extract all -> *_answer.md
"""
import json
import sys
from pathlib import Path


def extract(path: Path) -> str | None:
    """Return the final model_output text, or None if the dump has no answer."""
    text = path.read_text(encoding="utf-8", errors="replace")
    brace = text.find("{")
    if brace < 0:
        return None
    try:
        obj = json.loads(text[brace:])
    except json.JSONDecodeError:
        return None
    parts = []
    for step in obj.get("steps", []):
        if step.get("type") == "user_input":
            continue
        content = step.get("content")
        if isinstance(content, list):
            for chunk in content:
                if isinstance(chunk, dict) and chunk.get("text"):
                    parts.append(chunk["text"])
    return "\n\n".join(parts) or None


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--dir":
        batch = Path(argv[1])
        wrote = 0
        for report in sorted(batch.glob("*.md")):
            if report.name.endswith("_answer.md"):
                continue
            answer = extract(report)
            if answer:
                out = report.with_name(report.stem + "_answer.md")
                out.write_text(answer, encoding="utf-8")
                wrote += 1
                print(f"{out.name}  ({len(answer):,} chars)")
            else:
                print(f"SKIP (no answer found): {report.name}")
        print(f"\nextracted {wrote}")
        return 0
    for arg in argv:
        answer = extract(Path(arg))
        print(answer if answer else f"(no answer found in {arg})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
