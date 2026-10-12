"""WTP-05 causal controls, reachability gain and cognitive accounting (PREREG_WTP05 s8; directive s20, s23, s24).

Every number is measured on HELD-OUT seeds with the archive OFF: the organism runs alone.
  full            normal lifetime (plasticity as its arm allows); score = final-gate accuracy over the last
                  half of the lifetime (after learning has had a chance)
  ws_reset        working state zeroed at every step
  plast_frozen    eta = 0 (no lifetime learning; inherited parameters only)
  shuffled_hist   plasticity on, but each block's rewards are permuted across its episodes
  module_removed  every CALL returns zeros
  random_module   every module replaced by a random pure module with the same node and port counts
  birth / end     accuracy in the first block vs the last two blocks (lifetime-acquired structure)
Reachability gain RG(artifact) = accuracy with the artifact - accuracy with it ablated, at the same
subsequent budget (one lifetime): RG_state, RG_plastic, RG_module.
Cognitive accounting splits the final accuracy above chance into: environment (best cheap null's share,
from the admission ladder), inherited structure (birth block), lifetime learning (end - birth), working state
(full - ws_reset), promoted modules (full - module_removed) and search/archive (whether the elite's lineage
passed through the archive). The certifier's own contribution is reported as the gap between the training-
distribution accuracy and the certified probe accuracy.
"""
import copy

import numpy as np

from .mutate import random_node
from .tape import lifetime, node
from .worlds import make


def _acc(g, world, seeds, **kw):
    a_full, a_birth, a_end = [], [], []
    for s in seeds:
        rng = np.random.default_rng(s)
        world.new_life(rng)
        life = lifetime(g, world, rng, **kw)
        accs = [b["acc"].get(1) for b in life["blocks"] if 1 in b["acc"]]
        if not accs:
            continue
        a_full.append(np.mean(accs[len(accs) // 2:]))
        a_birth.append(accs[0])
        a_end.append(np.mean(accs[-2:]))
    return dict(acc=float(np.mean(a_full)), birth=float(np.mean(a_birth)), end=float(np.mean(a_end)))


def strip_modules(g):
    g = copy.deepcopy(g)
    g["modules"] = []
    return g


def random_modules(g, rng):
    g = copy.deepcopy(g)
    for m in g["modules"]:
        n_in = m.get("n_in", 1)
        nodes = [node("IN", port=p) for p in range(n_in)]
        while len(nodes) < len(m["nodes"]):
            op = str(rng.choice(["ADD", "MUL", "SIGN", "SEL", "CONST", "LIN", "DOT"]))
            nodes.append(random_node(op, len(nodes), rng, g["S"]))
        m["nodes"], m["out"] = nodes, len(nodes) - 1
    return g


def controls(g, spec, plasticity, seed=8_800_000, n_lives=6):
    fam, rung, cond = spec.split("-")
    w = make(f"{fam}-{rung}-desert")
    seeds = [seed + i for i in range(n_lives)]
    out = {"full": _acc(g, w, seeds, plasticity=plasticity)}
    out["ws_reset"] = _acc(g, w, seeds, plasticity=plasticity, ws_reset=True)
    if plasticity and g.get("eta", 0) > 0:
        out["plast_frozen"] = _acc(g, w, seeds, plasticity=False)
        out["shuffled_hist"] = _acc(g, w, seeds, plasticity=True, history_shuffle=True)
    if g["modules"]:
        out["module_removed"] = _acc(strip_modules(g), w, seeds, plasticity=plasticity)
        out["random_module"] = _acc(random_modules(g, np.random.default_rng(seed)), w, seeds, plasticity=plasticity)
    f = out["full"]["acc"]
    rg = dict(RG_state=f - out["ws_reset"]["acc"])
    if "plast_frozen" in out:
        rg["RG_plastic"] = f - out["plast_frozen"]["acc"]
        rg["RG_shuffled_history"] = f - out["shuffled_hist"]["acc"]
    if "module_removed" in out:
        rg["RG_module"] = f - out["module_removed"]["acc"]
        rg["RG_random_module"] = f - out["random_module"]["acc"]
    out["RG"] = rg
    return out


def accounting(ctrl, null_share, archive_lineage, cert_acc=None, train_acc=None):
    f = ctrl["full"]
    above = max(1e-9, f["acc"] - 0.5)
    acc = dict(final_acc=f["acc"],
               environment_null_share=null_share,
               inherited_structure=f["birth"] - 0.5,
               lifetime_learning=f["end"] - f["birth"],
               working_state=ctrl["RG"]["RG_state"],
               promoted_modules=ctrl["RG"].get("RG_module"),
               search_archive_lineage=archive_lineage,
               certifier_gap=(train_acc - cert_acc) if (cert_acc is not None and train_acc is not None) else None)
    acc["fractions_of_above_chance"] = {k: (acc[k] / above if isinstance(acc[k], float) else None)
                                       for k in ("inherited_structure", "lifetime_learning", "working_state", "promoted_modules")}
    return acc


def transfer(g, spec, plasticity, seed=8_900_000):
    """Directive s22 transfer probes for an R2+ elite (frozen genome; plasticity as in life). Returns final-gate
    accuracy per probe. Novel combination needs family D: NOT_TESTED."""
    from .certify import _probe
    from .worlds import FAMILIES
    fam, rung, _ = spec.split("-")
    rng = np.random.default_rng(seed)
    base_w = make(f"{fam}-{rung}-desert")
    learned = lifetime(g, base_w, rng, plasticity=plasticity)["learned"]
    learned = copy.deepcopy(learned)
    learned["eta"] = learned["sigma"] = 0.0
    probes = {"new_seeds": base_w}
    if fam in ("A", "N"):
        probes["longer_horizon_T24"] = FAMILIES[fam](rung, "desert", T=24)
    if fam == "A":
        probes["reskin_6_distractors"] = FAMILIES[fam](rung, "desert", n_distract=6)
    if fam == "N":
        probes["reskin_bit_rate_.7"] = FAMILIES[fam](rung, "desert", p_bit=0.7)
    if fam == "B":
        probes["reordered_modes_tags_swapped"] = FAMILIES[fam](rung, "desert", swap_tags=True)
    out = {}
    for name, w in probes.items():
        k, n, _ = _probe(learned, w, rng)
        out[name] = k / n
    out["novel_combination"] = "NOT_TESTED (family D not built)"
    return out
