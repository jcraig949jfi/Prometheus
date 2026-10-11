"""Copy a generator's latest reply VERBATIM from its transcript (JSONL) into proposals/<arm>/<idx>.py (code block)
and <idx>.md (full reply text). Prints only sha256 and sizes, so Cosmos never retypes or edits a proposal.

    python -m prometheus.cosmos.ns01.extract <transcript.jsonl> <out_dir> <idx> [n_seen_replies]
"""
import hashlib
import json
import re
import sys
from pathlib import Path


def replies(path):
    out = []
    for line in Path(path).read_text().splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        m = r.get("message")
        if r.get("type") != "assistant" or not isinstance(m, dict):
            continue
        txt = "".join(b.get("text", "") for b in m.get("content", []) if isinstance(b, dict) and b.get("type") == "text")
        if txt.strip():
            out.append(txt)
    return out


def main(path, out_dir, idx, seen=None):
    rs = replies(path)
    seen = len(rs) - 1 if seen is None else int(seen)
    if len(rs) <= seen:
        print(json.dumps({"error": f"only {len(rs)} replies"}))
        return 1
    txt = rs[seen]
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", txt, re.S)
    code = max(blocks, key=len) if blocks else ""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{int(idx):02d}.md").write_text(txt)
    (out / f"{int(idx):02d}.py").write_text(code)
    print(json.dumps({"idx": int(idx), "reply_index": seen, "n_replies": len(rs), "code_lines": code.count("\n"),
                      "sha256": hashlib.sha256(code.encode()).hexdigest()[:16], "reply_chars": len(txt)}))
    return 0


if __name__ == "__main__":
    a = sys.argv
    sys.exit(main(a[1], a[2], a[3], a[4] if len(a) > 4 else None))
