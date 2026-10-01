"""HT-8a87057933 / W5 probe: TREATMENT (core-guided MUS repair) + control arms.

Control arms are produced by the frozen controls.run (imported). TREATMENT is
run by `run` below, a line-for-line copy of controls.run's loop with the
core-guided repair branch added; `run` is also executed for the three
non-cheat control arms and checked row-for-row against controls.run.
Rows -> probe/rows.jsonl, one per (source, arm, seed), flushed per row.
"""
import json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
sys.dont_write_bytecode = True
sys.path.insert(0, WORLD)
import controls  # frozen; importing does not execute its __main__ block

K, V, W = controls.K, controls.V, controls.W
EPS, STEPS, SWITCH_EVERY, SEEDS = controls.EPS, controls.STEPS, controls.SWITCH_EVERY, controls.SEEDS


def sat(win):
    seen = {}
    for (kk, v, _) in win:
        if seen.setdefault(kk, v) != v:
            return False
    return True


def mus_by_deletion(window):
    """Deletion-based MUS, scanning window clauses oldest-first. Generic: uses
    only the SAT test. Returns the MUS as a list of clauses (window order)."""
    S = list(window)
    for c in list(window):          # window is in insertion (age) order
        trial = [x for x in S if x is not c]
        if not sat(trial):
            S = trial
    return S


def run(arm, seed):
    rng_w = random.Random(seed * 1000 + 1)
    rng_s = random.Random(seed * 1000 + 2)
    rng_a = random.Random(seed * 1000 + 3)
    theta = [rng_w.randrange(V) for _ in range(K)]
    window = []
    errors = 0
    unsat = 0
    deleted = 0
    valid_deleted = 0
    switches = 0
    mus_sizes = []
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
        window.append((k, (y_obs - u) % V, t))
        if len(window) > W:
            window.pop(0)

        if not sat(window):
            unsat += 1
            if arm == "POSITIVE_CONTROL":
                keep = [c for c in window if c[1] == theta[c[0]]]
                gone = len(window) - len(keep)
                deleted += gone
                window = keep
            else:
                while not sat(window):
                    if arm == "CONTROL_REF":
                        c = window.pop(0)
                    elif arm == "TREATMENT":
                        core = mus_by_deletion(window)
                        mus_sizes.append(len(core))
                        c = min(core, key=lambda x: x[2])
                        window = [x for x in window if x is not c]
                    else:  # NULL_TWIN
                        c = window.pop(rng_a.randrange(len(window)))
                    deleted += 1
                    if c[1] == theta[c[0]]:
                        valid_deleted += 1
    row = dict(arm=arm, seed=seed, steps=STEPS, switches=switches,
               errors=errors, unsat_events=unsat, deleted=deleted,
               valid_deleted=valid_deleted,
               valid_deleted_per_unsat=(valid_deleted / unsat) if unsat else 0.0)
    if arm == "TREATMENT":
        row["mus_calls"] = len(mus_sizes)
        row["mus_size_max"] = max(mus_sizes) if mus_sizes else 0
        row["mus_size_min"] = min(mus_sizes) if mus_sizes else 0
    return row


if __name__ == "__main__":
    t0 = time.process_time()
    params = dict(K=K, V=V, W=W, EPS=EPS, STEPS=STEPS, SWITCH_EVERY=SWITCH_EVERY)
    with open(os.path.join(HERE, "rows.jsonl"), "w") as f:
        for arm in ["CONTROL_REF", "POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"]:
            for s in SEEDS:
                row = controls.run(arm, s)
                row.update(source="controls.run", params=params)
                f.write(json.dumps(row) + "\n"); f.flush()
        for arm in ["CONTROL_REF", "POSITIVE_CONTROL", "NULL_TWIN"]:
            for s in SEEDS:
                row = run(arm, s)
                row.update(source="world.run_faithfulness", params=params)
                f.write(json.dumps(row) + "\n"); f.flush()
        for s in SEEDS:
            row = run("TREATMENT", s)
            row.update(source="world.run", params=params)
            f.write(json.dumps(row) + "\n"); f.flush()
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, "run_meta.json"), "w") as f:
        json.dump({"cpu_seconds": cpu, "attempt": 1, "seeds": SEEDS}, f, indent=1)
    print("cpu_seconds", cpu)
