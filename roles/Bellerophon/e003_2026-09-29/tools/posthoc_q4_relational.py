"""POST-HOC (labelled; written after the E-003 result and Archaeon's synthesis #980): relational Q4 diagnostic.

DEF-BEL-004: the frozen q4.py host-assisted arm applies the isolated test's "by its own stores" condition (every window
locus's last store performed by the child's own material). So it cannot see a child that is copied only because a
real host's code performs the copy -- the case Amendment C4.5 exists to separate. This diagnostic re-runs the SAME
host-assisted trials (same deterministic draws as q4.py: occupants from the run's self-performed children, 8 x 40,
random.Random(sha256(tape + "|host"))) and counts a trial as a success when the final window equals the child's
pre-execution tape, WHATEVER performed the stores. It also records the share of those successes that were performed
by the occupant.
It changes no frozen output and feeds no gate or verdict.
    python posthoc_q4_relational.py <births_export.jsonl.gz> <out.jsonl.gz> --workers 10
"""
import argparse, collections, gzip, hashlib, json, multiprocessing as mp, random, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import q4 as Q  # noqa: E402  (reuses its constants, initialiser and draw scheme)


def _one(tape_hex):
    vm = Q._G["vm"]; BT = Q._G["BT"]; L = Q.L
    tape = bytes.fromhex(tape_hex)
    rng = random.Random(int(hashlib.sha256((tape_hex + "|host").encode()).hexdigest()[:16], 16))
    H = Q._G["hosts"]
    occs = [bytes.fromhex(H[rng.randrange(len(H))]) for _ in range(Q.N_OCC)] if H else []
    k = n = by_occ = 0
    for occ in occs:
        for _ in range(Q.N_IN):
            x = rng.randrange(256); n += 1
            mem = bytearray(256); mem[:L] = tape; mem[L:2 * L] = occ; mem[vm.IN_BASE] = x
            after, recs, _ = BT.trace(vm, mem, L, Q.BUDGET, [x], allow_copyall=Q._G["allow"], check=False)
            if after[L:2 * L] == tape and all(recs[i]["written"] for i in range(L)):
                k += 1
                by_occ += any("P" in {b[1] for b in recs[i]["performer"]} for i in range(L))
    return {"tape": tape_hex, "k": k, "n": n, "occupant_performed_successes": by_occ, "capable_relational": n > 0 and k >= 0.5 * n}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("export"); ap.add_argument("out"); ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    tapes = collections.OrderedDict(); hosts = []; allow = None
    for line in gzip.open(a.export, "rt", encoding="utf-8"):
        r = json.loads(line); allow = r["pre_state"]["allow_copyall"]; tapes.setdefault(r["child_tape"], 0)
        W = [x for x in r["loci"] if x["written"]]
        perf = collections.Counter(p[0] for x in W for p in x["performer"])
        if W and perf and perf.most_common(1)[0][0] == "W":
            hosts.append(r["child_tape"])
    hosts = sorted(set(hosts))
    with mp.Pool(a.workers, initializer=Q._init, initargs=(hosts, allow)) as pool, gzip.open(a.out, "wt", encoding="utf-8", newline="\n") as fh:
        for res in pool.imap(_one, list(tapes), chunksize=16):
            fh.write(json.dumps(res, sort_keys=True) + "\n")
    print(json.dumps({"tapes": len(tapes), "out": a.out}))


if __name__ == "__main__":
    mp.freeze_support(); main()
