"""Known-answer tests for prometheus.ananke.audit.trace (H-INST test_pte_trace.py, promoted), built on
prometheus/ananke/plants.py.

Every test has a POSITIVE control (the answer is known by construction), a
NEGATIVE control (the primitive must report absence), and a MUST-FAIL input
(a wrong input on which the same assertion would fail, checked inline).
CPU only.

Run (from the worktree root):
  CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python -m pytest \
      roles/Ananke/research/harvest/H-INST/test_pte_trace.py -q -p no:cacheprovider
"""
from __future__ import annotations

import os

if not os.environ.get("CUDA_VISIBLE_DEVICES"):      # an EMPTY value does not hide the GPU on this host
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import numpy as np  # noqa: E402
import pytest  # noqa: E402
import torch  # noqa: E402

from prometheus.ananke.audit import trace as P  # noqa: E402
from prometheus.ananke import assays, c1b, envs, lens, plants  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402

SEEDS = assays.world_seeds(0x7E57, 16)
M = len(SEEDS)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)
TK = c1b.ticks(HOLD)
K = 5                                   # trial under study
T0 = K * HOLD.period()
BI = torch.arange(M)


def echo():
    ph = plants.c1b_echo_physics()
    return ph, plants.echo_hold(ph)


def latch():
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    return ph, plants.plant("hold_latch", ph)


def null():
    ph = plants.c1b_echo_physics()
    return ph, plants.plant("null", ph)


def flush(w):
    w.Msum.zero_()
    w.Mcnt.zero_()


def classes(rt):
    u, c = np.unique(rt["path"], return_counts=True)
    return {str(a): int(b) for a, b in zip(u, c)}


# =============================================================== 1 diff_trace
@pytest.fixture(scope="module")
def echo_tw():
    ph, g = echo()
    return P.twin_trace(ph, g, HOLD, SEEDS, trial=K)


@pytest.fixture(scope="module")
def latch_tw():
    ph, g = latch()
    return P.twin_trace(ph, g, HOLD, SEEDS, trial=K)


def test_closure_invariant_and_fault_injection(echo_tw):
    """Every new site difference is explained by a differing arrival / sense
    input, and every new mailbox difference by a recorded edge. A tracer that
    recomputes edges one tick late must break the closure."""
    dt, _ = echo_tw
    assert dt.edges_exact and len(dt.edges) > 0
    assert dt.unexplained_site == 0 and dt.unexplained_flight == 0
    ph, g = echo()
    bad, _ = P.twin_trace(ph, g, HOLD, SEEDS, trial=K, _fault_edge_tick=1)      # MUST-FAIL input
    assert bad.unexplained_flight > 0


@pytest.mark.parametrize("variant", ["p2_aloha", "async", "sample_lossy_jitter", "plastic_route"])
def test_closure_holds_across_physics(variant):
    base = plants.c1b_echo_physics()
    relay = envs.EnvSpec(family="RELAY", d=3, delta=8, cue_len=2, trials=12)
    if variant == "p2_aloha":
        ph, env = base.replace(update_period=2, cap=1, collision="aloha"), HOLD
        g = plants.echo_hold(ph)
    elif variant == "async":
        ph, env = base.replace(update_mode="async", update_p=0.5), HOLD
        g = plants.echo_hold(ph)
    elif variant == "sample_lossy_jitter":
        ph = base.replace(dest_mode="sample", fanout=2, lat_jitter=2, loss=0.2, update_period=2, prog_len=28)
        env, g = relay, plants.plant("relay_flood", ph)
    else:
        ph = plants.c1b_route_physics()
        env, g = envs.EnvSpec(family="RELAY", d=2, delta=8, cue_len=4, trials=12), plants.route_relay(ph)[None]
    dt, _ = P.twin_trace(ph, g, env, SEEDS, trial=3)
    assert len(dt.edges) > 0
    assert dt.unexplained_site == 0 and dt.unexplained_flight == 0
    bad, _ = P.twin_trace(ph, g, env, SEEDS, trial=3, _fault_edge_tick=1)      # MUST-FAIL input
    assert bad.unexplained_flight > 0


def test_edges_and_cone_known_answer_echo(echo_tw):
    """echo_hold: the sensor s emits the cue at t0 to s+-1 (delay 5); both relay
    it back at t0+5; the echo lands on s at the readout t0+10. The backward cone
    of the readout is exactly those 4 edges with one ENV leaf; at mid-gap the
    whole cone is in flight, nothing is held."""
    dt, ep = echo_tw
    N = plants.c1b_echo_physics().n_sites
    for b in (0, 5, 11):
        s = int(ep.schedule.read_idx[b, 0])
        ro = int(ep.ro_tick[b, K])
        c = dt.cone(b, s, ro)
        L, R = (s - 1) % N, (s + 1) % N
        assert c["edges"] == {(s, T0, L, T0 + 5), (s, T0, R, T0 + 5), (L, T0 + 5, s, ro), (R, T0 + 5, s, ro)}
        assert c["leaves"] == {("ENV", T0, s)}
        cut = dt.cone_cut(c, TK["mid"][K])
        assert cut["held"] == set() and cut["flight"] == {(L, T0 + 5, s, ro), (R, T0 + 5, s, ro)}
        # NEGATIVE: a far site never differs -> empty cone; MUST-FAIL: the tick before the echo lands
        far = dt.cone(b, (s + 12) % N, ro)
        assert far["nodes"] == set() and far["edges"] == set()
        assert dt.cone(b, s, ro - 1)["edges"] != c["edges"]


def test_cone_cut_latch_is_held_not_in_flight(latch_tw):
    dt, ep = latch_tw
    b = 3
    s = int(ep.schedule.read_idx[b, 0])
    c = dt.cone(b, s, int(ep.ro_tick[b, K]))
    cut = dt.cone_cut(c, TK["mid"][K])
    assert cut["held"] == {s} and cut["flight"] == set() and c["edges"] == set()
    assert len(dt.edges) == 0


def test_local_vs_transported(echo_tw, latch_tw):
    """hold_latch (sensor = actuator, no packets): LOCAL. echo_hold (bit only in
    flight): TRANSPORTED. relay_flood (sensor != actuator): TRANSPORTED.
    null genome: NO_DIFF (absence) and no output difference."""
    dt, ep = latch_tw
    rl = dt.readout_table(ep, K)
    assert rl["output_diff"].all() and classes(rl) == {"LOCAL": M}
    dt, ep = echo_tw
    re_ = dt.readout_table(ep, K)
    assert re_["output_diff"].all() and classes(re_) == {"TRANSPORTED": M}
    assert classes(rl) != classes(re_)                                          # MUST-FAIL: the classes differ
    ph = plants.c1b_da_physics()
    env = envs.EnvSpec(family="RELAY", d=1, delta=4, cue_len=2, trials=12, iti=50)
    dtf, epf = P.twin_trace(ph, plants.plant("relay_flood", ph), env, SEEDS, trial=2)
    rf = dtf.readout_table(epf, 2)
    assert rf["output_diff"].all() and classes(rf) == {"TRANSPORTED": M}
    ph, g = null()
    dtn, epn = P.twin_trace(ph, g, HOLD, SEEDS, trial=K)
    rn = dtn.readout_table(epn, K)
    assert not rn["output_diff"].any() and classes(rn) == {"NO_DIFF": M} and len(dtn.edges) == 0


def test_write_authority(echo_tw):
    """rule_switch_hold writes r from SENSE only (receiver-local authority);
    route_relay writes w from SENSE at the sensor and S from arrivals at the
    actuator; echo_hold never writes r, w or Kp differently (absence)."""
    ph = plants.c1b_rule_physics()
    dt, _ = P.twin_trace(ph, plants.rule_switch_hold(ph), HOLD, SEEDS, trial=K)
    cc = dt.component_causes()
    assert set(cc["r"]) == {"SENSED"}
    ph = plants.c1b_route_physics()
    env = envs.EnvSpec(family="RELAY", d=2, delta=8, cue_len=4, trials=12)
    dt, _ = P.twin_trace(ph, plants.route_relay(ph)[None], env, SEEDS, trial=3)
    cr = dt.component_causes()
    assert set(cr["w"]) == {"SENSED"} and set(cr["S"]) == {"TRANSPORTED"}
    ce = echo_tw[0].component_causes()
    assert not ({"r", "w", "Kp"} & set(ce))                                    # NEGATIVE: absence
    assert set(ce["S"]) == {"TRANSPORTED"} and set(ce["S"]) != set(cc["r"])  # MUST-FAIL: not SENSED


# ====================================================== 2 reach certificate
def _latch_hooks():
    ph, g = latch()
    ep = envs.build(ph, HOLD, SEEDS)
    ridx = ep.schedule.read_idx[:, 0]

    def s1_readout(w):                    # an unused register at the readout site
        w.S[BI, ridx, 1] += 7

    def s0_elsewhere(w):                  # every site except the readout
        m = torch.ones(M, w.N, dtype=torch.bool)
        m[BI, ridx] = False
        w.S[..., 0][m] += 7

    return ph, g, {"swap_S": lambda w: lens.swap(w, ["S"]), "s1_readout": s1_readout,
                   "s0_elsewhere": s0_elsewhere, "swap_w": lambda w: lens.swap(w, ["w"])}


def test_reach_certificate_four_verdicts():
    ph, g, H = _latch_hooks()
    mid = TK["mid"][K]
    r = {n: P.reach_certificate(ph, g, HOLD, SEEDS, {mid: h}, K) for n, h in H.items()}
    assert r["swap_S"]["verdict"] == "REACHED_OUTPUT" and r["swap_S"]["path"] == {"LOCAL": M}
    assert r["s1_readout"]["verdict"] == "ABSORBED" and r["s1_readout"]["touched"] == 1.0
    assert r["s0_elsewhere"]["verdict"] == "NOT_REACHED" and r["s0_elsewhere"]["applied"] == 1.0
    assert r["swap_w"]["verdict"] == "UNAPPLIED"                                # NEGATIVE: w identical
    assert len({v["verdict"] for v in r.values()}) == 4                        # MUST-FAIL: verdicts differ
    for v in r.values():
        assert v["unexplained_site"] == 0 and v["unexplained_flight"] == 0


def test_verify_reach_applied_count_is_not_reach():
    """lens.applied_ticks (the applied half of lens.verify_reach) counts ANY
    state difference anywhere: an edit to non-readout sites of a purely local
    latch reads 'applied' on every tick, so verify_reach can only say
    NOT_VERIFIED; the certificate proves the edit never reached the readout."""
    ph, g, H = _latch_hooks()
    mid = TK["mid"][K]
    hooks = {mid: H["s0_elsewhere"]}
    assert lens.applied_ticks(ph, g, HOLD, SEEDS, hooks=hooks) > 0
    assert lens.verify_reach((ph, g, HOLD), None, SEEDS, hooks=hooks)["reach"] == "NOT_VERIFIED"
    assert P.reach_certificate(ph, g, HOLD, SEEDS, hooks, K)["verdict"] == "NOT_REACHED"
    # MUST-FAIL input: the same count on a hook that does reach gives REACHED_OUTPUT, not NOT_REACHED
    assert P.reach_certificate(ph, g, HOLD, SEEDS, {mid: H["swap_S"]}, K)["verdict"] == "REACHED_OUTPUT"


def test_reach_certificate_window_miss_echo():
    """Mid-gap flush reaches the echo readout through transport; the same flush
    after the readout tick cannot reach it (applied, NOT_REACHED)."""
    ph, g = echo()
    r_mid = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][K]: flush}, K)
    assert r_mid["verdict"] == "REACHED_OUTPUT" and set(r_mid["path"]) == {"TRANSPORTED"}
    r_late = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["ro"][K]: flush}, K)
    assert r_late["verdict"] == "NOT_REACHED" and r_late["applied"] == 1.0
    assert r_late["verdict"] != r_mid["verdict"]                               # MUST-FAIL


def test_self_maintained_machinery():
    """sham_positive_hold keeps its relays armed with packets in flight across
    the ITI: a flush at trial 0's ITI reaches LATER trials' readouts by transport.
    echo_hold has no machinery in flight at the ITI: the same flush is UNAPPLIED."""
    ph = plants.c1b_echo_physics().replace(prog_len=64)
    it = {TK["iti"][0]: flush}
    for k in (1, 3):
        rs = P.reach_certificate(ph, plants.sham_positive_hold(ph), HOLD, SEEDS, it, k)
        assert rs["verdict"] == "REACHED_OUTPUT" and set(rs["path"]) == {"TRANSPORTED"}
        re_ = P.reach_certificate(ph, plants.echo_hold(ph), HOLD, SEEDS, it, k)
        assert re_["verdict"] == "UNAPPLIED" and re_["verdict"] != rs["verdict"]


# ======================================================= 3 ProvenanceWorld
def _echo_groups(ep, N):
    s = ep.schedule.sense_idx[:, 0].numpy()
    gr = np.full((M, N), 2)
    gr[np.arange(M), (s - 1) % N] = 0
    gr[np.arange(M), (s + 1) % N] = 1
    return gr


def _run_checked(w, T):
    worst, inbox = {}, 0
    for _ in range(T):
        w.step()
        for k, v in w.check().items():
            worst[k] = max(worst.get(k, 0), v)
        inbox += int(w.Icnt.abs().sum())
    return worst, inbox


@pytest.mark.parametrize("variant", ["plain", "p2", "p2_aloha", "drop", "flush", "reset_inbox_p3", "async"])
def test_provenance_tags_sum_exactly(variant):
    base = plants.c1b_echo_physics()
    ph, ctrl = {
        "plain": (base, Controls()),
        "p2": (base.replace(update_period=2), Controls()),
        "p2_aloha": (base.replace(update_period=2, cap=1, collision="aloha"), Controls()),
        "drop": (base, Controls(drop_packets_at=(10, 11, 40))),
        "flush": (base, Controls(flush_inflight_at=(7, 33))),
        "reset_inbox_p3": (base.replace(update_period=3),
                           Controls(reset_state_at=(20, 21, 50), reset_parts=("S", "inbox"))),
        "async": (base.replace(update_mode="async", update_p=0.5), Controls()),
    }[variant]
    g = P.genome_batch(plants.echo_hold(ph), M)
    ep = envs.build(ph, HOLD, SEEDS)
    gr = np.arange(ph.n_sites)[None].repeat(M, 0) % 3
    w = P.ProvenanceWorld(ph, g, P.mirrored_ws(SEEDS), schedule=ep.schedule, ctrl=ctrl, groups=gr,
                          n_groups=3, epoch_bounds=(30, 60))
    ref = World(ph, g, P.mirrored_ws(SEEDS), device="cpu", schedule=ep.schedule, ctrl=ctrl)
    worst, inbox = _run_checked(w, 100)
    ref.run(100, graph=False)
    assert set(worst.values()) == {0}, worst
    assert w.digest() == ref.digest()                        # tagging never perturbs physics
    if variant in ("p2", "reset_inbox_p3", "async"):
        assert inbox > 0                                     # the inbox leg is exercised
    bad = gr.copy()
    bad[:, 1] = 7                                            # MUST-FAIL: not a partition (id 7 untracked)
    wb = P.ProvenanceWorld(ph, g, P.mirrored_ws(SEEDS), schedule=ep.schedule, ctrl=ctrl, groups=bad, n_groups=3)
    worst_b, _ = _run_checked(wb, 100)
    assert max(worst_b.values()) > 0


def test_provenance_attribution_echo():
    """Mail to the echo readout (the sensor) comes only from its two neighbours;
    the rest of the ring (incl. the sensor itself) contributes nothing."""
    ph, g = echo()
    ep = envs.build(ph, HOLD, SEEDS)
    gr = _echo_groups(ep, ph.n_sites)
    w = P.ProvenanceWorld(ph, P.genome_batch(g, M), P.mirrored_ws(SEEDS), schedule=ep.schedule, groups=gr,
                          n_groups=3)
    mass = np.zeros(3)
    for _ in range(HOLD.T()):
        w.step()
        mass += w.Fcnt.sum((0, 1, 2, 4)).numpy()
    assert mass[0] > 0 and mass[1] > 0 and mass[2] == 0                      # NEGATIVE: rest absent
    far = ((ep.schedule.read_idx[:, :1] + 12) % ph.n_sites)
    wf = P.ProvenanceWorld(ph, P.genome_batch(g, M), P.mirrored_ws(SEEDS), schedule=ep.schedule, groups=gr,
                           n_groups=3, recipients=far)
    mf = np.zeros(3)
    for _ in range(HOLD.T()):
        wf.step()
        mf += wf.Fcnt.sum((0, 1, 2, 4)).numpy()
    assert mf[0] == 0 and mf[1] == 0                                          # MUST-FAIL: wrong recipient


def test_provenance_follow_group_and_epoch():
    """Swapping BOTH neighbours' echoes FLIPs every readout; one neighbour alone
    is partial (the sum cancels); the rest's contribution is a no-op. By
    emission epoch, the echo (emitted at t0+5) carries the bit and older mail
    carries nothing."""
    ph, g = echo()
    ep = envs.build(ph, HOLD, SEEDS)
    gr = _echo_groups(ep, ph.n_sites)
    mid = TK["mid"][K]
    r = P.provenance_follow(ph, g, HOLD, SEEDS, K, mid, gr, 3,
                            {"L": [0], "R": [1], "LR": [0, 1], "rest": [2], "none": []})
    assert set(r["check"].values()) == {0} and r["eligible"] == M
    assert r["LR"]["follow"] == 1.0
    assert r["rest"]["identical"] and r["none"]["identical"]                   # NEGATIVE
    assert r["L"]["follow"] < 1.0 and r["R"]["follow"] < 1.0                   # MUST-FAIL: one is not both
    re_ = P.provenance_follow(ph, g, HOLD, SEEDS, K, mid, gr, 3, {"old": [0, 1, 2], "echo": [3, 4, 5]},
                              epoch_bounds=(T0 + 5,))
    assert re_["echo"]["follow"] == 1.0 and re_["old"]["identical"]


def test_all_keys_swap_equals_array_swap():
    """With every key selected, provenance_swap equals swapping the recipients'
    whole mail + inbox between partners (period 2: the inbox is live). A key
    subset that leaves tagged mass behind must NOT equal it."""
    ph = plants.c1b_echo_physics().replace(update_period=2)
    g = P.genome_batch(plants.echo_hold(ph), M)
    ep = envs.build(ph, HOLD, SEEDS)
    N = ph.n_sites
    gr = np.arange(N)[None].repeat(M, 0) % 3
    allsites = np.arange(N)[None].repeat(M, 0)                # recipients: every site
    w = P.ProvenanceWorld(ph, g, P.mirrored_ws(SEEDS), schedule=ep.schedule, groups=gr, n_groups=3,
                          recipients=allsites, epoch_bounds=(T0,))
    for _ in range(T0):
        w.step()
    while int(w.Icnt.sum()) == 0 and w.t < HOLD.T():        # first tick with live inbox mail
        w.step()
    tags = w.tags()
    assert int(tags["Icnt"].sum()) > 0
    rec = w.rec
    bi = torch.arange(M)[:, None]
    p = torch.arange(M) ^ 1

    def copy():
        c = World(ph, g, P.mirrored_ws(SEEDS), device="cpu", schedule=ep.schedule)
        for n, v in World.state_arrays(w).items():
            getattr(c, n).copy_(v)
        return c

    a = copy()
    P.provenance_swap(a, tags, range(w.K))
    b = copy()
    b.Msum[:, bi, rec] = w.Msum[:, bi, rec][:, p]
    b.Mcnt[:, bi, rec] = w.Mcnt[:, bi, rec][:, p]
    b.Acc_sum[bi, rec] = w.Acc_sum[bi, rec][p]
    b.Acc_cnt[bi, rec] = w.Acc_cnt[bi, rec][p]
    assert a.digest() == b.digest()
    c = copy()
    live = [k for k in range(w.K) if int(tags["Fcnt"][..., k, :].abs().sum() + tags["Icnt"][..., k, :].abs().sum())]
    assert len(live) >= 2
    P.provenance_swap(c, tags, live[:1])                                       # MUST-FAIL: subset
    assert c.digest() != b.digest()
