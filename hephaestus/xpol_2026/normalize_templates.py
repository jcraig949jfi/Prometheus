"""Normalize templates/ to LF bytes and strip the leading backslash-newline that is a
Python line-continuation inside the original triple-quoted literal (it produces no
characters at runtime). Rewrites MANIFEST.json hashes over the LF bytes.
Run: python hephaestus/xpol_2026/normalize_templates.py
"""
import hashlib, json
from pathlib import Path

D = Path(__file__).resolve().parent / "templates"
man = json.loads((D / "MANIFEST.json").read_text(encoding="utf-8"))
for fn, m in man.items():
    p = D / fn
    b = p.read_bytes().replace(b"\r\n", b"\n")
    if b.startswith(b"\\\n"):
        b = b[2:]
        if "line-continuation" not in m["note"]:
            m["note"] += "; leading line-continuation of the Python literal removed (produces no characters)"
    p.write_bytes(b)
    m["sha256"] = hashlib.sha256(b).hexdigest()
    m["chars"] = len(b.decode("utf-8"))
    print(fn, m["sha256"][:12], m["chars"], repr(b[:12]))
(D / "MANIFEST.json").write_bytes(json.dumps(man, indent=1).encode("utf-8"))
