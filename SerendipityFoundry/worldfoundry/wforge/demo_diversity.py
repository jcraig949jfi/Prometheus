"""World Foundry v0 -- generated-world diversity demonstration + determinism audit.

Deliverable items 17-18 of the v0 review packet:
  * sample N de novo genomes from grammar v0 and expand them
  * run the reference probe battery (solo; and paired-vs-random on 2-slot worlds)
  * measure: behavioral fingerprint diversity, the DISCRIMINATIVE BAND
    (worlds where probes actually differ), degenerate fractions (all-dead /
    no-discrimination), horizon-class mix, structural diversity
  * demonstrate lineage: mutate one world into descendants, show provenance
  * determinism audit: re-run identical (world, probes, seed) and require
    IDENTICAL trace hashes; also verify genome re-expansion reproduces the
    mechanics manifest hash bit-for-bit

Run:  python -m wforge.demo_diversity  [N]
"""
from __future__ import annotations

import sys
from collections import Counter

from . import GRAMMAR_VERSION
from .genome import de_novo, mutate
from .world import expand, Encounter
from .probes import BATTERY


def run_probe(mech, world_id, probe_cls, seed, opponent_cls=None):
    enc = Encounter(mech, world_id, seed)
    probes = [probe_cls()]
    if mech.n_slots == 2:
        probes.append((opponent_cls or probe_cls)())
    for i, p in enumerate(probes):
        p.reset(seed * 7919 + i, mech.act_width)
    done = False
    while not done:
        acts = [p.act(enc.observe(i)) for i, p in enumerate(probes)]
        done = enc.step(acts)
    return enc.outcome()


def fingerprint(mech, world_id, seeds=(11, 23)):
    """Per-world behavioral fingerprint: bucketed slot-0 outcome per probe."""
    fp = []
    for probe_cls in BATTERY:
        vals = []
        for s in seeds:
            from .probes import RandomP
            out = run_probe(mech, world_id, probe_cls, s, opponent_cls=RandomP)
            p0 = out["per_slot"][0]
            vals.append((p0["final_charge"] if p0["alive"] else -1,
                         p0["yield_events"]))
        charge = sum(v[0] for v in vals) // len(vals)
        yields = sum(v[1] for v in vals) // len(vals)
        bucket = (-1 if charge < 0 else min(9, charge // 64), min(9, yields // 4))
        fp.append(bucket)
    return tuple(fp)


def main(n_worlds=300):
    print(f"wforge diversity demo | grammar={GRAMMAR_VERSION} | N={n_worlds}")
    print("=" * 70)

    genomes = [de_novo(GRAMMAR_VERSION, 1000 + i) for i in range(n_worlds)]
    mechs = [expand(g) for g in genomes]

    # --- structural diversity ---
    hclass = Counter(m.horizon_class for m in mechs)
    slots = Counter(m.n_slots for m in mechs)
    stoch = Counter(m.stochasticity if hasattr(m, "stochasticity")
                    else ("SEEDED" if m.stoch_rate else "DET") for m in mechs)
    struct = Counter((len(m.lin_ops), m.delay > 0, m.regime_period > 0,
                      m.corrupt_rate > 0) for m in mechs)
    print(f"horizon classes : {dict(hclass)}")
    print(f"slot counts     : {dict(slots)}")
    print(f"stochasticity   : {dict(stoch)}")
    print(f"distinct structural signatures (ops,delay,regime,corrupt): {len(struct)}")

    # --- behavioral diversity + discriminative band ---
    fps, all_dead, no_disc, disc = [], 0, 0, 0
    for g, m in zip(genomes, mechs):
        fp = fingerprint(m, g.world_id)
        fps.append(fp)
        charges = [b[0] for b in fp]
        if all(c < 0 for c in charges):
            all_dead += 1
        elif len(set(fp)) == 1:
            no_disc += 1
        else:
            disc += 1
    print(f"distinct behavioral fingerprints: {len(set(fps))} / {n_worlds}")
    print(f"ALL-PROBES-DEAD worlds  : {all_dead:4d}  ({100*all_dead//n_worlds}%)  <- no selection info")
    print(f"NO-DISCRIMINATION worlds: {no_disc:4d}  ({100*no_disc//n_worlds}%)  <- no selection info")
    print(f"DISCRIMINATIVE BAND     : {disc:4d}  ({100*disc//n_worlds}%)  <- the usable landscape")

    # --- probe ordering diversity (do different worlds rank probes differently?) ---
    orderings = set()
    for fp in fps:
        ranked = tuple(sorted(range(len(BATTERY)), key=lambda i: -fp[i][0]))
        orderings.add(ranked)
    print(f"distinct probe orderings: {len(orderings)} (worlds disagree about which strategy wins)")

    # --- lineage demonstration ---
    print("-" * 70)
    parent = genomes[0]
    kids = [mutate(parent, op, 42 + k) for k, op in enumerate(
        ["PARAM_PERTURB", "PRIMITIVE_INSERT", "REWIRE", "INTERFACE_MUTATE"])]
    gkid = mutate(kids[0], "PARAM_PERTURB", 77)
    print(f"lineage: parent {parent.world_id}")
    pfp = fingerprint(expand(parent), parent.world_id)
    for k in kids + [gkid]:
        kfp = fingerprint(expand(k), k.world_id)
        differs = "differs" if kfp != pfp else "same-behavior"
        ops = ">".join(m.op for m in k.mutation_history)
        print(f"  child {k.world_id}  ops={ops:<40s} {differs}")
    assert gkid.parent_ids == (kids[0].world_id,), "lineage chain broken"
    print("lineage provenance chain: OK (grandchild records child as parent)")

    # --- determinism audit ---
    print("-" * 70)
    g0, m0 = genomes[7], mechs[7]
    from .probes import RandomP
    t1 = run_probe(m0, g0.world_id, RandomP, 99)["trace_hash"]
    t2 = run_probe(m0, g0.world_id, RandomP, 99)["trace_hash"]
    assert t1 == t2, "DETERMINISM BREACH: same manifest, different trace"
    m0b = expand(g0)
    assert m0.manifest_hash() == m0b.manifest_hash(), "re-expansion mismatch"
    t3 = run_probe(m0b, g0.world_id, RandomP, 99)["trace_hash"]
    assert t3 == t1, "re-expanded world produced different trace"
    diff = run_probe(m0, g0.world_id, RandomP, 100)["trace_hash"]
    assert diff != t1, "different seed produced identical trace (suspicious)"
    print(f"determinism: replay trace hash identical      OK  {t1[:16]}...")
    print("determinism: genome re-expansion bit-identical OK")
    print("determinism: seed sensitivity                  OK")
    print("=" * 70)
    return {
        "n": n_worlds, "band_pct": 100 * disc // n_worlds,
        "all_dead_pct": 100 * all_dead // n_worlds,
        "fingerprints": len(set(fps)), "orderings": len(orderings),
    }


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    main(n)
