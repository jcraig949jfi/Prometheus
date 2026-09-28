"""Run the NPE fixture pack (npe_fixtures.py) through the shadow tracer and check every expectation; also the
world-level fixtures (K9/K28/K18) on the frozen Runner via observe.Observed; and MUTANT TRACERS, each of which must fail
at least one fixture (v4 s4.4 mutation testing, the subset meaningful for Z8 under mask 0x0C).

    python check_fixtures.py [--write]   -> FIXTURES_RESULT.json
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import interventions as I                                     # noqa: E402
import npe_fixtures as NF                                      # noqa: E402
import observe as O                                            # noqa: E402
import z8shadow as S                                           # noqa: E402


def pre_of(f):
    p = I.Pre()
    p.n, p.size, p.budget, p.mask, p.vside = NF.N, 2 * NF.N, f["budget"], f["mask"], f.get("vside", 0)
    p.g = {0: bytearray(f["ga"]), 1: bytearray(f["gb"])}
    p.regs = {0: None if f["regs_a"] is None else list(f["regs_a"]), 1: None if f["regs_b"] is None else list(f["regs_b"])}
    p.flags = {0: tuple(f["flags_a"]), 1: tuple(f["flags_b"])}
    return p


def s_base(b):
    return O.enc_base(b)


def view(run: I.Run, j, mutant=None):
    """What a tracer reports for victim locus j: (value, data label, ctrl, addr, exec, performer) -- optionally
    transformed by a mutant tracer."""
    st = run.last.get(run.voff + j)
    dl, ad = run.cell(j)
    ctrl = set(st.ctrl) if st else set()
    exe = set(st.exec_) if st else set()
    addr = set(ad)
    perf = st.performer if st else None
    if mutant:
        dl, ctrl, addr, exe, perf = mutant(run, j, dl, ctrl, addr, exe, perf)
    return run.victim[j], dl, ctrl, addr, exe, perf


def check_one(f, mutant=None):
    run = I.Run(pre_of(f))
    fails = []
    for j, e in f["expect"].items():
        v, dl, ctrl, addr, exe, perf = view(run, j, mutant)
        written = run.written(j)
        def bad(msg):
            fails.append("%s[%d]: %s" % (f["name"], j, msg))
        if "value" in e and v != e["value"]:
            bad("value %r != %r" % (v, e["value"]))
        if "written" in e and written != e["written"]:
            bad("written %r != %r" % (written, e["written"]))
        if "kind" in e and dl[0] != e["kind"]:
            bad("kind %r != %r" % (dl[0], e["kind"]))
        if "ent" in e and (len(dl) < 2 or dl[1] != e["ent"]):
            bad("ent %r != %r" % (dl[1] if len(dl) > 1 else None, e["ent"]))
        if "src" in e and (dl[0] != "E" or dl[2] != e["src"]):
            bad("src %r != %r" % (dl[2] if dl[0] == "E" else None, e["src"]))
        if "reg" in e and (dl[0] != "P" or dl[2] != e["reg"]):
            bad("reg label %r" % (dl,))
        if "op" in e and (dl[0] != "X" or dl[1] != e["op"]):
            bad("context %r" % (dl,))
        if "performer_ent" in e and (perf is None or perf[0] != "E" or perf[1] != e["performer_ent"]):
            bad("performer %r" % (perf,))
        if "store_by" in e:
            st_ = run.last.get(run.voff + j)
            if st_ is None or ("a" if st_.side == 0 else "b") != e["store_by"]:
                bad("store_by %r" % (None if st_ is None else st_.side,))
        for key, got in (("ctrl_has", ctrl), ("addr_has", addr), ("exec_has", exe)):
            for want in e.get(key, []):
                if want not in {s_base(b) for b in got}:
                    bad("%s lacks %s" % (key, want))
        for want in e.get("exec_lacks", []):
            if want in {s_base(b) for b in exe}:
                bad("exec has %s" % want)
        if "has_bases" in e:
            got = {s_base(b) for b in S.base(dl)}
            for want in e["has_bases"]:
                if want not in got:
                    bad("label bases lack %s" % want)
        if "not_label" in e and dl[0] == "E" and "E|%s|%d" % (dl[1], dl[2]) == e["not_label"]:
            bad("labelled %s (forbidden)" % e["not_label"])
    if "accepted" in f and run.accepted != f["accepted"]:
        fails.append("%s: accepted %r != %r" % (f["name"], run.accepted, f["accepted"]))
    return fails


# ---------------------------------------------------------------- mutant tracers (post-hoc transforms of the report)
def m_loc0(run, j, dl, c, a, e, p):
    return (dl[:2] + (0,) + dl[3:] if dl[0] == "E" else dl), c, a, e, p


def m_reverse(run, j, dl, c, a, e, p):
    return (dl[:2] + (NF.N - 1 - dl[2],) + dl[3:] if dl[0] == "E" else dl), c, a, e, p


def m_positional(run, j, dl, c, a, e, p):
    return (dl[:2] + (j,) + dl[3:] if dl[0] == "E" else dl), c, a, e, p


def m_ptrlabel(run, j, dl, c, a, e, p):
    """data label = the store pointer's label instead of the value's."""
    st = run.last.get(run.voff + j)
    if st is None:
        return dl, c, a, e, p
    ptr = sorted(b for b in st.cell[1] if b[0] == "E")
    return (("E", ptr[0][1], ptr[0][2], None) if ptr else ("K", "ptr")), c, a, e, p


def m_noexec(run, j, dl, c, a, e, p):
    return dl, c, a, set(), p


def m_exec_all(run, j, dl, c, a, e, p):
    return dl, c, a, {("E", s, i) for s in ("a", "b") for i in range(NF.N)}, p


def m_noctrl(run, j, dl, c, a, e, p):
    return dl, set(), a, e, p


def m_implicit_move(run, j, dl, c, a, e, p):
    """control-flow or computed recreation relabelled as a MOVE of an entity byte it depends on."""
    if dl[0] in ("C", "F", "K"):
        src = sorted(b for b in (set(S.base(dl)) | set(c)) if b[0] == "E")
        if src:
            return ("E", src[0][1], src[0][2], None), c, a, e, p
    return dl, c, a, e, p


def m_value_alignment(run, j, dl, c, a, e, p):
    """label by value match: the first byte of the pre-state equal to the final value."""
    v = run.victim[j]
    pre = run.pre
    for s, ent in ((1, "b"), (0, "a")):
        g = pre.g[s]
        for i in range(len(g)):
            if g[i] == v:
                return ("E", ent, i, None), c, a, e, p
    return dl, c, a, e, p


def m_noperformer_material(run, j, dl, c, a, e, p):
    """performer by LOCATION (which half the storing pc is in) instead of by material."""
    st = run.last.get(run.voff + j)
    if st is None:
        return dl, c, a, e, p
    ent = "a" if st.pc < NF.N else "b"
    return dl, c, a, e, ("E", ent, 0, None)


MUTANTS = {"loc0": m_loc0, "reverse": m_reverse, "positional": m_positional, "ptrlabel": m_ptrlabel,
           "noexec": m_noexec, "exec_all": m_exec_all, "noctrl": m_noctrl, "implicit_move": m_implicit_move,
           "value_alignment": m_value_alignment, "performer_by_location": m_noperformer_material}


# ---------------------------------------------------------------- world-level fixtures on the real Runner
def world_fixtures():
    """K9/K28/K18: drive one pair through the REAL world code path (Runner._pair_interact) with a raised mutation
    rate on a fixture instance, and check: every changed or redrawn opcode position carries MUTATION at its draw; the
    shadow agreed with the world's values (Observed asserts it); order = slices, then half a mutated, then half b."""
    import pin_reproduce as P  # noqa: F401  (path setup)
    job = P.job_list(O.Z, P.REPO / P.PATHS[2])[0]
    kw = dict(job["kwargs"]); kw.pop("implant_source", None); hx = kw.pop("implant_hex", None)
    if hx:
        kw["implant_bytes"] = bytes.fromhex(hx)
    got = {}

    def sink(runner, iid, pre_oid, orgs, gs, regs, flags, sh, last_store, post, births, n):
        if "post" not in got:                                 # the first interaction of the epoch
            got["post"], got["muts"], got["sh"] = post, list(runner._muts), sh

    r = O.Observed(job["cell"], job["seed"], tier=job["tier"], sink=sink, max_epochs=1, **kw)
    r.mut_rate = 0.5                                          # fixture instance only: force mutations
    r.run()
    res = {}
    ok_draw = True
    n_ev = 0
    for side in (0, 1):
        final, new, events = got["post"][side]
        pre_mut = got["muts"][side][0]
        for ev in events:
            n_ev += 1
            dl = final[ev["pos"]][0]
            ok_draw &= dl[0] == "M" and dl[1][1] == side and dl[1][2] == ev["call"]
        for j in range(len(new)):
            if new[j] != pre_mut[j]:
                ok_draw &= final[j][0][0] == "M"                 # every changed byte is a labelled mutation
    res["K9_K28_mutation_at_draw"] = bool(ok_draw and n_ev > 0)
    res["K18_order_two_writebacks_a_then_b"] = len(got["muts"]) == 2
    res["world_value_identity"] = r.shadow_checked > 0
    return res


def merged_fixtures():
    """Nestor's pack + Archaeon's adversarial expectations (Amendment C7.5; vendored copy ARCHAEON_ADDITIONS.json with
    its provenance). Lists are unioned, scalars must not conflict with Nestor's own expectation."""
    fx = NF.fixtures()
    add = json.loads((HERE / "ARCHAEON_ADDITIONS.json").read_text(encoding="utf-8"))
    by = {f["name"]: f for f in fx}
    n = 0
    for name, loci in add.items():
        if name == "note":
            continue
        f = by[name]
        for j, e in loci.items():
            cur = f["expect"].setdefault(int(j), {})
            for k, v in e.items():
                n += 1
                if isinstance(v, list):
                    cur[k] = sorted(set(cur.get(k, [])) | set(v))
                elif k in cur and cur[k] != v:
                    raise ValueError("Archaeon addition conflicts with Nestor's expectation: %s[%s].%s" % (name, j, k))
                else:
                    cur[k] = v
    return fx, n


def main():
    fx, n_add = merged_fixtures()
    real = {f["name"]: check_one(f) for f in fx}
    mutants = {}
    for name, m in MUTANTS.items():
        caught = [f["name"] for f in fx if check_one(f, m)]
        mutants[name] = caught
    world = world_fixtures()
    res = {"fixtures": len(fx), "archaeon_additions_merged": n_add, "real_tracer_failures": {k: v for k, v in real.items() if v},
           "real_tracer_pass": all(not v for v in real.values()),
           "mutants_caught_by": mutants, "all_mutants_caught": all(mutants.values()),
           "world": world, "world_pass": all(world.values()),
           "inapplicable": NF.INAPPLICABLE, "world_level": NF.WORLD_LEVEL}
    res["pass"] = res["real_tracer_pass"] and res["all_mutants_caught"] and res["world_pass"]
    txt = json.dumps(res, indent=1, sort_keys=True)
    if "--write" in sys.argv:
        (HERE / "FIXTURES_RESULT.json").write_text(txt + "\n", encoding="utf-8")
    print(txt)
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parent / "pin"))
    sys.exit(main())
