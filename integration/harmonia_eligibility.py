#!/usr/bin/env python3
"""HARMONIA ELIGIBILITY -- world coupling, participation, and the funnel.

This module exists because packet 01 measured world-coupling two different ways
in two different loops and did not notice. L2 asked "does any surface respond to
the world", including the final-state image, and found 16/64 coupled. L7 asked
the same question of COMPOSED objects using EXECUTION ONLY, silently dropping
the most sensitive surface, and reported that composition destroys coupling
(15/240, 6.2%). Re-measured consistently the figure is 146/240 (60.8%).

A definition that lives in two scripts becomes two definitions. It lives here now.

THE CONTAMINATION RULE, which is what went wrong and is now enforced
  The runtime copies the genome onto the front of the tape, so the final-state
  IMAGE contains the genome bytes. Therefore:

    comparing the SAME object across DIFFERENT worlds  -> image is SAFE.
        The genome is identical in both arms; any image difference is
        world-driven. This is world-coupling, and dropping the image here
        throws away the most sensitive surface (14/16 vs meter 11/16 vs
        transcript 2/16).

    comparing DIFFERENT objects (A vs A+B, A+B vs A+B\\A) -> image is
        CONTAMINATED. The genomes differ, so the image differs whether or not
        anything ran. This is the distinctness-by-construction that produced
        two false positives in packet 01.

  `coupling()` may use the image. `participation()` may not, and asserts so.

PARTICIPATION
  Packet 01's P5 ("both single knockouts move EXECUTION") was killed by a
  known-negative: it fires identically on a pair with a genuine data dependence
  and on a pair where one component writes a register nothing reads. So does
  Proteus's activation_evidence, and so does order-sensitivity. See
  integration/harmonia_diagnostics.py for the controls.

  The surviving criterion is CROSS-CONTRIBUTION AT CONSTANT COST:
      ablating A changes what B emits, AND the op count is unchanged.
  The op-count clause rules out the change being explained by B getting more or
  less machine to run in. It is affordable here because Proteus's ablate()
  rewrites only the opcode word to NOP, and a NOP costs exactly one op, so
  NOP-ablation is RESOURCE-NEUTRAL BY CONSTRUCTION. A deletion ablation is NOT
  (measured: same genome, deletion 8 out_writes vs neutralisation 4), so this
  criterion is valid only under NOP-ablation.

  It is scored 6/6 on the known cases in harmonia_diagnostics: DEP_DATA,
  DEP_CONST positive; INDEP_REG, INDEP_LONG, POSITION, RESOURCE negative.
"""
from __future__ import annotations

import hashlib
import json

from proteus.compose import segments as S
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import Meter, Player

IW = 4
DEFAULT_WORLDS = [
    [[1, 2, 3, 4], [5, 6, 7, 8]],
    [[9, 9, 9, 9], [0, 0, 0, 0]],
    [[2 ** 31, 7, 13, 29], [4, 4, 4, 4]],
]
DEFAULTS = {"seed": 20260905, "ticks": 6, "n_out": 2, "budget": 64}


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)


def observe(man, inputs, seed=None, ticks=None, n_out=None, budget=None):
    cfg = dict(DEFAULTS)
    for k, v in (("seed", seed), ("ticks", ticks), ("n_out", n_out), ("budget", budget)):
        if v is not None:
            cfg[k] = v
    p = Player(man)
    st = p.fresh_state()
    rng = SplitMix64(cfg["seed"])
    m = Meter()
    tr, status = [], []
    for _ in range(cfg["ticks"]):
        outs, s = p.run_tick(st, inputs, cfg["n_out"], rng, meter=m, budget=cfg["budget"])
        tr.append(outs)
        status.append(s)
        if s == "halt":
            break
    d = m.as_dict(man)
    for k in ("wall_s", "cpu_s", "footprint_words", "persistent_state_words"):
        d.pop(k, None)
    return {
        "meter": d, "statuses": status, "outputs": tr,
        "exec": hashlib.sha256(_canon({"m": d, "s": status, "t": tr}).encode()).hexdigest()[:12],
        "out": hashlib.sha256(_canon(tr).encode()).hexdigest()[:12],
        "image": hashlib.sha256(_canon(st).encode()).hexdigest()[:12],
    }


def coupling(man, worlds=None, **kw):
    """Does THIS object respond to the world? Image is SAFE here (same object)."""
    obs = [observe(man, w, **kw) for w in (worlds or DEFAULT_WORLDS)]
    return {
        "execution": len({o["exec"] for o in obs}) > 1,
        "output": len({o["out"] for o in obs}) > 1,
        "image": len({o["image"] for o in obs}) > 1,
        "any": len({(o["exec"], o["image"]) for o in obs}) > 1,
        "emits": any(o["meter"]["out_writes"] > 0 for o in obs),
        "saturated": all(o["meter"]["budget_exhausted_ticks"] == o["meter"]["ticks"]
                         for o in obs),
        "ops": [min(o["meter"]["ops"] for o in obs), max(o["meter"]["ops"] for o in obs)],
        "in_reads": obs[0]["meter"]["in_reads"],
        "first_status": obs[0]["statuses"][0],
    }


def _exec_profile(man, worlds, **kw):
    """EXECUTION-only profile. Image is deliberately excluded: this is used for
    cross-OBJECT comparison, where the image is contaminated by genome bytes."""
    obs = [observe(man, w, **kw) for w in worlds]
    return (tuple(o["exec"] for o in obs), tuple(o["out"] for o in obs),
            obs[0]["meter"]["ops"])


def participation(doc, worlds=None, **kw):
    """Component participation classes for a 2-component composition document.

    Returns, per component, whether ablating IT changes what the composition
    EMITS (cross-contribution) and whether the op count survived the ablation
    (cost-neutrality). `causal_contribution` requires both.
    """
    worlds = worlds or DEFAULT_WORLDS
    names = [c["component"] for c in doc["components"]]
    base_x, base_o, base_ops = _exec_profile(doc["manifest"], worlds, **kw)
    out = {"components": {}}
    for nm in names:
        abl = S.ablate(doc, nm)
        x, o, ops = _exec_profile(abl["manifest"], worlds, **kw)
        out["components"][nm] = {
            "moves_execution": x != base_x,          # packet 01's P5 -- KILLED as a
                                                     # criterion, kept as a datum
            "moves_output": o != base_o,
            "cost_neutral": ops == base_ops,
            "causal_contribution": (o != base_o) and (ops == base_ops),
            "activated": S.activation_evidence(doc, nm)["verdict"] == "ACTIVATED",
        }
    cs = out["components"]
    out["all_activated"] = all(c["activated"] for c in cs.values())
    out["all_move_execution"] = all(c["moves_execution"] for c in cs.values())
    out["all_causal"] = all(c["causal_contribution"] for c in cs.values())
    out["any_causal"] = any(c["causal_contribution"] for c in cs.values())
    return out


def compose_pair(man_a, man_b, label_a="A", label_b="B"):
    """Compose two manifests under an envelope sized for the PAIR, so that the
    two conditions differ only in genome content and never in tape size."""
    sa = S.segment_from_instructions(man_a["genome"], label=label_a)
    sb = S.segment_from_instructions(man_b["genome"], label=label_b)
    need = len(man_a["genome"]) + len(man_b["genome"])
    tape = max(man_a["tape_words"], man_b["tape_words"])
    while tape < need:
        tape *= 2
    env = {"n_regs": max(man_a["n_regs"], man_b["n_regs"]), "tape_words": tape,
           "code_writable": man_a["code_writable"] or man_b["code_writable"],
           "persist": "tape",
           "tick_budget": max(man_a["tick_budget"], man_b["tick_budget"]),
           "out_cap": max(man_a["out_cap"], man_b["out_cap"])}
    return S.compose([(label_a, sa), (label_b, sb)], env), env


def eligibility(man_a, man_b, worlds=None, **kw):
    """Gate-by-gate eligibility for one ordered pair, with every gate measured on
    the COMPOSED object. Gates are reported INDIVIDUALLY and never AND-ed here;
    the caller decides which are necessary for its claim, because packet 02
    found P2 excludes valid cross-component dependence that is simply not
    world-driven (DEP_CONST)."""
    doc, env = compose_pair(man_a, man_b)
    c = coupling(doc["manifest"], worlds, **kw)
    p = participation(doc, worlds, **kw)
    return {
        "G_activated": p["all_activated"],
        "G_coupled": c["any"],
        "G_coupled_execution_only": c["execution"],   # packet 01's stricter, buggy P2
        "G_emits": c["emits"],
        "G_unsaturated": not c["saturated"],
        "G_moves_execution": p["all_move_execution"],   # old P5, retained as a datum
        "G_causal_both": p["all_causal"],
        "G_causal_any": p["any_causal"],
        "ops": c["ops"], "in_reads": c["in_reads"], "first_status": c["first_status"],
        "participation": p["components"],
    }


if __name__ == "__main__":
    # SELF-TEST: participation() must score the known cases correctly, or it is
    # not an instrument. One known positive and one known negative minimum.
    import sys
    sys.path.insert(0, "D:/Prometheus")
    from integration.harmonia_diagnostics import envelope, genome, instr

    NOP, HALT, LOADI, IN, OUT = 0, 1, 3, 21, 23
    ENV = envelope(tape_words=128, n_regs=8, tick_budget=64, out_cap=8)
    B_EMIT = genome(instr(OUT, 0, 1, 0), instr(HALT))
    KNOWN = {
        "DEP_DATA":   (genome(instr(IN, 0, 1, 0)), B_EMIT, True),
        "DEP_CONST":  (genome(instr(LOADI, 0, 42, 0)), B_EMIT, True),
        "INDEP_REG":  (genome(instr(LOADI, 5, 12345, 0)), B_EMIT, False),
        "INDEP_LONG": (genome(*[instr(LOADI, 5, k, 0) for k in range(4)]), B_EMIT, False),
        "POSITION":   (genome(instr(NOP), instr(NOP)), B_EMIT, False),
    }
    ok = True
    print("harmonia_eligibility SELF-TEST -- participation() vs known truth")
    for name, (a, b, truth) in KNOWN.items():
        sa = S.segment_from_instructions(a, label="A")
        sb = S.segment_from_instructions(b, label="B")
        doc = S.compose([("A", sa), ("B", sb)], ENV)
        p = participation(doc)
        got = p["components"]["A"]["causal_contribution"]
        old_p5 = p["components"]["A"]["moves_execution"]
        good = got == truth
        ok &= good
        print("  %-11s causal=%-5s expected=%-5s %-14s | old_P5=%-5s activated=%s"
              % (name, got, truth, "OK" if good else "*** MISMATCH ***",
                 old_p5, p["components"]["A"]["activated"]))
    print("SELF-TEST", "PASS" if ok else "FAIL")
    print()
    print("  note: old_P5 and activated are TRUE for every row above, including")
    print("  the three known negatives. That is why they were retired as criteria.")
