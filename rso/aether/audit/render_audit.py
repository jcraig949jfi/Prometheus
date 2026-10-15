"""Render AUDIT.md from TABLES.json (written by `replay_audit aggregate`) and the AUDIT_TEMPLATE.md prose.
    python -B -m rso.aether.audit.render_audit
The per-unit table is the only generated part; the prose is committed in AUDIT_TEMPLATE.md."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    t = json.load(open(os.path.join(HERE, "TABLES.json"), encoding="utf-8"))
    rows = []
    for u in t["units"]:
        if u["status"] == "PRIOR_FULL_REPLAY":
            rows.append("| %s | %s | %s | (prior full replay, not re-run) | MATCH (prior) | %s | %s |" % (
                u["law"], u["seed"], u["committed_arrays_sha256"][:12], u["committed_class"], u["replayed_class"]))
        else:
            ce = u["clamp_equal"]
            ok = u["match"] and ce["ftick_cutB"] and ce["ftick_cutN"]
            rows.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                u["law"], u["seed"], u["committed_arrays_sha256"][:12], u["replayed_arrays_sha256"][:12],
                "MATCH" if ok else "MISMATCH", u["committed_class"], u["replayed_class"]))
    tpl = open(os.path.join(HERE, "AUDIT_TEMPLATE.md"), encoding="utf-8").read()
    out = tpl.replace("@@UNIT_ROWS@@", "\n".join(rows))
    with open(os.path.join(HERE, "AUDIT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("rows", len(rows), "MISMATCH", sum(1 for r in rows if "MISMATCH" in r))


if __name__ == "__main__":
    main()
