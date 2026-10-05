"""PTE-C2A common: namespaces, plants/adversaries, batched program evaluation, competence-class rulers.

Operator order: roles/Ananke/prompts/2026-10-05_pte_c2a_directive/ (34bcebe4b).
Device-agnostic (cpu or cuda); importing this module does NOT hide or claim the GPU.

Plants are hand-written and are copied verbatim from the Wave-2 modules named beside each one (those modules
are left untouched). In C2A a plant is injected ONLY in the declared seeded arms (PSEED, KSEED) and the
Flight-1 pilot; BASE/W0/M32 never see one.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))

from prometheus.ananke import assays, envs, inference, plants  # noqa: E402
from prometheus.ananke.engine import Schedule, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
import hp_plants  # noqa: E402  (H-PLANT; pure, no environment side effects)

A = plants.assemble

# ------------------------------------------------------------------ namespaces (fresh; declared)
C2A_NS = 0xC2A01005          # every C2A key hangs off this; disjoint from C1 TRAIN/FINAL/HELD (0x7A1/0xF1A/0x4E1D
                             # are used as SECOND keys under a search seed) and from W2-AD NS 0x57324144
ADMIT_KEY = 0xAD01           # admission worlds (ceiling + plant + adversaries), per candidate
SEED_KEY = 0x5EED            # search seed per (cell, seed index); shared by all arms at that index (CRN pairing)
KSEED_KEY = 0x4B5E           # KSEED perturbation stream per (cell, k, seed index)
PILOT_KEY = 0x9110           # Flight-1 PSEED pilot (never production)
FAM_ID = {"RELAY": 1, "XOR": 2, "MAJ": 3, "FLIP": 4}

MARGIN_SE = inference.margin_for_keep(0.95, f=1.12)   # 2.605 SE (C2 draft s4)
SIGNAL_CUT = 0.55
B_CUT = 0.75
P_ADMIT = 64                  # admission pairs (128 worlds), C2 held design
M_HELD = 128                  # held worlds per search (64 pairs)


def search_seed(cell_key: int, idx: int) -> int:
    return H_int(C2A_NS, SEED_KEY, cell_key, idx)


def admit_seeds(fam: str, i: int, P: int = P_ADMIT) -> list:
    return assays.world_seeds(H_int(C2A_NS, ADMIT_KEY, FAM_ID[fam], i), 2 * P)


# ------------------------------------------------------------------ plants (verbatim copies, attributed)
def _bc(ph, body):
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def relay_flood(ph):                      # prometheus.ananke.plants (C1 plant)
    return plants.plant("relay_flood", ph)


def relay_refresh(ph):                    # W2-AD w2ad_plants.relay_refresh == P-1 decay_plant.py (P-2)
    return _bc(ph, A(ph, [
        ("GT", "T2", "S0", "ZERO", 0), ("GT", "T3", "ZERO", "S0", 0), ("SUB", "S0", "T2", "T3", 0),
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("GT", "T2", "T0", "ZERO", 0), ("GT", "T3", "ZERO", "T0", 0),
        ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0), ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0), ("MULQ", "EMIT", "T2", "T3", 0), ("MOV", "PAY0", "T1", 0, 0),
        ("SUB", "T3", "T1", "S0", 0), ("MULQ", "T3", "T3", "T2", 0), ("ADD", "S0", "S0", "T3", 0)]))


def relay_bit(ph):                        # W2-AD w2ad_plants.relay_bit (12 lines)
    return _bc(ph, A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("CONST", "T3", 0, 7, -1),
        ("GT", "T1", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "T1", "T3", 0),
        ("MOV", "EMIT", "S1", 0, 0), ("SEL", "EMIT", "T3", "T1", 0), ("SHR", "T2", "EMIT", 8, 0),
        ("XOR", "S1", "S1", "T2", 0), ("GT", "T0", "S1", "ZERO", 0), ("ADDI", "S0", "T0", 0, -128)]))


def p_flip(ph):                           # H-PLANT hp_plants.p_flip (imported, unmodified)
    return hp_plants.p_flip(ph)


def flip_bit16(ph):                       # W2-AD w2ad_plants.flip_bit16 (16 lines, decay-invariant bits)
    assert ph.prog_len >= 16 and ph.state_dim >= 2
    return _bc(ph, A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("CONST", "T3", 0, 7, -1),
        ("GT", "T1", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "T1", "T3", 0),
        ("MOV", "EMIT", "S1", 0, 0), ("SEL", "EMIT", "T3", "T1", 0), ("SHR", "T2", "EMIT", 8, 0),
        ("XOR", "S1", "S1", "T2", 0), ("GT", "T0", "S0", "ZERO", 0), ("XOR", "T0", "T0", "EMIT", 0),
        ("MULQ", "T1", "SENSE", "SENSE", 0), ("GT", "T3", "SENSE", "ZERO", 0), ("SEL", "T1", "T3", "T0", 0),
        ("ADDI", "S0", "T1", 0, -128)]))


def relay_latch(ph):                      # W2-L relay_latch_def.relay_latch (14 lines; FLIP copy adversary)
    body = A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "PAY0", "T3", 0),
        ("SUB", "T0", "PAY0", "S0", 0), ("MULQ", "EMIT", "T0", "PAY0", 0),
        ("MULQ", "T1", "PAY0", "PAY0", 0), ("SEL", "T1", "PAY0", "S0", 0), ("MOV", "S0", "T1", 0, 0),
        ("MULQ", "T3", "SENSE", "SENSE", 0), ("SEL", "T3", "SENSE", "S0", 0), ("MOV", "S0", "T3", 0, 0)])
    return _bc(ph, body)


def onehop(ph):                           # NEW (C2A adversary): sensors emit their cue, nobody forwards,
    return _bc(ph, A(ph, [                # every site accumulates arrivals into S0 (a one-hop law)
        ("MOV", "PAY0", "SENSE", 0, 0), ("MOV", "EMIT", "SENSE", 0, 0), ("ADD", "S0", "S0", "IN0_0", 0)]))


def latch_once(ph):                       # NEW (C2A adversary): a once-per-episode flood latch (E-W22 shape).
    return _bc(ph, A(ph, [                # each site latches the FIRST arrival's sign, forwards it once, and
        ("ADD", "T0", "SENSE", "IN0_0", 0),   # reads it out forever (answers trial 0, chance afterwards)
        ("GT", "T1", "T0", "ZERO", 0), ("GT", "T2", "ZERO", "T0", 0), ("SUB", "T1", "T1", "T2", 0),
        ("MULQ", "T3", "S1", "S1", 0),        # nonzero iff already latched
        ("SEL", "T3", "S1", "T1", 0),         # latched ? S1 : arrival sign
        ("SUB", "T2", "T3", "S1", 0),         # nonzero iff newly latched
        ("MULQ", "EMIT", "T2", "T2", 0), ("MOV", "PAY0", "T3", 0, 0),
        ("MOV", "S1", "T3", 0, 0), ("MOV", "S0", "T3", 0, 0)]))


def null(ph):
    return np.zeros((ph.rules, ph.prog_len, 5), dtype=np.int64)


def canonical(g: np.ndarray) -> np.ndarray:
    """Re-encode a hand plant into the GA's sampling support (random_genomes/_rand_instr: fields 0-3 in 0..255,
    field 4 in -128..127). Flight-1 REPAIR R1: P_FLIP, FLIP_BIT16 and relay_bit carry CONST imm=128 (b=0), which
    the GA can never produce, so the plant as written was NOT inside the searched genome space (R link) and
    KSEED's neighbourhood was not the GA's. CONST computes (imm + Kp) << (b & 7); the canonical form is the
    smallest shift that fits: 128 -> imm 64, b 1. Identical behaviour while Kp == 0 (no WIMM line; site mutation
    off); with site mutation (mut_site > 0) Kp perturbs the constant by 2*Kp instead of Kp, so admission
    re-scores the canonical genome (it is what PSEED/KSEED inject). Other ops never carry an out-of-range field
    in the C2A plants (checked in test_c2a)."""
    x = np.array(g, dtype=np.int64, copy=True)
    R, L, _ = x.shape
    for r in range(R):
        for i in range(L):
            op, imm = int(x[r, i, 0]) % 16, int(x[r, i, 4])
            if -128 <= imm <= 127:
                continue
            assert op == 6 and (int(x[r, i, 3]) & 7) == 0, ("out-of-range immediate outside CONST b=0", r, i)
            for sh in range(1, 8):
                if imm % (1 << sh) == 0 and -128 <= imm >> sh <= 127:
                    x[r, i, 4] = imm >> sh
                    x[r, i, 3] = sh
                    break
            else:
                raise AssertionError(("no canonical CONST encoding", imm))
    assert ((x[..., :4] >= 0) & (x[..., :4] <= 255)).all() and ((x[..., 4] >= -128) & (x[..., 4] <= 127)).all()
    return x


def _canon(fn):
    def w(ph):
        return canonical(fn(ph))
    w.__name__ = fn.__name__
    w.raw = fn
    return w


# Plant of record = the FIRST design in declared order that passes admission (declared before any scoring).
# FLIP: only P_FLIP may be the plant of record (operator order s3 R: "P-FLIP or the predeclared refresh
# fallback"); FLIP_BIT16 (an unreviewed W2-AD design) is screened DESCRIPTIVELY only.
PLANTS = {"RELAY": {"relay_refresh": _canon(relay_refresh), "relay_flood": _canon(relay_flood),
                    "relay_bit": _canon(relay_bit)},
          "FLIP": {"P_FLIP": _canon(p_flip), "FLIP_BIT16": _canon(flip_bit16)}}
PLANT_OF_RECORD_ELIGIBLE = {"RELAY": ("relay_refresh", "relay_flood"), "FLIP": ("P_FLIP",)}
ADVERSARIES = {"RELAY": {"null": null, "onehop": onehop, "latch_once": latch_once},
               "FLIP": {"null": null, "relay_latch_copy": relay_latch, "latch_once": latch_once}}
# FLIP_CLOCK (W2-B adversaries.flip_clock) needs prog_len >= 28 and state_dim >= 4: OUTSIDE the C2A FLIP genome
# space (16 lines, state_dim 2), so no champion can be it; recorded as structurally excluded, not run.
# anti-copy: B is symmetric in copy/anti-copy (B_anti = 1 - B_copy pair by pair when the readout is never 0);
# reported from the copy adversary's per-trial record, see flip_B(anti=True).


def nlines(g):
    return int((np.asarray(g)[0, :, 0] % 16 != 0).sum())


# ------------------------------------------------------------------ batched evaluation (per-trial)
def eval_programs(ph: Physics, env: envs.EnvSpec, seeds: list, genomes: list, device="cpu", edits=None):
    """genomes: list of [rules, L, 5]; every program sees the SAME worlds (common random numbers).
    edits: optional list (same length) of fn(sense_val_np [T,M,K], ep) or None (schedule edits, e.g. teacher_off).
    -> (per_trial [G, M, trials] in {0, .5, 1}, ep)"""
    M = len(seeds)
    assert M % 2 == 0
    ep = envs.build(ph, env, seeds)
    G = len(genomes)
    edits = edits or [None] * G
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    sv0 = ep.schedule.sense_val.numpy()
    svs = []
    for e in edits:
        sv = sv0.copy()
        if e is not None:
            e(sv, ep)
        svs.append(sv)
    sch = Schedule(ep.schedule.sense_idx.repeat(G, 1), torch.as_tensor(np.concatenate(svs, 1)),
                   ep.schedule.read_idx.repeat(G, 1))
    gg = np.concatenate([np.repeat(np.asarray(g)[None], M, axis=0) for g in genomes], 0)
    w = World(ph, gg, ws1 * G, device=device, schedule=sch)
    w.run(env.T(), graph=False)
    trace = w.trace.cpu().numpy()
    out = np.stack([envs.per_trial(ep, trace[:, gi * M:(gi + 1) * M]) for gi in range(G)])
    return out, ep


def _r3(pairs, cut):
    r = inference.reading3(pairs, cut, ">", bound="lo", method="BOOTT", margin_se=MARGIN_SE)
    st = r["status"]
    if st == "DEGENERATE":            # zero-variance array: the two-valued reading decides (W2-X note)
        st = "TRUE" if r["raw"] else "FALSE"
    r["decided"] = st
    m, lo, hi = inference.pair_ci_student(pairs)
    r.update(mean=float(m), lo99=float(lo), hi99=float(hi))
    return r


def pairs_of(pt, scored, trial_mask=None):
    """pt [M, tr]; scored [M, tr] bool -> mirror-pair means of per-world accuracy over (scored & mask)."""
    msk = scored.copy()
    if trial_mask is not None:
        msk = msk & trial_mask[None, :]
    acc = (pt * msk).sum(1) / np.maximum(msk.sum(1), 1)
    return acc.reshape(-1, 2).mean(1)


def flip_B_pairs(pt, ep, anti=False):
    """B = mean(changed-cue acc, same-cue acc) per mirror pair (W2-S/W2-AD definition)."""
    M, tr = pt.shape
    env = ep.meta["env"]
    Pd = env["delta"] + 1 + env["cue_len"] + env["iti"]   # == EnvSpec.period() for FLIP (checked in tests)
    sv = ep.schedule.sense_val.numpy()
    x = np.sign(sv[np.arange(tr) * Pd][:, :, 0]).T            # [M, tr]
    chg = np.zeros_like(ep.scored)
    chg[:, 1:] = x[:, 1:] != x[:, :-1]
    sc = ep.scored
    p = 1.0 - pt if anti else pt

    def pooled(mask):
        num = (p * mask).reshape(M // 2, 2, tr).sum((1, 2))
        den = mask.reshape(M // 2, 2, tr).sum((1, 2))
        return np.where(den > 0, num / np.maximum(den, 1), np.nan)
    pc, ps = pooled(sc & chg), pooled(sc & ~chg)
    ok = ~(np.isnan(pc) | np.isnan(ps))
    return (pc[ok] + ps[ok]) / 2, float(np.nanmean(pc)), float(np.nanmean(ps))


def competence(role: str, pt, ep) -> dict:
    """Competence-class ruler. role in {'RELAY-mh', 'FLIP', 'RELAY-1h'}.
    RELAY-mh: SIGNAL on all trials AND on the late half (trials >= tr/2) -- a once-per-episode flood latch
              (E-W22) answers trial 0 and is at chance later, so it fails the late half.
    FLIP:     B = mean(changed, same) lo99 > .75 (copy/anti-copy policies sit at B ~ .5).
    RELAY-1h: SIGNAL on all trials (positive control; late half reported).
    Every component is reading3 (BOOTT 99%, margin 2.605 SE). Overall: TRUE iff every component TRUE; FALSE iff
    any component FALSE; else INDETERMINATE."""
    tr = pt.shape[1]
    late = np.arange(tr) >= tr // 2
    out = {"role": role}
    out["all"] = _r3(pairs_of(pt, ep.scored), SIGNAL_CUT)
    out["late"] = _r3(pairs_of(pt, ep.scored, late), SIGNAL_CUT)
    if role == "FLIP":
        b, chg, same = flip_B_pairs(pt, ep)
        out["B"] = _r3(b, B_CUT)
        out["B"].update(chg=chg, same=same)
        comps = ["B"]
    elif role == "RELAY-mh":
        comps = ["all", "late"]
    elif role == "RELAY-1h":
        comps = ["all"]
    else:
        raise KeyError(role)
    if "late" in comps:
        # Liveness guard (decided at Flight 1, before any search): the late half is read TWO-valued
        # (BOOTT lo99 > .55). It exists to reject latches, not to re-certify competence; with the 2.605-SE
        # margin it rejected relay_refresh/relay_bit whose late-half lo99 was .57-.58 (dev admission).
        out["late"]["decided"] = "TRUE" if out["late"]["lo99"] > SIGNAL_CUT else "FALSE"
        out["late"]["rule"] = "two-valued lo99 > .55"
    st = [out[c]["decided"] for c in comps]
    out["status"] = "TRUE" if all(s == "TRUE" for s in st) else ("FALSE" if "FALSE" in st else "INDETERMINATE")
    out["components"] = comps
    return out


def slim(c: dict) -> dict:
    """Compact form of a competence() record for rows."""
    o = {"status": c["status"], "role": c["role"]}
    for k in ("all", "late", "B"):
        if k in c:
            o[k] = {kk: c[k][kk] for kk in ("mean", "lo99", "hi99", "d_se", "status", "decided") if kk in c[k]}
            if k == "B":
                o[k]["chg"], o[k]["same"] = c[k]["chg"], c[k]["same"]
    return o


def teacher_off(sv, ep):                  # W2-AD census.teacher_off (FLIP teacher only on trial 0)
    e = ep.meta["env"]
    Pd = e["delta"] + 1 + e["cue_len"] + e["iti"]
    sv[Pd:, :, 1] = 0


def sensor_off(sv, ep):                   # RELAY must-fail ablation: the sensor is silenced
    sv[:, :, 0] = 0


def jdump(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, indent=1, default=_jd))


def _jd(o):
    if hasattr(o, "tolist"):
        return o.tolist()
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, float) and math.isnan(o):
        return None
    return str(o)
