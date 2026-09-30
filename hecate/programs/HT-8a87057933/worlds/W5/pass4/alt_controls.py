"""HT-8a87057933 / W5 Pass 4 ALT world -- CONTROLS ONLY. NO TREATMENT CODE.

Relational plant: task on ordered pair (i, j); y = (u + theta_i - theta_j) mod V;
clause "theta_i - theta_j == (y_obs - u) mod V". SAT = consistency of the
difference constraints (weighted union-find over Z_V). See NOTES.md.
Arms: CONTROL_REF, POSITIVE_CONTROL, NULL_TWIN, CHEAT, CHANNEL_RESET.
Writes alt_control_rows.jsonl and ALT_ATTAINABILITY.json.
"""
import json, os, random, sys, time
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
K, V, W = 8, 8, 32
EPS = 0.03
STEPS = 2400
SWITCH_EVERY = 80
SEEDS = list(range(100, 110))
PARAMS = dict(world="ALT_relational", K=K, V=V, W=W, EPS=EPS, STEPS=STEPS,
              SWITCH_EVERY=SWITCH_EVERY)


def _uf(win):
    """Weighted union-find over window clauses (i, j, d, t): theta_i - theta_j = d.
    Returns (ok, find) where find(x) -> (root, theta_x - theta_root)."""
    parent = list(range(K)); pot = [0] * K

    def find(x):
        p = 0
        while parent[x] != x:
            p = (p + pot[x]) % V
            x = parent[x]
        return x, p
    ok = True
    for (i, j, d, _) in win:
        ri, pi = find(i); rj, pj = find(j)
        if ri == rj:
            if (pi - pj) % V != d:
                ok = False
        else:
            parent[ri] = rj
            pot[ri] = (d - pi + pj) % V
    return ok, find


def sat(win):
    return _uf(win)[0]


def estimate(win, i, j):
    _, find = _uf(win)
    ri, pi = find(i); rj, pj = find(j)
    return (pi - pj) % V if ri == rj else None


def run(arm, seed, repair=None):
    """repair: optional callable(window) -> clause to delete (used ONLY by the
    later treatment script; None here)."""
    rng_w = random.Random(seed * 1000 + 1)
    rng_s = random.Random(seed * 1000 + 2)
    rng_a = random.Random(seed * 1000 + 3)
    theta = [rng_w.randrange(V) for _ in range(K)]
    window = []                                   # (i, j, d, t)
    errors = unsat = deleted = valid_deleted = switches = 0
    last_switched = None
    unsat_touch_switched = 0
    for t in range(STEPS):
        if t > 0 and t % SWITCH_EVERY == 0:
            c = rng_w.randrange(K)
            theta[c] = (theta[c] + 1 + rng_w.randrange(V - 1)) % V
            switches += 1
            last_switched = c
        i = rng_w.randrange(K)
        j = (i + 1 + rng_w.randrange(K - 1)) % K
        r = rng_w.randrange(V)
        e = estimate(window, i, j)
        th = e if e is not None else 0
        u = (r - th) % V
        y = (u + theta[i] - theta[j]) % V
        if y != r:
            errors += 1
        noise = rng_s.random() < EPS
        y_obs = (y + 1 + rng_s.randrange(V - 1)) % V if noise else y
        new = (i, j, (y_obs - u) % V, t)
        window.append(new)
        if len(window) > W:
            window.pop(0)

        def valid(c):
            return (theta[c[0]] - theta[c[1]]) % V == c[2]

        if not sat(window):
            unsat += 1
            if last_switched in (i, j):
                unsat_touch_switched += 1
            if arm == "POSITIVE_CONTROL":
                keep = [c for c in window if valid(c)]
                deleted += len(window) - len(keep)
                window = keep
            elif arm == "CHANNEL_RESET":
                gone = [c for c in window if c is not new and
                        (c[0] in (i, j) or c[1] in (i, j))]
                keep = [c for c in window if not any(c is g for g in gone)]
                deleted += len(gone)
                valid_deleted += sum(1 for c in gone if valid(c))
                window = keep
            else:
                while not sat(window):
                    if arm == "CONTROL_REF":
                        c = window.pop(0)
                    elif arm in ("NULL_TWIN", "CHEAT"):
                        c = window.pop(rng_a.randrange(len(window)))
                    elif repair is not None:
                        c = repair(window)
                        window = [x for x in window if x is not c]
                    else:
                        raise ValueError(arm)
                    deleted += 1
                    if valid(c):
                        valid_deleted += 1
    row = dict(arm=arm, seed=seed, steps=STEPS, switches=switches,
               errors=errors, unsat_events=unsat, deleted=deleted,
               valid_deleted=valid_deleted,
               valid_deleted_per_unsat=(valid_deleted / unsat) if unsat else 0.0,
               unsat_touching_last_switched=unsat_touch_switched)
    if arm == "CHEAT":
        row.update(errors=0, valid_deleted=0, valid_deleted_per_unsat=0.0,
                   cheat_injected=True)
    return row


THRESH = {"A1": 0.50, "A2": 0.80}


def alt_values(X, ref, reset):
    ex = sum(r["errors"] for r in X)
    return {"A1": ex / sum(r["errors"] for r in ref),
            "A2": ex / sum(r["errors"] for r in reset)}


def alt_passes(v):
    return {"A1": v["A1"] <= THRESH["A1"], "A2": v["A2"] <= THRESH["A2"]}


def floor_flag(rs):
    return any(r["errors"] < 0.5 * r["switches"] for r in rs)


def attainability(rows):
    ref, reset = rows["CONTROL_REF"], rows["CHANNEL_RESET"]
    out = {a: alt_values(rows[a], ref, reset) for a in
           ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT")}
    ps = {a: alt_passes(v) for a, v in out.items()}
    clauses = [{"id": c, "threshold": THRESH[c],
                "positive_value": out["POSITIVE_CONTROL"][c],
                "twin_value": out["NULL_TWIN"][c],
                "attainable": ps["POSITIVE_CONTROL"][c],
                "discriminating": not ps["NULL_TWIN"][c]} for c in ("A1", "A2")]
    cheat_all = all(ps["CHEAT"].values())
    cheat_flag = floor_flag(rows["CHEAT"])
    pc_flag = floor_flag(rows["POSITIVE_CONTROL"])
    tw_flag = floor_flag(rows["NULL_TWIN"])
    cheat_detected = cheat_all and cheat_flag
    eligible = (all(c["attainable"] and c["discriminating"] for c in clauses)
                and cheat_detected and not pc_flag and not tw_flag)
    totals = {a: {k: sum(r[k] for r in rs) for k in
                  ("errors", "unsat_events", "deleted", "valid_deleted",
                   "unsat_touching_last_switched")} for a, rs in rows.items()}
    return {"clauses": clauses, "cheat_detected": cheat_detected,
            "cheat_detail": {"cheat_meets_all_alt_clauses": cheat_all,
                             "cheat_flagged_by_error_floor": cheat_flag,
                             "positive_control_flagged_by_floor": pc_flag,
                             "null_twin_flagged_by_floor": tw_flag},
            "eligible": eligible, "arm_totals": totals,
            "errors_per_seed": {a: [r["errors"] for r in rs] for a, rs in rows.items()}}


ARMS = ["CONTROL_REF", "CHANNEL_RESET", "POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"]

if __name__ == "__main__":
    t0 = time.process_time()
    rows = {}
    with open(os.path.join(HERE, "alt_control_rows.jsonl"), "w") as f:
        for arm in ARMS:
            for s in SEEDS:
                row = run(arm, s)
                row["params"] = PARAMS
                rows.setdefault(arm, []).append(row)
                f.write(json.dumps(row) + "\n"); f.flush()
    att = attainability(rows)
    att["control_cpu_seconds"] = time.process_time() - t0
    att["seeds"] = SEEDS
    att["params"] = PARAMS
    att["written_before_any_alt_treatment_code"] = True
    with open(os.path.join(HERE, "ALT_ATTAINABILITY.json"), "w") as f:
        json.dump(att, f, indent=1)
    print(json.dumps(att, indent=1))
