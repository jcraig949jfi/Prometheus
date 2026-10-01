"""HT-8a87057933 / W5 Pass 4 attacks: R, ORIG (original W5 world) and ALT
(relational world; its controls were run first by alt_controls.py).
Rows -> pass4/rows.jsonl, one per (attack, arm, seed[, source]), flushed per row.
Written after ALT_ATTAINABILITY.json existed (eligible=true).
"""
import json, os, random, sys, time
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
sys.path.insert(0, WORLD)
sys.path.insert(0, os.path.join(WORLD, "probe"))
sys.path.insert(0, HERE)
import controls                 # frozen W5 controls
import world as probe_world     # frozen round-3 treatment (core-guided)
import alt_controls             # ALT world (controls-first)

K, V, W = controls.K, controls.V, controls.W
EPS, STEPS, SWITCH_EVERY = controls.EPS, controls.STEPS, controls.SWITCH_EVERY
SEEDS = list(range(100, 110))
PARAMS_ORIG = dict(world="W5_original", K=K, V=V, W=W, EPS=EPS, STEPS=STEPS,
                   SWITCH_EVERY=SWITCH_EVERY)
CORE = ("errors", "unsat_events", "deleted", "valid_deleted", "switches")


def orig_run(arm, seed):
    """Verbatim copy of probe/world.run's loop + CHANNEL_RESET branch."""
    sat, mus_by_deletion = probe_world.sat, probe_world.mus_by_deletion
    rng_w = random.Random(seed * 1000 + 1)
    rng_s = random.Random(seed * 1000 + 2)
    rng_a = random.Random(seed * 1000 + 3)
    theta = [rng_w.randrange(V) for _ in range(K)]
    window = []
    errors = unsat = deleted = valid_deleted = switches = 0
    for t in range(STEPS):
        if t > 0 and t % SWITCH_EVERY == 0:
            k = rng_w.randrange(K)
            theta[k] = (theta[k] + 1 + rng_w.randrange(V - 1)) % V
            switches += 1
        k = rng_w.randrange(K)
        r = rng_w.randrange(V)
        allowed = set(range(V))
        for (kk, v, _) in window:
            if kk == k:
                allowed &= {v}
        th = min(allowed) if allowed else 0
        u = (r - th) % V
        y = (u + theta[k]) % V
        if y != r:
            errors += 1
        noise = rng_s.random() < EPS
        y_obs = (y + 1 + rng_s.randrange(V - 1)) % V if noise else y
        new = (k, (y_obs - u) % V, t)
        window.append(new)
        if len(window) > W:
            window.pop(0)
        if not sat(window):
            unsat += 1
            if arm == "POSITIVE_CONTROL":
                keep = [c for c in window if c[1] == theta[c[0]]]
                deleted += len(window) - len(keep)
                window = keep
            elif arm == "CHANNEL_RESET":
                gone = [c for c in window if c is not new and c[0] == k]
                window = [c for c in window if c is new or c[0] != k]
                deleted += len(gone)
                valid_deleted += sum(1 for c in gone if c[1] == theta[c[0]])
            else:
                while not sat(window):
                    if arm == "CONTROL_REF":
                        c = window.pop(0)
                    elif arm == "TREATMENT":
                        core = mus_by_deletion(window)
                        c = min(core, key=lambda x: x[2])
                        window = [x for x in window if x is not c]
                    else:
                        c = window.pop(rng_a.randrange(len(window)))
                    deleted += 1
                    if c[1] == theta[c[0]]:
                        valid_deleted += 1
    return dict(arm=arm, seed=seed, steps=STEPS, switches=switches,
                errors=errors, unsat_events=unsat, deleted=deleted,
                valid_deleted=valid_deleted,
                valid_deleted_per_unsat=(valid_deleted / unsat) if unsat else 0.0)


# ---- ALT treatment: core-guided repair on the relational world -------------
_mus_log = []


def alt_mus_by_deletion(window):
    S = list(window)
    for c in list(window):              # oldest-first
        trial = [x for x in S if x is not c]
        if not alt_controls.sat(trial):
            S = trial
    return S


def alt_core_guided(window):
    core = alt_mus_by_deletion(window)
    chans = set()
    for (i, j, _, _) in core:
        chans.update((i, j))
    _mus_log.append((len(core), len(chans)))
    return min(core, key=lambda x: x[3])


if __name__ == "__main__":
    t0 = time.process_time()
    f = open(os.path.join(HERE, "rows.jsonl"), "w")

    def emit(row):
        f.write(json.dumps(row) + "\n"); f.flush()

    # R + ORIG, original world
    for arm in ["CONTROL_REF", "POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"]:
        for s in SEEDS:
            row = controls.run(arm, s)
            row.update(attack="R", source="controls.run", params=PARAMS_ORIG)
            emit(row)
    for s in SEEDS:
        row = probe_world.run("TREATMENT", s)
        row.update(attack="R", source="probe/world.run", params=PARAMS_ORIG)
        emit(row)
    for s in SEEDS:
        row = orig_run("CHANNEL_RESET", s)
        row.update(attack="ORIG", source="pass4/attack.orig_run", params=PARAMS_ORIG)
        emit(row)
    for arm in ["CONTROL_REF", "POSITIVE_CONTROL", "NULL_TWIN", "TREATMENT"]:
        for s in SEEDS:
            row = orig_run(arm, s)
            row.update(attack="FAITHFULNESS", source="pass4/attack.orig_run",
                       params=PARAMS_ORIG)
            emit(row)
    # ALT world: control arms rerun (determinism vs alt_control_rows.jsonl) + TREATMENT
    for arm in alt_controls.ARMS:
        for s in SEEDS:
            row = alt_controls.run(arm, s)
            row.update(attack="ALT", source="alt_controls.run", params=alt_controls.PARAMS)
            emit(row)
    for s in SEEDS:
        _mus_log.clear()
        row = alt_controls.run("TREATMENT", s, repair=alt_core_guided)
        row.update(attack="ALT", source="alt_controls.run+attack.alt_core_guided",
                   params=alt_controls.PARAMS,
                   mus_calls=len(_mus_log),
                   mus_size_min=min((a for a, _ in _mus_log), default=0),
                   mus_size_max=max((a for a, _ in _mus_log), default=0),
                   mus_size_mean=(sum(a for a, _ in _mus_log) / len(_mus_log)) if _mus_log else 0,
                   mus_channels_min=min((b for _, b in _mus_log), default=0),
                   mus_frac_spanning_ge3_channels=(sum(1 for _, b in _mus_log if b >= 3) / len(_mus_log)) if _mus_log else 0)
        emit(row)
    f.close()
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, "run_meta.json"), "w") as g:
        json.dump({"attack_cpu_seconds": cpu, "attempt": 1, "seeds": SEEDS}, g, indent=1)
    print("attack cpu_seconds", cpu)
