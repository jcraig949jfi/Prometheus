"""v0.2 adapters for the four PORTABILITY-01 engines. FROZEN before the regression is rerun (ruling s11). Every rule below is derived
from the contract (v0.2.1) and from each engine's FIELD DEFINITIONS, not from the verdicts we hope to see. Engines are read-only.

COMMON
  hu_rule = MAJORITY(threshold 0.5, strict; tie -> ILL_POSED; no majority -> the engine's declared native policy) applied to FACTUAL
  contributor shares of the WHOLE output. Unknown shares -> NOT_IDENTIFIABLE unless a strict known majority exists (v0.2.1).
  Three autonomy roles, never bare:
    AUTONOMY_MATERIAL  own material > 1/2 of the output (YES) / another source > 1/2 (NO) / else NI
    AUTONOMY_WRITE     own code provably governed > 1/2 of the heritable writes (YES) / foreign code did (NO) / else NI
    AUTONOMY_EXEC      own region > 1/2 of execution steps (YES) / else NO; NI if steps are not recorded

ARCHAEON (native birth events, core.World._birth)
  BODY = cell; IDENTITY = oid (child oid not in the event -> the child's identity is a NEW identity, NI). The occupant of child_cell is
  a BODY whose previous identity ends at this birth (the body persists; J15).
  write_governing / execution_share: `executed_material` counts OPCODE FETCHES by source over the whole execution = execution share.
  If every fetch came from one source ('self' or 'neighbour'), that source necessarily governed every write too; if 'mixed', which
  code executed the writing instructions is not recorded -> write_governing NI.
  factual shares (32 bytes): executor glin copied_exec/32, occupant glin copied_nbr/32, computed bytes -> contributors (shared
  equally as NI mass), remaining bytes new material (mutation / input / constant, not a contributor).
  Native no-majority policy: ORIGINATE (a new glin). Native tie-break (nE >= nN -> executor) is NOT adopted: a 16/16 split is
  ILL_POSED under v0.2 and is reported beside the native reading.
  made_in: arrivals 'inflow_chamber', births 'ecology' (LOCATION); never used for ancestry.
  Counterfactuals: ENVGATE-02 arm contrasts as population-level CF_TEST nodes (intervention = input-window arm, outcome = genetic
  establishments per block; results = the frozen verdict's tests).

BEE (traced birth rows; traced_replay.py semantics)
  factual shares over L: writer own material = copied_from_own/L (TRACE); occupant retained = (L - n_window_writes)/L (TRACE write
  set; owner HU NI because `replaced` is not persisted); other written bytes = NI mass. into_empty: retained bytes are zeros
  (constant, no contributor).
  write_governing over the n_window_writes heritable writes: own code governed >= by_own_code (TRACE: copy op pc < L, src < L);
  foreign code governed >= copied_from_own - by_own_code (own-sourced bytes written by code outside the writer's region); the rest NI.
  execution_share: own_steps / win_steps / other_steps (TRACE).
  ARCH (bounded FULL replay only; births rows carry no tapes): declared criteria, in order:
    exact     child == writer's pre-execution tape
    rotation  child is a cyclic rotation of the writer's pre-execution tape (justification: an entry-point offset in a
              copy loop copies the same program shifted; the program text is the same up to its start address)
    otherwise NOT_IDENTIFIABLE (the child has some organisation; no declared criterion recognises it).
  Native readings kept beside: material (resemblance), is_sr, sr_depth, fid_pre.

NPE (preserved H2 RESERVOIR replays; P-11 definitions, p11.py)
  BODY = the organism's slot (victim_slot); a pair-tape birth is IDENTITY_CHANGE on the SAME BODY: old oid -> new oid (J15).
  Donor body: slot not recorded -> executor_body NI; executor_identity = donor oid.
  Factual material over the victim half (n): D_ord = positions where the initial victim byte differed from the donor's and the final
  byte equals it. Their VALUES come from the donor's genome (value equals donor, differs from victim): donor material share = |D|/n
  (DERIVED). Positions already equal to the donor (fid_init_ordinary) hold values both share: victim-retained or rewritten, not
  resolvable per position -> NI mass. Continuity: donor HU iff |D|/n > 1/2, else NI (never ILL_POSED: the evidence is incomplete).
  write_governing over D: donor context authored donor_authored_share (prov, TRACE); the rest was written by the victim's context.
  CF_TEST nodes (all P-11 fields; intervention and outcome named):
    NECESSITY(donor writes | block donor writes, REAL victim | victim fidelity to donor >= 0.9)   <- fid_donor_disabled_ordinary < 0.9
    SUFFICIENCY(donor | randomize victim, 3 draws, majority 2 | rebuilt fidelity >= 0.9)         <- C2
    SUFFICIENCY(donor | randomize victim | donor authors >= 0.9 of directed changes)              <- C4
    NECESSITY(donor writes | block donor writes, RANDOMIZED victim | fidelity >= 0.9)            <- C5
  host_body = the victim body.

PTE (instrumented GA replay; engine code unchanged)
  crossover is re-implemented with the IDENTICAL RNG call (m = g.random(a.shape[:2]) < 0.5) so the mask is logged; the champion and
  curve must equal the un-instrumented run.
  factual shares = mask counts over G x L instructions (complete evidence); continuity MAJORITY, tie/no majority -> ILL_POSED;
  mutation children continue their single parent (unmutated share > 1/2).
  ARCH behavioral: exact equality of the per-world accuracy vector on 8 probe worlds from a disjoint seed namespace (0xA4C7)
  (justification: the vector is produced by the full world dynamics; equality over 8 worlds x trials identifies the computed policy
  up to the probe set). A vector equal to the constant-policy control's is flagged DEGENERATE (membership is not informative).
  In-world: executor_body = site; execution_share = rule r; all heritable fields NOT_APPLICABLE; packets are not MATERIAL.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Dict, List, Optional

from archaeon.causal_lens.schema_v02 import Graph, NI, NONE, NA, ILL, YES, NO, continuity

MAJ_ORIG = {"kind": "MAJORITY", "threshold": 0.5, "tie": "ILL_POSED", "no_majority": "ORIGINATE"}
MAJ_ILL = {"kind": "MAJORITY", "threshold": 0.5, "tie": "ILL_POSED", "no_majority": "ILL_POSED"}


def tri_major(own, foreign, total):
    if total <= 0: return NI
    if own > total / 2: return YES
    if foreign > total / 2: return NO
    return NI


# ------------------------------------------------------------------------------------------------ ARCHAEON
def archaeon_event(ev: dict) -> dict:
    """Light v0.2 reading of one native Archaeon birth event."""
    G = 32; nE, nN, comp = ev["copied_exec"], ev["copied_nbr"], ev["computed"]
    shares = {}
    if nE: shares["glin:%d" % ev["executor_glin"]] = nE / G
    if nN:
        occ = ev["template_glin"] if ev["template"] == "neighbour" and ev["template_glin"] is not None else None
        others = [c for c in ev["contributors"] if c != ev["executor_glin"]]
        if occ is None: occ = others[0] if len(others) == 1 else (ev["executor_glin"] if not others else None)
        k = "glin:%d" % occ if occ is not None else "occupant?"
        shares[k] = shares.get(k, 0) + nN / G if k != "occupant?" else NI
    if comp: shares["computed?"] = NI
    c = continuity(shares, MAJ_ORIG)
    em = ev["executed_material"]; sc = ev["exec_counts"]; tot = max(1, sc.get("self", 0) + sc.get("nbr", 0) + sc.get("other", 0))
    wg = "own" if em == "self" else ("foreign" if em == "neighbour" else NI)
    return {"hu_continuity": c["hu_continuity"], "ill_posed": c.get("ill_posed"), "native_mechanism": ev["mechanism"],
            "native_child_glin": ev["child_glin"], "native_template": ev["template"],
            "autonomy_material": tri_major(nE, nN, G), "autonomy_write": YES if wg == "own" else (NO if wg == "foreign" else NI),
            "autonomy_exec": YES if sc.get("self", 0) > tot / 2 else NO, "host_body": ("cell:%d" % ev["executor_cell"]) if ev["host_glin"] is not None else NONE}


def envgate02_cf_graph(results: dict) -> Graph:
    g = Graph("archaeon.envgate2", "population", {"hu_rule": MAJ_ORIG}, {"source": "ENVGATE-02 RESULTS.json (frozen)"})
    g.event("est", ["ESTABLISHMENT"], persisting_object=dict(value="genetic_establishment_rate", basis="DECLARED", declared_kind="population rate of HU establishment"))
    g.node("window", "ENV", bytes="120..135")
    tot = results["totals_genetic"]; P = results["primary"]
    g.cf_test("cf_block", "window", "NECESSITY", {"name": "block input window 120..135 (arm BAND0 vs U)", "blocks": 24},
              {"predicate": "genetic establishments per block U > BAND0 (exact sign test, Holm)"}, YES if P["P1_U_gt_BAND0"]["holm_significant"] else NO, on="est",
              totals={"U": tot["U"], "BAND0": tot["BAND0"]})
    for arm, key in (("RRIGHT", "P2_RRIGHT_gt_R128"),):
        g.cf_test("cf_rescue_128_131", "window", "SUFFICIENCY", {"name": "restore only 128..131 (RRIGHT) vs only 128 (R128)"},
                  {"predicate": "RRIGHT > R128 per block (Holm)"}, YES if P[key]["holm_significant"] else NO, on="est", totals={"RRIGHT": tot["RRIGHT"], "R128": tot["R128"]})
    g.cf_test("cf_rescue_weak", "window", "SUFFICIENCY", {"name": "restore 128..131 (RRIGHT) vs 125..128 (RWEAK)"},
              {"predicate": "RRIGHT > RWEAK per block (Holm)"}, YES if P["P3_RRIGHT_gt_RWEAK"]["holm_significant"] else NO, on="est",
              totals={"RRIGHT": tot["RRIGHT"], "RWEAK": tot["RWEAK"]})
    return g


# ------------------------------------------------------------------------------------------------ BEE
def bee_row(r: list, L: int) -> dict:
    nw, own, byown, into_empty = r[7], r[8], r[9], r[19]
    own_s, win_s, oth_s = r[13], r[14], r[15]
    retained = 0 if into_empty else L - nw; other = nw - own; foreign_gov = own - byown
    shares = {"writer": own / L}
    if retained: shares["occupant"] = NI                                       # owner HU not persisted; its SIZE is known, its identity is not
    if other: shares["other"] = NI
    # the retained mass is one contributor of known size: use it to decide majority when it is the majority
    if retained > L / 2: c = {"hu_continuity": "occupant"}
    else: c = continuity(shares, MAJ_ORIG)
    ex_tot = own_s + win_s + oth_s
    return {"hu_continuity": c["hu_continuity"],
            "autonomy_material": YES if own > L / 2 else (NO if retained > L / 2 else NI),
            "autonomy_write": tri_major(byown, foreign_gov, nw),
            "autonomy_exec": (YES if own_s > ex_tot / 2 else NO) if ex_tot else NI,
            "exec_own_share": round(own_s / ex_tot, 3) if ex_tot else None,
            "write_own_min": byown, "write_foreign_min": foreign_gov, "writes": nw, "own_bytes": own, "retained": retained, "other": other}


def bee_arch(child: bytes, writer_pre: bytes) -> str:
    if child == writer_pre: return "exact"
    n = len(writer_pre)
    for k in range(1, n):
        if child == writer_pre[k:] + writer_pre[:k]: return "rotation"
    return NI


# ------------------------------------------------------------------------------------------------ NPE
def npe_graph(rec: dict) -> (Graph, List[dict]):
    """Canonical v0.2 graph + per-event readings from one preserved NPE replay record."""
    g = Graph("npe.z80atlas_c9", "segment", {"hu_rule": MAJ_ORIG}, {"specimen": (rec.get("job") or {}).get("specimen"), "arm": (rec.get("job") or {}).get("arm")})
    hu = {}; origin = {}
    for f in rec["founders"]:
        h = "anc%d" % f["anc"]; hu[f["oid"]] = h
        o = ("TRANSPLANT" if rec["implant"] == "ACTUAL_GENOME" else "RANDOM_INIT") if f["implant"] else \
            ("INSERTED_SEED" if f["anc"] < (rec["invaders"] or 0) else ("RANDOM_INIT" if rec["seeding"] == "RANDOM" else "INSERTED_SEED"))
        origin[h] = o
    pair = {p["child"]: p for p in rec["pair"]}; out = []
    n = None
    for e in rec["lineage"]:
        if e.get("kind") != "birth" or e["child"] not in pair: continue
        p = pair[e["child"]]; p11 = e.get("p11") or {}
        n = n or e.get("span") or 32
        D = p11.get("n_directed_ordinary"); s = p11.get("donor_authored_share_ordinary"); fi = p11.get("fid_init_ordinary")
        dhu = hu.get(p["donor_oid"], NI)
        donor_share = (D / n) if D is not None else NI
        shares = {dhu if dhu != NI else "donor?": donor_share}
        if D is None or D < n: shares["victim_or_shared?"] = NI
        c = continuity(shares, MAJ_ORIG) if dhu != NI else {"hu_continuity": NI}
        hc = c["hu_continuity"] if c["hu_continuity"] != "donor?" else NI
        hu[e["child"]] = hc if hc not in (NONE,) else NI
        t = "b%d" % e["child"]; V = "slot:%s" % p["victim_slot"]
        g.node(V, "BODY"); g.node("oid:%d" % p["victim_old_oid"], "IDENTITY"); g.node("oid:%d" % e["child"], "IDENTITY"); g.node("oid:%d" % p["donor_oid"], "IDENTITY")
        g.edge("oid:%d" % p["victim_old_oid"], "assigned", V, until=t); g.edge("oid:%d" % e["child"], "assigned", V, **{"from": t})
        g.edge("oid:%d" % e["child"], "labelled_parent", "oid:%d" % p["donor_oid"])
        g.event(t, ["REPRODUCTION", "AMPLIFICATION", "HOSTING", "IDENTITY_CHANGE"] if hc not in (NI,) else ["HOSTING", "IDENTITY_CHANGE"])
        g.edge(t, "consumes", V); g.edge(t, "produced", V); g.edge(t, "produced", "oid:%d" % e["child"]); g.edge(t, "hosted_by", V)
        g.field(t, "host_body", V, "TRACE", "body"); g.field(t, "executor_body", NI, "NATIVE_RECORD", source="donor slot not recorded")
        g.field(t, "executor_identity", "oid:%d" % p["donor_oid"], "NATIVE_RECORD")
        if dhu != NI:
            g.node("hu:" + dhu, "HU"); g.node("mD:%s" % t, "MATERIAL"); g.edge("mD:%s" % t, "member_of", "hu:" + dhu)
            cm = g.node("cD:%s" % t, "MATERIAL", share=donor_share if donor_share != NI else None); g.edge(cm, "copies_from", "mD:%s" % t, basis="DERIVED")
            g.edge(t, "produced", cm); g.edge(V, "carries", cm)
            if hc not in (NI, NONE): g.edge(cm, "member_of", "hu:" + dhu)
            g.field(t, "factual_contributors", ["hu:" + dhu], "DERIVED", "segment", shares={"donor": donor_share, "unresolved": "victim-retained or rewritten same-value"})
        g.field(t, "hu_continuity", ("hu:" + hc) if hc not in (NI, NONE) else hc, "DERIVED")
        g.field(t, "write_governing", {"donor_context": s, "victim_context": (round(1 - s, 4) if s is not None else NI)} if s is not None else NI,
                "TRACE", source="p11 prov (last context to change the value) over the directed set")
        cfs = {}
        if p11:
            dis = p11.get("fid_donor_disabled_ordinary")
            spec = [("N_real", "NECESSITY", "block donor writes, REAL victim (ordinary)", "victim fidelity to donor >= 0.9", (YES if dis < 0.9 else NO) if dis is not None else NI),
                    ("S_rebuild", "SUFFICIENCY", "randomize victim half (3 draws, majority 2)", "rebuilt victim fidelity to donor >= 0.9", YES if p11.get("C2") else NO),
                    ("S_author", "SUFFICIENCY", "randomize victim half (3 draws, majority 2)", "donor authors >= 0.9 of directed changes", YES if p11.get("C4") else NO),
                    ("N_random", "NECESSITY", "block donor writes, RANDOMIZED victim", "fidelity >= 0.9 fails without donor writes", YES if p11.get("C5") else NO)]
            for cid, kind, iv, oc, res in spec:
                g.cf_test("%s:%s" % (cid, t), "oid:%d" % p["donor_oid"], kind, {"name": iv}, {"predicate": oc}, res, on=t); cfs[cid] = res
        out.append({"child": e["child"], "victim_body": V, "old_identity": p["victim_old_oid"], "new_identity": e["child"],
                    "body_continuity": "SAME_BODY", "hu_continuity": hc, "donor_material_share": donor_share, "fid_init": fi,
                    "donor_write_share": s, "cf": cfs, "native": {"causal": e.get("causal"), "p11_pass": p11.get("pass")},
                    "spontaneous": ("NO" if origin.get(hc) in ("TRANSPLANT", "INSERTED_SEED") else ("YES" if origin.get(hc) else NI)) if hc not in (NI, NONE) else NI})
    return g, out


# ------------------------------------------------------------------------------------------------ PTE
def pte_instrumented_evolve(row: dict, small: dict, device="cpu"):
    import numpy as np
    from prometheus.ananke import search as S, envs, assays
    from prometheus.ananke.physics import Physics
    ph = Physics.from_dict(row["physics"]); env = envs.EnvSpec(**row["env"]); sp = S.SearchSpec(**{**row["search"], **small})
    log = []; genomes = {}; om, oc = S.mutate, S.crossover

    def gh(a):
        import hashlib
        h = hashlib.sha256(np.ascontiguousarray(a, dtype=np.int64).tobytes()).hexdigest()[:16]; genomes.setdefault(h, np.array(a)); return h

    def cross(g, a, b):
        m = g.random(a.shape[:2]) < 0.5                                     # IDENTICAL draw to search.crossover
        c = np.where(m[..., None], a, b)
        log.append({"op": "crossover", "a": gh(a), "b": gh(b), "child": gh(c), "from_a": int(m.sum()), "from_b": int(m.size - m.sum()), "total": int(m.size)})
        return c

    def mut(g, parent, sp_):
        c = om(g, parent, sp_)
        log.append({"op": "mutate", "parent": gh(parent), "child": gh(c), "changed_fields": int(np.sum(c != parent)), "changed_instr": int(np.sum(np.any(c != parent, axis=-1))),
                    "total_instr": int(c.shape[0] * c.shape[1])})
        return c
    S.mutate, S.crossover = mut, cross
    try:
        out = S.evolve(ph, env, row["search_seed"], sp, device=device)
    finally:
        S.mutate, S.crossover = om, oc
    plain = S.evolve(ph, env, row["search_seed"], sp, device=device)
    same = {"champion_identical": out["champion"] == plain["champion"], "curve_identical": out["curve"] == plain["curve"]}
    return ph, env, log, genomes, same


def pte_behavior(ph, env, genomes: Dict[str, object], device="cpu"):
    import numpy as np
    from prometheus.ananke import assays
    keys = sorted(genomes); seeds = assays.world_seeds(0xA4C7, 8)
    r = assays.evaluate(ph, np.stack([genomes[k] for k in keys]), env, seeds, device=device)
    return {k: tuple(float(x) for x in r.acc[i]) for i, k in enumerate(keys)}


def pte_lens(log: List[dict], sig: Dict[str, tuple], const_sig: Optional[tuple]) -> dict:
    cls = Counter(); rows = []
    for i, e in enumerate(log):
        if e["op"] != "crossover": continue
        m = log[i + 1] if i + 1 < len(log) and log[i + 1]["op"] == "mutate" and log[i + 1]["parent"] == e["child"] else None
        c = continuity({"a": e["from_a"] / e["total"], "b": e["from_b"] / e["total"]}, MAJ_ILL)
        final = m["child"] if m else e["child"]
        s_child, s_a, s_b = sig.get(final), sig.get(e["a"]), sig.get(e["b"])
        degenerate = s_child is not None and const_sig is not None and s_child == const_sig
        arch = ("same_as_a" if s_child == s_a else "") + ("same_as_b" if s_child == s_b else "")
        arch = arch or ("new_class" if s_child is not None else NI)
        k = ("continuity=%s" % (c["hu_continuity"] if c["hu_continuity"] in (ILL, NI, NONE) else "decided"), "arch=%s" % arch, "degenerate=%s" % degenerate)
        cls[k] += 1; rows.append({"from_a": e["from_a"], "from_b": e["from_b"], "total": e["total"], "hu_continuity": c["hu_continuity"], "arch": arch,
                                  "degenerate": degenerate, "mutated_fields_after": m["changed_fields"] if m else None})
    return {"classes": {" | ".join(k): v for k, v in cls.items()}, "rows": rows}
