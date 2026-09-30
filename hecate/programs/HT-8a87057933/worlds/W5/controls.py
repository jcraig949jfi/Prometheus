"""HT-8a87057933 / W5 controls (Pass 3 v2). NO TREATMENT CODE.

World: factored switching plant. K channels, each with an unknown offset
theta_k in Z_V. Each step a task requests channel k_t with target r_t; the
controller applies u = (r_t - theta_hat_k) mod V; plant output
y = (u + theta_k) mod V; a tracking error is y != r_t. The sensor reports
y_obs = y with prob 1-EPS, otherwise a uniformly random other value. Every
step appends one observation clause "theta_k == (y_obs - u) mod V" to a FIFO
window of capacity W. The clause set is SAT iff, for every channel, all its
window clauses agree. On UNSAT an arm-specific REPAIR deletes clauses until
SAT. Every SWITCH_EVERY steps one channel (uniform) takes a new value.

Arms here (controls only; the TREATMENT, core-guided MUS repair, is NOT here):
  POSITIVE_CONTROL : oracle repair -- on UNSAT delete exactly the clauses
                     inconsistent with the true current theta (targeted
                     forgetting present by construction; same trigger times).
  CONTROL_REF      : drop-oldest until SAT (the spec's CONTROL, a reference).
  NULL_TWIN        : random-drop, one uniformly chosen clause at a time,
                     until SAT (same trigger, same stop rule; localisation
                     destroyed).
  CHEAT            : the NULL_TWIN run with success injected into the
                     observables (errors := 0, valid_deleted := 0).
Rows -> control_rows.jsonl, one per (arm, seed), flushed per row.
"""
import json, os, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
K, V, W = 8, 8, 32
EPS = 0.03
STEPS = 2400
SWITCH_EVERY = 80
SEEDS = list(range(10))


def run(arm, seed):
    rng_w = random.Random(seed * 1000 + 1)      # world: theta, switches, tasks
    rng_s = random.Random(seed * 1000 + 2)      # sensor noise
    rng_a = random.Random(seed * 1000 + 3)      # arm-private (random drop)
    theta = [rng_w.randrange(V) for _ in range(K)]
    window = []                                  # list of (k, value, t)
    errors = 0
    errors_post_switch_first = 0
    unsat = 0
    deleted = 0
    valid_deleted = 0
    switches = 0
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

        def sat(win):
            seen = {}
            for (kk, v, _) in win:
                if seen.setdefault(kk, v) != v:
                    return False
            return True

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
                    else:  # NULL_TWIN (and CHEAT's underlying run)
                        c = window.pop(rng_a.randrange(len(window)))
                    deleted += 1
                    if c[1] == theta[c[0]]:
                        valid_deleted += 1
    row = dict(arm=arm, seed=seed, steps=STEPS, switches=switches,
               errors=errors, unsat_events=unsat, deleted=deleted,
               valid_deleted=valid_deleted,
               valid_deleted_per_unsat=(valid_deleted / unsat) if unsat else 0.0)
    if arm == "CHEAT":
        row["errors"] = 0
        row["valid_deleted"] = 0
        row["valid_deleted_per_unsat"] = 0.0
        row["cheat_injected"] = True
    return row


# ---------------- clause evaluation (arm X placed in the treatment slot) ---
THRESH = {"S1": 0.50, "S2": 0.80, "S3": 0.50}


def clause_values(X, ref):
    ex = sum(r["errors"] for r in X); er = sum(r["errors"] for r in ref)
    s1 = ex / er
    bys = {r["seed"]: r for r in ref}
    s2 = sum(1 for r in X if r["errors"] <= 0.5 * bys[r["seed"]]["errors"]) / len(X)
    vx = sum(r["valid_deleted"] for r in X) / max(1, sum(r["unsat_events"] for r in X))
    vr = sum(r["valid_deleted"] for r in ref) / max(1, sum(r["unsat_events"] for r in ref))
    s3 = vx / vr
    return {"S1": s1, "S2": s2, "S3": s3}


def passes(vals):
    return {"S1": vals["S1"] <= THRESH["S1"], "S2": vals["S2"] >= THRESH["S2"],
            "S3": vals["S3"] <= THRESH["S3"]}


if __name__ == "__main__":
    t0 = time.process_time()
    rows = {}
    with open(os.path.join(HERE, "control_rows.jsonl"), "w") as f:
        for arm in ["CONTROL_REF", "POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"]:
            for s in SEEDS:
                row = run(arm, s)
                rows.setdefault(arm, []).append(row)
                f.write(json.dumps(row) + "\n"); f.flush()
    cpu = time.process_time() - t0
    ref = rows["CONTROL_REF"]
    out = {}
    for arm in ["POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"]:
        v = clause_values(rows[arm], ref)
        out[arm] = {"values": v, "pass": passes(v)}
    summ = {a: {"errors_total": sum(r["errors"] for r in rows[a]),
                "unsat_total": sum(r["unsat_events"] for r in rows[a]),
                "deleted_total": sum(r["deleted"] for r in rows[a]),
                "valid_deleted_total": sum(r["valid_deleted"] for r in rows[a])}
            for a in rows}
    # Plausibility floor: after each switch the switched channel's old value is
    # stale, so its first post-switch request errs with prob >= 7/8 under ANY
    # policy that has not been told about the switch. A run reporting fewer
    # than 0.5 errors per switch is physically implausible -> flagged.
    def floor_flag(rs):
        return any(r["errors"] < 0.5 * r["switches"] for r in rs)
    cheat_pass_all = all(out["CHEAT"]["pass"].values())
    cheat_flagged = floor_flag(rows["CHEAT"])
    pc_flagged = floor_flag(rows["POSITIVE_CONTROL"])
    twin_flagged = floor_flag(rows["NULL_TWIN"])
    er = sum(r["errors"] for r in ref)
    vr = sum(r["valid_deleted"] for r in ref) / sum(r["unsat_events"] for r in ref)
    must = {"S1": "total errors over the 10 seeds <= %d (= 0.50 x CONTROL_REF %d)" % (int(0.5 * er), er),
            "S2": ">= 8 of 10 seeds with errors <= 0.50 x same-seed CONTROL_REF errors (per-seed bars: %s)"
                  % [int(0.5 * r["errors"]) for r in ref],
            "S3": "valid clauses deleted per UNSAT event <= %.3f (= 0.50 x CONTROL_REF %.3f)" % (0.5 * vr, vr)}
    clauses = []
    for cid in ["S1", "S2", "S3"]:
        pv = out["POSITIVE_CONTROL"]["values"][cid]; tv = out["NULL_TWIN"]["values"][cid]
        att = out["POSITIVE_CONTROL"]["pass"][cid]; disc = not out["NULL_TWIN"]["pass"][cid]
        clauses.append({"id": cid, "positive_value": pv, "twin_value": tv,
                        "attainable": att, "discriminating": disc,
                        "treatment_must_reach": must[cid]})
    cheat_detected = cheat_pass_all and cheat_flagged
    frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_detected         and not pc_flagged and not twin_flagged
    revisions = json.load(open(os.path.join(HERE, "revisions.json")))
    att = {"clauses": clauses, "cheat_detected": cheat_detected,
           "cheat_detail": {"cheat_meets_all_success_clauses": cheat_pass_all,
                            "cheat_flagged_by_error_floor": cheat_flagged,
                            "positive_control_flagged_by_floor": pc_flagged,
                            "null_twin_flagged_by_floor": twin_flagged},
           "frozen": frozen, "revisions": revisions,
           "control_cpu_seconds": cpu, "seeds_per_arm": len(SEEDS),
           "arm_totals": summ}
    with open(os.path.join(HERE, "ATTAINABILITY.json"), "w") as f:
        json.dump(att, f, indent=1)
    print(json.dumps(att, indent=1))
