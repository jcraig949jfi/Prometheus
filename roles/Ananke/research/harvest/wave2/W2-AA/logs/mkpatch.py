import pathlib, sys
p=pathlib.Path(sys.argv[1]); s=p.read_text(encoding='utf-8')
def rep(a,b):
    global s
    assert s.count(a)==1, a
    s=s.replace(a,b)
rep('''If the delimiters are missing, the whole message is deposited and flagged
"undelimited".
"""''','''If the delimiters are missing, the whole message is deposited and flagged
"undelimited".

Advisory kind audit (W2-AA): after REPORT.md is written, tools/kind_audit.py is run on the
deposited block and its flags (C1 cell ids cited with search-outcome language when the row is
not kind=evolve) are recorded under "kind_audit" in the provenance JSON. It never blocks a
deposit and never changes REPORT.md; if it cannot run, "status" is "NOT_VERIFIED" with the error.
"""''')
rep('''import hashlib
import json
import pathlib
''','''import hashlib
import importlib.util
import json
import pathlib
''')
rep('''BEGIN, END = "===BEGIN REPORT===", "===END REPORT==="
''','''BEGIN, END = "===BEGIN REPORT===", "===END REPORT==="
KIND_AUDIT = pathlib.Path(__file__).resolve().parent / "tools" / "kind_audit.py"


def kind_audit(block: str) -> dict:
    """Advisory flags for the deposited block. Never raises: a failure is recorded, not hidden."""
    try:
        spec = importlib.util.spec_from_file_location("ananke_kind_audit", KIND_AUDIT)
        ka = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ka)
        idx = ka.load_index()
        s = ka.summary(ka.audit_text(block, "REPORT.md", idx), idx)
        for f in s["flags"]:
            f["line"] += 1  # REPORT.md = one provenance header line + the block
        return {"status": "ok", **s}
    except Exception as e:  # noqa: BLE001 -- advisory only; the deposit must not depend on it
        return {"status": "NOT_VERIFIED", "error": f"{type(e).__name__}: {e}"[:300]}
''')
rep(r'''    target.write_text(header + block + "\n", encoding="utf-8", newline="\n")
''',r'''    target.write_text(header + block + "\n", encoding="utf-8", newline="\n")
    prov["kind_audit"] = kind_audit(block)
''')
rep('''    print(p, "verified" if verify(p) else "HASH MISMATCH")''','''    print(p, "verified" if verify(p) else "HASH MISMATCH")
    ka = json.loads(p.with_name(p.stem + ".provenance.json").read_text()).get("kind_audit", {})
    print("kind_audit:", ka.get("status"), ka.get("counts", ka.get("error", "")))''')
p.write_text(s,encoding='utf-8',newline='\n')
