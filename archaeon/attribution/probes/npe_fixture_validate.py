"""Archaeon's validation of Nestor's NPE fixture pack (Amendment C5 condition 1) with the INDEPENDENT NPE reference tracer.

- Nestor's fixtures: nestor/s1-forensics-2026-09-23 roles/Nestor/campaigns/ancestry-replay-2026-09-28/tracer/npe_fixtures.py,
  copied verbatim into ops/.../npe_fixture_validation/nestor_npe_fixtures.py.
- The reference tracer: ops/.../npe_reftracer/ref_tracer_npe.py. It asserts equality with the frozen engine on every slice and
  interaction.
- Every per-locus expectation Nestor wrote is checked against the reference's output. Expectations come from Nestor's draft
  semantics; the reference comes from the prereg text alone; the engine decides values.
- A disagreement is either an expectation error or a tracer disagreement. Each is listed for adjudication.
- Interaction-level keys (accepted, budget_ended_b) are not checked here: they need a write-back RNG. They are reported as
  unchecked.
    python -m archaeon.attribution.probes.npe_fixture_validate
"""
import importlib
import os
import sys
import types

ARC = "ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28"
ENGINE = os.path.abspath("roles/Nestor/campaigns/z80atlas-verify-2026-09-22")
KIND = {"E": "ENTITY", "K": "CONST", "X": "CONTEXT", "P": "PREG", "C": "COMPUTED", "F": "COMPUTED_FROM", "M": "MUTATION"}


def load_ref():
    src = open(os.path.join(ARC, "npe_reftracer", "ref_tracer_npe.py"), encoding="utf-8").read()
    old = 'os.path.expanduser(\n    "~/Prometheus-worktrees/npereftr/roles/Nestor/campaigns/z80atlas-verify-2026-09-22")'
    assert old in src
    src = src.replace(old, repr(ENGINE))
    m = types.ModuleType("ref_npe"); sys.modules["ref_npe"] = m
    exec(compile(src, "ref_tracer_npe.py", "exec"), m.__dict__)
    return m


def parse(s):
    p = s.split("|")
    if p[0] == "E": return ("ENTITY", p[1], int(p[2]))
    if p[0] == "X": return ("CONTEXT", p[1])
    if p[0] == "P": return ("PREG", p[1], p[2])
    if p[0] == "K": return ("CONST", p[1])
    return tuple(p)


def norm(lab):
    return lab[:3] if lab[0] == "ENTITY" else lab


def main():
    R = load_ref()
    sys.path.insert(0, os.path.join(ARC, "npe_fixture_validation"))
    NF = importlib.import_module("nestor_npe_fixtures")
    F = NF.fixtures(); n = NF.N
    import json
    add = json.load(open(os.path.join(ARC, "npe_fixture_validation", "ARCHAEON_ADDITIONS.json")))
    for f in F:
        for j, e in add.get(f["name"], {}).items():
            f["expect"].setdefault(int(j), {}).update(e)
    total = passed = 0; issues = []; unchecked = []
    for f in F:
        vside = f.get("vside", 0)
        st_a = (f["regs_a"],) + tuple(f["flags_a"]); st_b = (f["regs_b"],) + tuple(f["flags_b"])
        r = R.trace_interaction(f["ga"], f["gb"], st_a, st_b, budget=f["budget"], ops_mask=f["mask"])
        for j, e in f["expect"].items():
            if not isinstance(j, int): unchecked.append((f["name"], j)); continue
            rec = r["loci"][vside * n + j]; lab = rec["label"]
            def chk(ok, msg):
                nonlocal total, passed
                total += 1
                if ok: passed += 1
                else: issues.append("%s[%d]: %s" % (f["name"], j, msg))
            if "value" in e: chk(rec["post"] == e["value"], "value ref=%r exp=%r" % (rec["post"], e["value"]))
            if "written" in e: chk(rec["written"] == e["written"], "written ref=%r exp=%r" % (rec["written"], e["written"]))
            if "kind" in e: chk(lab[0] == KIND[e["kind"]], "kind ref=%s exp=%s" % (R.fmt_label(lab), e["kind"]))
            if "ent" in e:                       # 'ent' is the entity side for E, the register's side for P (PREG)
                chk(lab[0] in ("ENTITY", "PREG") and lab[1] == e["ent"], "ent ref=%s exp=%s" % (R.fmt_label(lab), e["ent"]))
            if "reg" in e: chk(lab[0] == "PREG" and lab[2] == R.REGN[e["reg"]], "reg ref=%s exp=%s" % (R.fmt_label(lab), e["reg"]))
            if "src" in e: chk(lab[0] == "ENTITY" and lab[2] == e["src"], "src ref=%s exp=%s" % (R.fmt_label(lab), e["src"]))
            for key, field in (("ctrl_has", "ctrl_deps"), ("addr_has", "addr_deps"), ("exec_has", "exec_deps")):
                have = {norm(b) for b in rec[field]}
                for b in e.get(key, []):
                    chk(parse(b) in have, "%s lacks %s (ref %s)" % (field, b, R.fmt_set(rec[field])))
            have = {norm(b) for b in rec["exec_deps"]}
            for b in e.get("exec_lacks", []):
                chk(parse(b) not in have, "exec_deps over-tainted with %s" % b)
            if "performer_ent" in e: chk(rec["performer_entity"] == e["performer_ent"], "performer ref=%s exp=%s" % (rec["performer_entity"], e["performer_ent"]))
    print("NPE fixture pack (Nestor draft) vs independent reference tracer: %d/%d expectations agree over %d fixtures" % (passed, total, len(F)))
    print("unchecked interaction-level keys:", unchecked)
    for x in issues: print("  ISSUE", x)
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
