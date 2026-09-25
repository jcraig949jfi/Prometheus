"""Static mechanism-shape fingerprint for generated tools (the 1.0 finding was "~1,960 files
= ~5 mechanisms in costumes": regex dispatch + NCD + meta-confidence). This counts the
costume parts so the 2026 tools can be compared with the 1.0 tools on the same axes.
Read-only. Prints a table for every *.tool.py under runs/ and, with --orig, for the
original code files named in packets/selection.json.
Run: python hephaestus/xpol_2026/shape.py [--orig]
"""
from __future__ import annotations
import ast, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def shape(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"parse": "syntax_error"}
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    imports = sorted({(a.name.split(".")[0]) for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
                     | {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module})
    kw_in_prompt = len(re.findall(r"""['"][A-Za-z ]+['"]\s+in\s+\w*(prompt|text|p|q|question|lower)\w*""", code))
    return {"lines": code.count("\n") + 1, "functions": len(funcs), "regex_calls": len(re.findall(r"\bre\.(?:search|match|findall|finditer|compile|sub|fullmatch)\(", code)),
            "regex_literals": len(re.findall(r"""r['"]""", code)), "keyword_dispatch": kw_in_prompt,
            "uses_zlib_ncd": bool(re.search(r"zlib\.compress", code)), "uses_numpy": "numpy" in imports,
            "uses_primitives": "forge_primitives" in imports, "float_parse": len(re.findall(r"float\(", code)),
            "meta_confidence": bool(re.search(r"_meta_confidence|presuppos|ambigu", code, re.I)),
            "try_except": len([n for n in ast.walk(tree) if isinstance(n, ast.Try)]), "imports": imports}


def main() -> None:
    rows = []
    files = sorted(HERE.glob("runs/*/calls/*/*/*.tool.py"))
    for f in files:
        rel = f.relative_to(HERE).parts
        rows.append({"run": rel[1], "packet": rel[3], "arm": rel[4], "stage": f.name.split(".")[0], **shape(f.read_text(encoding="utf-8", errors="replace"))})
    if "--orig" in sys.argv:
        for p in json.loads((HERE / "packets/selection.json").read_text(encoding="utf-8"))["packets"]:
            oc = p.get("original_code")
            if oc:
                rows.append({"run": "1.0", "packet": p["packet_id"], "arm": "orig", "stage": "-", **shape((ROOT / oc["path"]).read_text(encoding="utf-8", errors="replace"))})
    (HERE / "runs/SHAPES.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    hdr = "run          packet  arm     stage   lines fn  re  relit kwdisp ncd np prim float meta try"
    print(hdr)
    for r in rows:
        if r.get("parse") == "syntax_error":
            print(f"{r['run'][:12]:<12} {r['packet']:<7} {r['arm']:<7} {r['stage']:<7} SYNTAX_ERROR"); continue
        print(f"{r['run'][:12]:<12} {r['packet']:<7} {r['arm']:<7} {r['stage']:<7} {r['lines']:>5} {r['functions']:>3} {r['regex_calls']:>3} {r['regex_literals']:>5} "
              f"{r['keyword_dispatch']:>6} {int(r['uses_zlib_ncd']):>3} {int(r['uses_numpy']):>2} {int(r['uses_primitives']):>4} {r['float_parse']:>5} {int(r['meta_confidence']):>4} {r['try_except']:>3}")


if __name__ == "__main__":
    main()
