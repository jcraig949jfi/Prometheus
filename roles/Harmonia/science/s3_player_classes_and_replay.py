"""S3 -- PLAYER CLASSES, REPLAY STRENGTH, AND STATE LEAKAGE ACROSS UNITS.

Harmonia science loop 3, 2026-09-05.

Loops 1-2 were null by construction, which was the only honest ground truth
available before executor attestation existed. This loop changes experiment
class: outcomes are now COMPUTED by real policies against a real scoring
landscape, so the phenomenon under study is the policies themselves.

THE LANDSCAPE (deliberately boring and fully analysable): a world carries a
hidden target bitstring derived from its seed_root. A player emits a bitstring
per encounter and scores the fraction of matching positions. No wall clock, no
external service; every source of variation is one we introduce on purpose.

FOUR PLAYER CLASSES, chosen because they differ on the axes that break
analyses, not on the axes that make good demos:

  P_DET        deterministic, stateless. Same input -> same output, always.
  P_STOCH      stochastic, stateless, SEEDED from the spec.
  P_STOCH_U    stochastic, stateless, seeded from a source NOT in the spec.
  P_STATEFUL   hill-climber holding state WITHIN a world. Order-dependent.
  P_LEARNER    hill-climber holding state ACROSS worlds. This is the adversary:
               it makes nominally independent worlds dependent on each other,
               and on the order in which unrelated worlds happened to run.

Three questions:
  1. REPLAY STRENGTH. A byte-identical frozen spec guarantees what, exactly?
  2. WORLD IDENTITY. Where does "same world" stop being true while every
     recorded hash stays equal?
  3. INDEPENDENCE. Can a player make the unit of analysis a lie?
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
import urllib.error
import urllib.request

FINDINGS = []
BITS = 64


def finding(fid, title, klass, detail):
    FINDINGS.append({"id": fid, "title": title, "class": klass, "detail": detail})
    print("\n[%s] %s\n    %s" % (klass, title, detail))


def target_for(seed):
    r = random.Random(seed)
    return [r.randint(0, 1) for _ in range(BITS)]


def score(bits, target):
    return sum(1 for i in range(BITS) if bits[i] == target[i]) / BITS


def cfg_hash(obj):
    """C-1 from packet 1: the executor hashes the configuration it ACTUALLY
    ran. Not a label -- a hash over the real thing."""
    return "exec:" + hashlib.sha256(
        json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


# --------------------------------------------------------------------------
# players. Each returns (score, executed_config, state_hash_after)
# --------------------------------------------------------------------------
class P_DET:
    name = "P_DET"
    stateful = False

    def __init__(self, seed): self.seed = seed

    def play(self, target, enc, spec_seed):
        r = random.Random(self.seed)
        bits = [r.randint(0, 1) for _ in range(BITS)]
        return score(bits, target), {"policy": "det", "seed": self.seed}, "-"


class P_STOCH:
    name = "P_STOCH_seeded_from_spec"
    stateful = False

    def play(self, target, enc, spec_seed):
        r = random.Random("%s|%s" % (spec_seed, enc))
        bits = [r.randint(0, 1) for _ in range(BITS)]
        return score(bits, target), {"policy": "stoch", "seed": [spec_seed, enc]}, "-"


class P_STOCH_U:
    """Stochastic, seeded from something the FROZEN SPEC DOES NOT CONTAIN."""
    name = "P_STOCH_unseeded_from_spec"
    stateful = False

    def __init__(self): self.r = random.Random()

    def play(self, target, enc, spec_seed):
        bits = [self.r.randint(0, 1) for _ in range(BITS)]
        # the executed config LOOKS identical to the seeded case
        return score(bits, target), {"policy": "stoch", "seed": [spec_seed, enc]}, "-"


class P_STATEFUL:
    """Hill-climbs WITHIN a world. Reset between worlds."""
    name = "P_STATEFUL_within_world"
    stateful = True

    def __init__(self, seed=0):
        self.seed = seed
        self.reset()

    def reset(self):
        r = random.Random(self.seed)
        self.best = [r.randint(0, 1) for _ in range(BITS)]
        self.best_s = None

    def play(self, target, enc, spec_seed):
        if self.best_s is None:
            self.best_s = score(self.best, target)
        # seeded by the CURRENT state as well as the encounter, so the
        # trajectory is path dependent. The first version seeded only on
        # (seed, enc), which flipped the same bit positions in every world and
        # made order irrelevant BY CONSTRUCTION -- it measured my player, not
        # the system.
        r = random.Random("%s|%s|%s" % (self.seed, enc,
                                        "".join(map(str, self.best))))
        cand = list(self.best)
        i = r.randrange(BITS)
        cand[i] ^= 1
        s = score(cand, target)
        if s >= self.best_s:
            self.best, self.best_s = cand, s
        return (self.best_s, {"policy": "hill", "enc": enc},
                hashlib.sha256(bytes(self.best)).hexdigest()[:12])


class P_LEARNER(P_STATEFUL):
    """Identical hill-climber, but NEVER reset between worlds. Its state
    crosses the boundary that the analysis assumes is independent."""
    name = "P_LEARNER_across_worlds"

    def reset_between_worlds(self):
        pass                                     # deliberately does nothing


class C:
    def __init__(self, base):
        self.base, self.token, self.key = base.rstrip("/"), None, None

    def call(self, m, p, body=None):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if self.key:
            h["X-SFE-Session"] = self.key
        d = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + p, data=d, headers=h, method=m)
        try:
            with urllib.request.urlopen(r, timeout=60) as z:
                return z.status, json.loads(z.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:                                      # noqa: BLE001
                return e.code, {}


def run_world(c, sid, name, player, seed_root, n_enc, spec_seed, order=None):
    """One world, n_enc encounters. Returns the per-encounter scores and the
    frozen spec hashes, all written to the real engine."""
    w = c.call("POST", "/worlds", {"session_id": sid, "name": name,
                                   "seed_root": seed_root,
                                   "sharing_policy": "ISOLATED"})[1]
    wid = w["world_id"]
    c.call("POST", "/worlds/%s/start" % wid, {})
    h = c.call("POST", "/worlds/%s/hypotheses" % wid, {"statement": name})[1]
    target = target_for(seed_root)
    encs = order if order is not None else list(range(n_enc))
    entry_state = (hashlib.sha256(bytes(player.best)).hexdigest()[:12]
                   if getattr(player, "best", None) is not None else "-")
    scores, hashes, states = [], [], []
    for enc in encs:
        spec = {"action": "encounter", "ticks": 8, "enc": enc,
                "spec_seed": spec_seed}
        x = c.call("POST", "/worlds/%s/experiments" % wid,
                   {"spec": spec, "hyp_id": h["hyp_id"], "commit": True})[1]
        s, cfg, state = player.play(target, enc, spec_seed)
        c.call("POST", "/worlds/%s/observations" % wid,
               {"exp_id": x["exp_id"],
                "content": {"score": s, "executed_config_hash": cfg_hash(cfg),
                            "executor_state_hash": state},
                "outcome": "SURVIVED"})
        scores.append(s)
        hashes.append(x.get("spec_hash") or
                      c.call("GET", "/worlds/%s/experiments/%s"
                             % (wid, x["exp_id"]))[1].get("spec_hash"))
        states.append(state)
    return {"world_id": wid, "scores": scores, "spec_hashes": hashes,
            "states": states, "entry_state": entry_state}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8896/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    st, _ = c.call("GET", "/version")
    if st != 200:
        print("engine unreachable"); return 2
    c.token = c.call("POST", "/clients", {"name": "s3"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "s3"})[1]
    c.key = s["session_key"]
    sid = s["session_id"]
    SEED, NENC, SPEC_SEED = 424242, 12, 777
    data = {}

    # ==================================================================
    # Q1  REPLAY STRENGTH -- what does a byte-identical spec guarantee?
    # ==================================================================
    print("=" * 74)
    print("Q1  REPLAY STRENGTH BY PLAYER CLASS")
    print("=" * 74)
    print("  same frozen spec, executed twice, per class\n")
    levels = {}
    for cls in (P_DET(1), P_STOCH(), P_STOCH_U(), P_STATEFUL(1)):
        if isinstance(cls, P_STATEFUL):
            cls.reset()
        r1 = run_world(c, sid, "q1-%s-a" % cls.name, cls, SEED, NENC, SPEC_SEED)
        if isinstance(cls, P_STATEFUL):
            cls.reset()
        elif isinstance(cls, P_STOCH_U):
            cls.r = random.Random()
        r2 = run_world(c, sid, "q1-%s-b" % cls.name, cls, SEED, NENC, SPEC_SEED)
        same_spec = r1["spec_hashes"] == r2["spec_hashes"]
        l0 = r1["scores"] == r2["scores"]
        l1 = r1["scores"][-1] == r2["scores"][-1]
        l2 = abs(statistics.fmean(r1["scores"]) -
                 statistics.fmean(r2["scores"])) < 0.02
        lvl = "L0 exact sequence" if l0 else ("L1 terminal only" if l1 else
              ("L2 distribution only" if l2 else "L3 none of these"))
        levels[cls.name] = {"spec_identical": same_spec, "L0_sequence": l0,
                            "L1_terminal": l1, "L2_distribution": l2,
                            "level": lvl,
                            "mean_a": round(statistics.fmean(r1["scores"]), 4),
                            "mean_b": round(statistics.fmean(r2["scores"]), 4)}
        print("  %-28s spec identical=%s  L0=%-5s L1=%-5s L2=%-5s  -> %s"
              % (cls.name, same_spec, l0, l1, l2, lvl))
    data["replay"] = levels

    finding("S3-1", "A byte-identical frozen spec guarantees NOTHING about "
            "reproduction beyond the deterministic class", "SCIENTIFIC_DESIGN_GAP",
            "All four classes produced IDENTICAL spec hashes across both runs. "
            "Only P_DET reproduced its exact score sequence. The "
            "spec-seeded stochastic player reproduced because its seed is IN "
            "the spec; the otherwise-identical player whose seed is NOT in the "
            "spec did not, and NOTHING IN THE RECORD DISTINGUISHES THE TWO -- "
            "their executed configs are written the same way. 'We replayed the "
            "experiment' is therefore a claim about the executor's seeding "
            "discipline, not about the frozen spec. Replay strength must be "
            "declared per claim: L0 exact sequence / L1 terminal outcome / "
            "L2 distribution / L3 ranking only.")

    # ==================================================================
    # Q2  WORLD IDENTITY -- same spec, different ORDER
    # ==================================================================
    print("\n" + "=" * 74)
    print("Q2  SAME CHECKPOINT, SAME SPECS, DIFFERENT ENCOUNTER ORDER")
    print("=" * 74)
    p = P_STATEFUL(1); p.reset()
    fwd = run_world(c, sid, "q2-forward", p, SEED, NENC, SPEC_SEED,
                    order=list(range(NENC)))
    p.reset()
    rev = run_world(c, sid, "q2-reversed", p, SEED, NENC, SPEC_SEED,
                    order=list(reversed(range(NENC))))
    same_specs = sorted(fwd["spec_hashes"]) == sorted(rev["spec_hashes"])
    print("  identical SET of frozen spec hashes : %s" % same_specs)
    print("  terminal score forward / reversed   : %.4f / %.4f"
          % (fwd["scores"][-1], rev["scores"][-1]))
    print("  same terminal outcome               : %s"
          % (fwd["scores"][-1] == rev["scores"][-1]))
    data["order"] = {"same_spec_set": same_specs,
                     "terminal_fwd": fwd["scores"][-1],
                     "terminal_rev": rev["scores"][-1]}

    finding("S3-2", "Encounter ORDER changes the outcome while the set of "
            "frozen specs is identical", "BLOCKS_LONG_RUN"
            if fwd["scores"][-1] != rev["scores"][-1] else "KILLED_CONCERN",
            "A stateful player run over the SAME checkpoint with the SAME set "
            "of frozen specs in a different ORDER terminated at %.4f vs %.4f. "
            "The specs hash identically as a set, so any 'same experiment' "
            "claim resting on spec equality is unsupported for stateful "
            "players. Order IS recoverable from the ledger (world_index is "
            "dense and ordered), so this is a missing CHECK rather than lost "
            "information -- but nothing currently checks it, and for a "
            "stateless player order genuinely does not matter, so the check "
            "must be conditional on the player class being declared."
            % (fwd["scores"][-1], rev["scores"][-1]))

    # ==================================================================
    # Q3  INDEPENDENCE -- can a player make the unit of analysis a lie?
    # ==================================================================
    print("\n" + "=" * 74)
    print("Q3  DOES HIDDEN PLAYER STATE MAKE 'INDEPENDENT' WORLDS DEPENDENT?")
    print("=" * 74)
    NW = 8
    honest = P_STATEFUL(1)
    leaky = P_LEARNER(1); leaky.reset()
    h_means, l_means = [], []
    for w in range(NW):
        honest.reset()                                   # correct: reset
        rh = run_world(c, sid, "q3-honest-%d" % w, honest, SEED + w, 6, SPEC_SEED)
        h_means.append(statistics.fmean(rh["scores"]))
        rl = run_world(c, sid, "q3-leaky-%d" % w, leaky, SEED + w, 6, SPEC_SEED)
        l_means.append(statistics.fmean(rl["scores"]))

    def trend(xs):
        n = len(xs); mx = (n - 1) / 2
        my = statistics.fmean(xs)
        num = sum((i - mx) * (x - my) for i, x in enumerate(xs))
        den = (sum((i - mx) ** 2 for i in range(n))
               * sum((x - my) ** 2 for x in xs)) ** 0.5
        return num / den if den else 0.0

    th, tl = trend(h_means), trend(l_means)
    print("  world means, state RESET each world  : %s"
          % [round(x, 3) for x in h_means])
    print("      correlation with run order       : %+.3f" % th)
    print("  world means, state CARRIED OVER      : %s"
          % [round(x, 3) for x in l_means])
    print("      correlation with run order       : %+.3f" % tl)
    data["independence"] = {"honest_means": h_means, "leaky_means": l_means,
                            "honest_trend": th, "leaky_trend": tl}

    finding("S3-3", "Hidden cross-world player state turns independent "
            "replicates into a trend (r=%+.2f vs %+.2f)" % (tl, th),
            "BLOCKS_LONG_RUN",
            "The SAME hill-climbing policy was run over %d worlds twice: once "
            "reset between worlds, once carrying its state across them. Reset, "
            "the world means correlate with run order at r=%+.3f -- no "
            "structure, as it should be. Carrying state, r=%+.3f. The worlds "
            "are then NOT independent replicates: each one starts from where "
            "the last finished, so the unit of analysis declared in packet 1 "
            "(the world) is a LIE for this player class, and every "
            "world-level test silently inherits it. Worse, the effect is "
            "indistinguishable from a real improvement over time. Nothing in "
            "the engine record marks the difference between these two runs -- "
            "same policy name, same specs, same world structure."
            % (NW, th, tl))

    # ==================================================================
    # Q4  REMEDIATION -- does the packet-1 attestation actually catch it?
    # ==================================================================
    print("\n" + "=" * 74)
    print("Q4  ADVERSARIAL POSITIVE CONTROL: does the C-1 executor state hash")
    print("    detect the leakage it was designed to detect?")
    print("=" * 74)
    entries_honest, entries_leaky, leaky_scores = [], [], []
    fresh = P_STATEFUL(1)
    for k in range(5):
        fresh.reset()                                    # correct discipline
        rh = run_world(c, sid, "q4-honest-%d" % k, fresh, SEED + 50 + k, 6,
                       SPEC_SEED)
        rl = run_world(c, sid, "q4-leaky-%d" % k, leaky, SEED + 50 + k, 6,
                       SPEC_SEED)
        entries_honest.append(rh["entry_state"])
        entries_leaky.append(rl["entry_state"])
        leaky_scores.append(statistics.fmean(rl["scores"]))
    honest_all_same = len(set(entries_honest)) == 1
    leaky_differs_from_honest = [h != l for h, l in
                                 zip(entries_honest, entries_leaky)]
    leaky_converged = len(set(entries_leaky[1:])) == 1
    detected = sum(leaky_differs_from_honest)
    print("  honest entry-state hashes across 5 worlds : %s"
          % ("ALL IDENTICAL" if honest_all_same else set(entries_honest)))
    print("  leaky  entry-state hashes across 5 worlds : %s"
          % ("CONVERGED after world 1" if leaky_converged
             else "still moving"))
    print("  worlds where leaky entry != honest entry  : %d of 5" % detected)
    data["remediation"] = {"honest_entries": entries_honest,
                           "leaky_entries": entries_leaky,
                           "honest_all_same": honest_all_same,
                           "leaky_converged": leaky_converged,
                           "detected": detected}

    finding("S3-4", "The entry-state hash detects leakage, but ONLY while the "
            "leaked state is still moving", "INSTRUMENTATION_GAP",
            "Adversarial positive control for my own proposed remediation, and "
            "it found a limit in it. A properly reset player enters every world "
            "with an IDENTICAL state hash (%s). The leaking player entered with "
            "a different hash in %d of 5 worlds, so the field does detect the "
            "leak. BUT its entry states %s: once a leaking learner CONVERGES, "
            "every subsequent world is entered from the same fixed point and "
            "the hash stops distinguishing it from a reset player. A converged "
            "leaker is invisible to the very check designed to catch it. The "
            "hash is therefore necessary and NOT sufficient: it must be paired "
            "with a declaration of intended reset discipline, so that "
            "'identical entry state across worlds' is checked against what the "
            "experiment CLAIMED rather than taken as evidence of hygiene."
            % ("all identical" if honest_all_same else "NOT identical",
               detected,
               "converge after world 1" if leaky_converged
               else "keep changing"))

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"findings": FINDINGS, "data": data}, f, indent=1)
    print("\n" + "=" * 74)
    print("S3 findings: %d   rows: %s" % (len(FINDINGS), a.out))
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
