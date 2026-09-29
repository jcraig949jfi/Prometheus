"""W-K: adversarial intervention-reach fixtures and candidate checks.

Everything here is W-K's own code. The engine (prometheus.ananke.engine)
is imported, never edited. Bugs live in HARNESSES (the arm's own code) or
in ARM SPECS, exactly where they lived in the mined cases.
"""
from __future__ import annotations

import dataclasses
import hashlib
import time
import zlib

import numpy as np
import torch

from prometheus.ananke import assays, c1b, envs, lens, plants, rng
from prometheus.ananke.engine import Controls, World, Schedule
from prometheus.ananke.physics import Physics

torch.set_num_threads(2)
NS = 0x5F0
M = 64
SEEDS = assays.world_seeds(NS, M)
DEV = "cpu"
COST = {"runs": 0}


# ======================================================================= plants
def bc(body, ph):
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def flood_rwrite(ph):
    """relay_flood + cue-signed routing writes to port 0 (w changes with the cue)."""
    lines = plants.assemble(ph, [("MOV", "RVAL", "T1", 0, 0)], L=1)
    out = np.zeros((ph.prog_len, 5), dtype=np.int64)
    out[:12] = plants.relay_flood(ph)[:12]
    out[12] = lines[0]
    return bc(out, ph)


def flood_rdecor(ph):
    """relay_flood + cue-INDEPENDENT round-robin routing writes (+16 to port S1)."""
    rf = [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("GT", "T2", "T0", "ZERO", 0),
        ("GT", "T3", "ZERO", "T0", 0), ("SUB", "T1", "T2", "T3", 0),
        ("MULQ", "T2", "T1", "T1", 0), ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0), ("MULQ", "EMIT", "T2", "T3", 0),
        ("MOV", "PAY0", "T1", 0, 0), ("SUB", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T2", 0), ("ADD", "S0", "S0", "T3", 0),
        ("ADDI", "S1", "S1", 0, 1),            # counter
        ("MOV", "RPORT", "S1", 0, 0),
        ("CONST", "RVAL", 0, 0, 16),
    ]
    return bc(plants.assemble(ph, rf), ph)


def latch_listen(ph):
    """echo_hold's emission/relay logic (lines 0-19) + a SENSE latch into S0:
    cue-bearing echoes reach the sensor/actuator but are never read."""
    eh = plants.echo_hold(ph)
    latch = plants.assemble(ph, [
        ("CONST", "T0", 0, 7, 1), ("GT", "T2", "SENSE", "T0", 0),
        ("SUB", "T1", "ZERO", "T0", 0), ("GT", "T3", "T1", "SENSE", 0),
        ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0),
        ("SUB", "T3", "T1", "S0", 0), ("MULQ", "T3", "T3", "T2", 0),
        ("ADD", "S0", "S0", "T3", 0)], L=9)
    out = np.zeros((ph.prog_len, 5), dtype=np.int64)
    out[:20] = eh[:20]
    out[20:29] = latch
    return bc(out, ph)


def rule_decor(ph):
    """Two identical SENSE latches; each rule SETRULEs to the other every tick."""
    latch = [("CONST", "T0", 0, 7, 1), ("GT", "T2", "SENSE", "T0", 0),
             ("SUB", "T1", "ZERO", "T0", 0), ("GT", "T3", "T1", "SENSE", 0),
             ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0),
             ("SUB", "T3", "T1", "S0", 0), ("MULQ", "T3", "T3", "T2", 0),
             ("ADD", "S0", "S0", "T3", 0)]
    r0 = plants.assemble(ph, latch + [("CONST", "T2", 0, 0, 1), ("SETRULE", "T3", "T2", 0, 0)])
    r1 = plants.assemble(ph, latch + [("CONST", "T2", 0, 0, 0), ("SETRULE", "T3", "T2", 0, 0)])
    return np.stack([r0, r1])


PLANTS = {  # name -> (plant physics (genome-space fields), genome fn)
    "echo_hold": (plants.c1b_echo_physics, lambda ph: bc(plants.echo_hold(ph), ph)),
    "hold_latch": (lambda: plants.c1b_echo_physics().replace(prog_len=12, payload_width=1),
                   lambda ph: plants.plant("hold_latch", ph)),
    "relay_flood": (plants.c1b_da_physics, lambda ph: plants.plant("relay_flood", ph)),
    "rule_switch_hold": (plants.c1b_rule_physics, plants.rule_switch_hold),
    "route_relay": (plants.c1b_route_physics, lambda ph: bc(plants.route_relay(ph), ph)),
}

# ======================================================================= envs
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)
RELAY_DA = envs.EnvSpec(family="RELAY", d=1, delta=4, cue_len=2, trials=12, iti=50)
RELAY_ROUTE = envs.EnvSpec(family="RELAY", d=2, delta=8, cue_len=4, trials=12)


# ======================================================================= hooks
class CondFlush:
    """Between-tick hook: flush every in-flight packet of the worlds where
    cond holds. kind: 'never' (|sensor S0| > 256), 'probe' (never, but the
    probe mutates in-flight payloads in place), 'fires' (sensor emitted)."""

    def __init__(self, kind, sham=False):
        self.kind, self.sham = kind, sham
        self.hits = 0

    def cond(self, w, ep):
        B = w.B
        sensor = w.sch_idx[:, 0]
        bi = torch.arange(B)
        if self.kind == "never":
            return w.S[bi, sensor, 0].abs() > 256
        if self.kind == "probe":
            big = w.Msum[..., 0].abs_().sum((0, 2, 3))      # BUG: in-place abs_ on a view
            return big > 10 ** 12
        if self.kind == "fires":
            return w.last_emit[bi, sensor]
        raise KeyError(self.kind)

    def __call__(self, w, t, ep):
        c = self.cond(w, ep)
        if self.sham:
            return 0
        n = int(c.sum())
        if n:
            keep = (~c).to(w.Msum.dtype)
            w.Msum.mul_(keep[None, :, None, None, None])
            w.Mcnt.mul_(keep[None, :, None, None])
        self.hits += n
        return n


# ======================================================================= arm spec
@dataclasses.dataclass
class Arm:
    name: str
    ctrl_fn: object = None                # (env, ep) -> Controls kwargs
    phys: dict = dataclasses.field(default_factory=dict)
    hook: object = None                   # factory () -> CondFlush
    var: str = "S"                        # declared state variable
    foot_fn: object = None                # (env, ep, ph) -> (ticks list, site mask [B,N] or None)
    window: bool = False                  # windowed packet drop (K1 applies)
    pathway: str = "transport"

    def ctrl(self, env, ep):
        return self.ctrl_fn(env, ep) if self.ctrl_fn else {}

    def declared_ctrl(self, env, ep):
        return sorted(self.ctrl(env, ep).keys())

    def sham(self):
        if self.hook is not None:
            k = self.hook().kind
            return Arm(self.name, None, {}, lambda: CondFlush(k, sham=True), self.var,
                       self.foot_fn, self.window, self.pathway)
        return Arm(self.name, None, {}, None, self.var, self.foot_fn, self.window, self.pathway)


NORMAL = Arm("normal")


# ======================================================================= harnesses
@dataclasses.dataclass
class RunOut:
    trace: np.ndarray
    acc: np.ndarray
    pairs: np.ndarray
    digests: list
    manifest: dict
    rec: list
    self_hits: int
    applied: int | None
    applied_worlds: int | None
    ep: object
    wall: float


def _sha(x) -> str:
    if isinstance(x, torch.Tensor):
        x = x.cpu().numpy()
    return hashlib.sha256(np.ascontiguousarray(np.asarray(x)).tobytes()).hexdigest()[:16]


def _ctrl_manifest(c: Controls) -> dict:
    out = {}
    for f in dataclasses.fields(c):
        v = getattr(c, f.name)
        out[f.name] = _sha(v) if isinstance(v, np.ndarray) or isinstance(v, torch.Tensor) else repr(v)
    return out


def state_of(w, var, t=None):
    if var == "S":
        return w.S.clone()
    if var == "r":
        return w.r.clone()
    if var == "w":
        return w.w.clone()
    if var == "E":
        return w.E.clone()
    if var == "inflight":                 # [B, N, LM*C*P + LM*C]
        return torch.cat([w.Msum.permute(1, 2, 0, 3, 4).flatten(2),
                          w.Mcnt.permute(1, 2, 0, 3).flatten(2)], 2)
    raise KeyError(var)


def _copy_state(src: World, dst: World):
    for k, v in dst.state_arrays().items():
        v.copy_(getattr(src, k))
    dst.t_dev.fill_(int(src.t_dev))
    dst.t = src.t
    dst.last_emit.copy_(src.last_emit)


class Harness:
    """Reference (correct) harness: the arm's own code, done right."""
    label = "reference"

    def seeds_for(self, arm, seeds, is_normal):
        return list(seeds)

    def ctrl_for(self, kw):
        return Controls(**kw)

    def targets_for(self, arm, ep, is_normal):
        return ep.y

    def run(self, ph0: Physics, genome, env, arm: Arm, seeds=SEEDS, record=False,
            shadow=False, is_normal=None, extra_hooks=None) -> RunOut:
        t_start = time.time()
        COST["runs"] += 1 + (1 if shadow else 0)
        is_normal = (arm is NORMAL) if is_normal is None else is_normal
        ph = ph0.replace(**arm.phys) if arm.phys else ph0
        sd = self.seeds_for(arm, seeds, is_normal)
        ep = envs.build(ph, env, sd)
        kw = arm.ctrl(env, ep)
        ctrl = self.ctrl_for(kw)
        ws = [sd[m - (m % 2)] for m in range(len(sd))]
        g = np.repeat(genome[None], len(sd), axis=0)
        w = World(ph, g, ws, device=DEV, ctrl=ctrl, schedule=ep.schedule)
        hook = arm.hook() if arm.hook else None
        sh = None
        if shadow:
            sh = World(ph0, g, ws, device=DEV, ctrl=Controls(), schedule=ep.schedule)
        rec, applied, aw = [], 0, np.zeros(len(sd), bool)
        for t in range(env.T()):
            if sh is not None:
                _copy_state(w, sh)
            if record == "delivered":
                slot = t % w.LM
                keep = 1
                if ctrl.drop_packets_at:
                    keep = 0 if w._drop_tab[min(t, w._Tc)] else 1
                rec.append(torch.cat([w.Msum[slot].flatten(1), w.Mcnt[slot].flatten(1)], 1) * keep)
            w.step()
            if hook is not None:
                hook(w, t, ep)
            if extra_hooks and t in extra_hooks:
                extra_hooks[t](w)
            if sh is not None:
                sh.step()
                dif = torch.zeros(len(sd), dtype=torch.bool)
                for k, v in w.state_arrays().items():
                    o = getattr(sh, k)
                    if k in ("Msum", "Mcnt"):
                        dif |= (v != o).flatten(2).any(-1).any(0)
                    else:
                        dif |= (v != o).reshape(len(sd), -1).any(-1)
                dif |= (w.trace[t] != sh.trace[t]).any(-1)
                applied += int(dif.sum())
                aw |= dif.numpy()
            if record and record != "delivered":
                rec.append(state_of(w, record))
        trace = w.trace.cpu().numpy()
        y = self.targets_for(arm, ep, is_normal)
        ep2 = envs.Episode(ep.schedule, ep.ro_tick, ep.ro_slot, y, ep.scored, ep.meta)
        acc = envs.score(ep2, trace)
        dg = []
        for i, d in enumerate(w.digest(per_world=True)):
            h = hashlib.sha256(d.encode())
            h.update(trace[:, i].tobytes())
            dg.append(h.hexdigest()[:16])
        man = {
            "physics": w.ph.to_dict(), "genome": _sha(w.genome), "ws": [int(x) for x in ws],
            "sense_idx": _sha(ep.schedule.sense_idx), "sense_val": _sha(ep.schedule.sense_val),
            "read_idx": _sha(ep.schedule.read_idx), "y": _sha(y), "scored": _sha(ep.scored),
            "ro_tick": _sha(ep.ro_tick), "ctrl": _ctrl_manifest(w.ctrl),
            "hook": (hook.kind if hook is not None else None),
        }
        if hook is not None:
            self_hits = hook.hits
        else:
            # what the harness BELIEVES it applied, from its own spec
            self_hits = sum(len(v) if isinstance(v, tuple) else 1 for k, v in kw.items()
                            if isinstance(v, np.ndarray) or v not in (False, (), None, -1))                 + len(arm.phys)
        return RunOut(trace, acc, acc.reshape(-1, 2).mean(-1), dg, man, rec, self_hits,
                      applied if shadow else None, int(aw.sum()) if shadow else None, ep2,
                      time.time() - t_start)


OLD_FIELDS = ("zero_comm", "shuffle_dest", "shuffle_time", "randomize_payload",
              "freeze_routing", "no_adapt", "reset_state_at", "reset_state_mask",
              "drop_packets_at", "distractor_chan")


class UnwiredHarness(Harness):
    """[2a] Builds Controls from a pre-C1b field whitelist: freeze_rule is
    accepted by the spec and silently never reaches the World."""
    label = "unwired"

    def ctrl_for(self, kw):
        return Controls(**{k: v for k, v in kw.items() if k in OLD_FIELDS})


class KeyedTargetHarness(Harness):
    """[2b] Non-normal arms score against y * key (a per-trial key drawn from
    the arm label): the arms score different targets."""
    label = "keyed_targets"

    def targets_for(self, arm, ep, is_normal):
        if is_normal:
            return ep.y
        g = np.random.default_rng(zlib.crc32(arm.name.encode()))
        key = np.where(g.random(ep.y.shape[1]) < 0.5, -1, 1)
        return ep.y * key[None, :]


class LabelSeedHarness(Harness):
    """[3a] Non-normal arms draw their worlds from the arm label (no common
    random numbers between an arm and its control)."""
    label = "label_seeds"

    def seeds_for(self, arm, seeds, is_normal):
        if is_normal:
            return list(seeds)
        return assays.world_seeds(rng.H_int(NS, zlib.crc32(arm.name.encode())), len(seeds))


# ======================================================================= footprints
def _mid(env):
    return list(c1b.ticks(env)["mid"])


def foot_all(env, ep, ph):
    return list(range(env.T())), None


def foot_ticks(fn):
    return lambda env, ep, ph: (fn(env), None)


def sensor_mask_per_world(ep, N):
    m = np.zeros((ep.schedule.sense_idx.shape[0], N), bool)
    for b, s in enumerate(ep.schedule.sense_idx[:, 0].numpy()):
        m[b, s] = True
    return m


def sensor_mask_world0(ep, N):          # BUG [mis-target]: world 0's sensor everywhere
    m = np.zeros((ep.schedule.sense_idx.shape[0], N), bool)
    m[:, int(ep.schedule.sense_idx[0, 0])] = True
    return m


# ======================================================================= fixtures
@dataclasses.dataclass
class Fixture:
    fid: str
    truth: str          # BROKEN / VALID
    shape: str
    ph: Physics
    env: envs.EnvSpec
    specimen: str       # plant name in SPECIMENS
    arm: Arm
    harness: Harness
    twin: str
    claim: str


SPEC_GENOMES = {
    "relay_flood": lambda ph: plants.plant("relay_flood", ph),
    "flood_rwrite": flood_rwrite,
    "flood_rdecor": flood_rdecor,
    "route_relay": lambda ph: bc(plants.route_relay(ph), ph),
    "rule_switch_hold": plants.rule_switch_hold,
    "rule_decor": rule_decor,
    "echo_hold": lambda ph: bc(plants.echo_hold(ph), ph),
    "hold_latch": lambda ph: plants.plant("hold_latch", ph),
    "latch_listen": latch_listen,
}


def fixtures():
    REF = Harness()
    da = plants.c1b_da_physics()
    echo = plants.c1b_echo_physics()
    latch_ph = echo.replace(prog_len=12, payload_width=1)
    rule_ph = plants.c1b_rule_physics()
    route_ph = plants.c1b_route_physics()
    inert_ph = da.replace(plastic_route=1, adapt_shift=0, prog_len=14)
    sat_ph = da.replace(c_op=1, c_emit=5, e_income=12, e_max=1000)

    def dw(key):
        return lambda env, ep: {"drop_packets_at": c1b.drop_windows(env)[key]}

    def dfoot(key):
        return lambda env, ep, ph: (list(c1b.drop_windows(env)[key]), None)

    win_c1 = Arm("drop_window_c1", dw("drop_window_c1"), var="delivered",
                 foot_fn=dfoot("drop_window_c1"), window=True)
    win_ok = Arm("drop_window_corrected", dw("drop_window_corrected"), var="delivered",
                 foot_fn=dfoot("drop_window_corrected"), window=True)
    frz_route = Arm("freeze_routing", lambda e, p: {"freeze_routing": True}, var="w",
                    foot_fn=foot_all, pathway="routing")
    frz_rule = Arm("freeze_rule", lambda e, p: {"freeze_rule": True}, var="r",
                   foot_fn=foot_all, pathway="rule")
    reset_mid = Arm("reset_S_mid", lambda e, p: {"reset_state_at": tuple(_mid(e))}, var="S",
                    foot_fn=foot_ticks(_mid), pathway="S")
    ro = lambda e: list(c1b.ticks(e)["ro"])
    reset_ro = Arm("reset_S_readout", lambda e, p: {"reset_state_at": tuple(ro(e))}, var="S",
                   foot_fn=foot_ticks(ro), pathway="S")

    def masked(name, fn, N):
        def cf(e, ep):
            return {"reset_state_at": tuple(_mid(e)), "reset_state_mask": fn(ep, N)}

        def ff(e, ep, ph):
            return _mid(e), fn(ep, N)
        return Arm(name, cf, var="S", foot_fn=ff, pathway="S")

    def cond_arm(kind):
        def ff(e, ep, ph):
            return None, kind          # resolved from the condition on the twin run
        return Arm("cond_flush_" + kind, None, hook=lambda: CondFlush(kind), var="inflight",
                   foot_fn=ff, pathway="transport")

    cut = lambda v, name: Arm(name, None, phys={"e_income": v}, var="E", foot_fn=foot_all,
                              pathway="energy")
    F = [
        Fixture("WIN-B", "BROKEN", "mistimed window", da, RELAY_DA, "relay_flood", win_c1, REF,
                "WIN-V", "drop over [t0,ro) null -> packets not needed"),
        Fixture("WIN-V", "VALID", "mistimed window", da, RELAY_DA, "relay_flood", win_ok, REF,
                "WIN-B", "drop over [t0,ro] kills -> packets carry"),
        Fixture("INERT-B", "BROKEN", "inert channel", inert_ph, RELAY_DA, "flood_rwrite",
                frz_route, REF, "INERT-V", "freeze_routing null -> routing not used"),
        Fixture("INERT-V", "VALID", "inert channel", route_ph, RELAY_ROUTE, "route_relay",
                frz_route, REF, "INERT-B", "freeze_routing kills -> routing carries"),
        Fixture("UNWIRED-B", "BROKEN", "unwired switch", rule_ph, HOLD, "rule_switch_hold",
                frz_rule, UnwiredHarness(), "UNWIRED-V", "freeze_rule null -> rule not used"),
        Fixture("UNWIRED-V", "VALID", "unwired switch", rule_ph, HOLD, "rule_switch_hold",
                frz_rule, REF, "UNWIRED-B", "freeze_rule kills -> rule carries"),
        Fixture("TARGET-B", "BROKEN", "wrong target", echo, HOLD, "echo_hold", reset_mid,
                KeyedTargetHarness(), "TARGET-V", "reset_S kills -> S carries"),
        Fixture("TARGET-V", "VALID", "wrong target", echo, HOLD, "echo_hold", reset_mid, REF,
                "TARGET-B", "reset_S null -> S not needed (true null)"),
        Fixture("DEAD-B", "BROKEN", "dead branch", echo, HOLD, "echo_hold", cond_arm("never"),
                REF, "COND-V", "conditional flush null -> in-flight not needed"),
        Fixture("SEED-B", "BROKEN", "condition never met + label seeds", echo, HOLD, "echo_hold",
                cond_arm("never"), LabelSeedHarness(), "COND-V", "conditional flush reading"),
        Fixture("PROBE-B", "BROKEN", "probe side effect", echo, HOLD, "echo_hold",
                cond_arm("probe"), REF, "COND-V", "conditional flush kills -> in-flight carries"),
        Fixture("COND-V", "VALID", "conditional arm", echo, HOLD, "echo_hold", cond_arm("fires"),
                REF, "DEAD-B", "conditional flush kills -> in-flight carries"),
        Fixture("MASK-B", "BROKEN", "mis-targeted site", latch_ph, HOLD, "hold_latch",
                masked("reset_S_sensor", sensor_mask_world0, latch_ph.n_sites), REF, "MASK-V",
                "reset of the sensor's S null -> latch not in S"),
        Fixture("MASK-V", "VALID", "mis-targeted site", latch_ph, HOLD, "hold_latch",
                masked("reset_S_sensor", sensor_mask_per_world, latch_ph.n_sites), REF, "MASK-B",
                "reset of the sensor's S kills -> latch in S"),
        Fixture("FORCED-B", "BROKEN", "forced by readout", echo, HOLD, "echo_hold", reset_ro, REF,
                "FORCED-V", "reset_S kills -> S carries"),
        Fixture("FORCED-V", "VALID", "forced by readout", latch_ph, HOLD, "hold_latch", reset_mid,
                REF, "FORCED-B", "reset_S kills -> S carries"),
        Fixture("SAT-B", "BROKEN", "saturated gate", sat_ph, RELAY_DA, "relay_flood",
                cut(11, "income_cut_11"), REF, "SAT-V", "income cut null -> energy not limiting"),
        Fixture("SAT-V", "VALID", "saturated gate", sat_ph, RELAY_DA, "relay_flood",
                cut(0, "income_cut_0"), REF, "SAT-B", "income cut kills -> energy gates relaying"),
        Fixture("V0-WIN", "VALID", "true null (arrivals unused)", echo.replace(prog_len=30), HOLD,
                "latch_listen", Arm("drop_window_corrected", dw("drop_window_corrected"),
                                    var="delivered", foot_fn=dfoot("drop_window_corrected"),
                                    window=True), REF, "-", "drop null -> arrivals not used"),
        Fixture("V0-ROUTE", "VALID", "true null (w read, unused)", route_ph, RELAY_ROUTE,
                "flood_rdecor", frz_route, REF, "-", "freeze_routing null -> routing not used"),
        Fixture("V0-RULE", "VALID", "true null (r read, indifferent)", rule_ph.replace(prog_len=12),
                HOLD, "rule_decor", frz_rule, REF, "-", "freeze_rule null -> rule not used"),
    ]
    return F


def genome_of(fx: Fixture):
    return SPEC_GENOMES[fx.specimen](fx.ph)


# ======================================================================= readings
def reading(n: RunOut, a: RunOut) -> dict:
    d = a.pairs - n.pairs
    m, lo, hi = c1b.ci(d)
    nm = c1b.ci(n.pairs)
    am = c1b.ci(a.pairs)
    eff = m <= -c1b.DROP_PT and lo < c1b.DROP_LO
    nul = lo >= c1b.INTACT_LO
    return {"normal": nm, "arm": am, "diff": (m, lo, hi),
            "reading": "EFFECT" if eff else ("NULL" if nul else "AMBIG")}
