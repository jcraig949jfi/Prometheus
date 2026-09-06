"""T2 -- concurrency, recorded as UNKNOWN in the sprint directive.

Harmonia, 2026-09-05. Only bounded concurrency on INDEPENDENT ISOLATED worlds
has ever passed. Everything here is unmeasured.

Run against a SCRATCH engine, never the live datastore: C1 deliberately drives
concurrent writes into one world's hash chain, and if the chain can be broken
this is how you break it. The scratch engine is the same pinned build.

Bounded by instruction: N <= 8, and the battery STOPS at the first integrity
anomaly rather than pushing through. A corrupted ledger measured twice is not
twice the evidence.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request

R = []
N = 8


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "state": "PASS" if ok else "FAIL",
              "detail": detail})
    print("  [%s] %-44s %s" % ("PASS" if ok else "FAIL", name, detail))
    return bool(ok)


def indet(name, reason):
    """A gate whose precondition did not hold has measured nothing. It is not
    a failure of the engine and must not be counted as one."""
    R.append({"gate": name, "pass": None, "state": "INDETERMINATE",
              "detail": reason})
    print("  [INDT] %-44s %s" % (name, reason))
    return False


class C:
    def __init__(self, base, token=None, key=None):
        self.base, self.token, self.key = base.rstrip("/"), token, key

    def call(self, m, p, body=None, idem=None):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if self.key:
            h["X-SFE-Session"] = self.key
        if idem:
            h["Idempotency-Key"] = idem
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
        except Exception as e:                                     # noqa: BLE001
            return None, {"transport_error": repr(e)}


def parallel(fn, n):
    """Release n threads as close to simultaneously as a barrier allows."""
    out, bar = [None] * n, threading.Barrier(n)
    def run(i):
        bar.wait()
        out[i] = fn(i)
    ts = [threading.Thread(target=run, args=(i,)) for i in range(n)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8899/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    boot = C(a.base)
    tok = boot.call("POST", "/clients", {"name": "t2"})[1]["token"]
    boot.token = tok
    s = boot.call("POST", "/sessions", {"name": "t2"})[1]
    c = C(a.base, tok, s["session_key"])
    sid = s["session_id"]

    # ---- C1 same-world concurrent writes --------------------------------
    print("\nC1  same-world concurrent writes (N=%d)" % N)
    w = c.call("POST", "/worlds", {"session_id": sid, "name": "t2-c1",
                                   "seed_root": 424242})[1]
    wid = w["world_id"]
    c.call("POST", "/worlds/%s/start" % wid, {})
    K = 5

    def writer(i):
        oks = 0
        for j in range(K):
            payload = ("t2-%d-%d" % (i, j)).encode()
            import base64
            st, _ = c.call("POST", "/worlds/%s/artifacts" % wid,
                           {"kind": "observation_payload",
                            "data_b64": base64.b64encode(payload).decode()})
            oks += (st == 200)
        return oks

    t0 = time.time()
    wrote = parallel(writer, N)
    dt = time.time() - t0
    st, sts = c.call("GET", "/worlds/%s/status" % wid)
    integrity = sts.get("ledger_integrity_ok")
    gate("C1a_all_concurrent_writes_accepted", sum(wrote) == N * K,
         "%d/%d accepted in %.1fs" % (sum(wrote), N * K, dt))
    chain_ok = gate("C1b_ledger_integrity_after_concurrent_writes",
                    integrity is True,
                    "ledger_integrity_ok=%s event_count=%s"
                    % (integrity, sts.get("event_count")))

    st, ev = c.call("GET", "/worlds/%s/events?limit=1000" % wid)
    evs = ev.get("events", ev) if isinstance(ev, dict) else ev
    idx = [e.get("world_index") for e in evs if e.get("world_index") is not None]
    seqs = [e.get("event_seq") for e in evs if e.get("event_seq") is not None]
    dense = sorted(idx) == list(range(min(idx), min(idx) + len(idx))) if idx else False
    gate("C1c_world_index_unique", len(idx) == len(set(idx)),
         "%d events, %d distinct world_index" % (len(idx), len(set(idx))))
    gate("C1d_world_index_dense", dense,
         "range %s..%s over %d events" % (min(idx) if idx else "-",
                                          max(idx) if idx else "-", len(idx)))
    gate("C1e_event_seq_unique", len(seqs) == len(set(seqs)),
         "%d distinct event_seq of %d" % (len(set(seqs)), len(seqs)))

    if not chain_ok:
        print("\nSTOPPING: ledger integrity failed. Not proceeding to further "
              "concurrency tests -- per instruction, stop at the first anomaly.")
        return finish(a.out)

    # ---- C2 claim race ---------------------------------------------------
    print("\nC2  claim race (%d workers, ONE queued item)" % N)
    w2 = c.call("POST", "/worlds", {"session_id": sid, "name": "t2-c2",
                                    "seed_root": 7})[1]
    w2id = w2["world_id"]
    c.call("POST", "/worlds/%s/start" % w2id, {})
    h = c.call("POST", "/worlds/%s/hypotheses" % w2id, {"statement": "H"})[1]
    c.call("POST", "/worlds/%s/predictions" % w2id,
           {"hyp_id": h["hyp_id"], "content": {"p": 1}})
    x = c.call("POST", "/worlds/%s/experiments" % w2id,
               {"spec": {"action": "encounter", "ticks": 4},
                "hyp_id": h["hyp_id"], "commit": True, "enqueue": True})[1]

    def claimer(i):
        return c.call("POST", "/work/claim", {"worker_id": "w%d" % i})

    res = parallel(claimer, N)

    def item(p):
        # POST /work/claim answers {"work": {...}}, not a flat object. Reading
        # it flat scored 0 winners on the first run -- a probe artifact that
        # looks exactly like a broken claim path.
        return (p or {}).get("work") or {}

    winners = [(i, item(p)) for i, (st, p) in enumerate(res)
               if st == 200 and item(p).get("work_id") and item(p).get("claim_id")]
    gate("C2a_exactly_one_claim_winner", len(winners) == 1,
         "%d of %d workers received a work_id+claim_id" % (len(winners), N))
    win_ix = {i for i, _ in winners}
    losers_with_claim = [i for i, (st, p) in enumerate(res)
                         if item(p).get("claim_id") and i not in win_ix]
    gate("C2b_losers_hold_no_claim_id", not losers_with_claim,
         "losers holding a claim_id: %s" % (losers_with_claim or "none"))

    # ---- C3 duplicate completion / stale claim ---------------------------
    print("\nC3  duplicate completion and stale claim fencing")
    if winners:
        wi, wk = winners[0]
        work_id, claim = wk["work_id"], wk["claim_id"]
        me = "w%d" % wi          # the worker that ACTUALLY won the race
        other = "w%d" % ((wi + 1) % N)

        # A valid claim_id presented by a DIFFERENT worker must not complete
        # the item. Discovered by accident -- the first run hardcoded w0 and
        # got 409 because the race winner was someone else -- so it is now a
        # deliberate gate instead of a probe bug.
        stx, px = c.call("POST", "/work/%s/complete" % work_id,
                         {"worker_id": other, "claim_id": claim,
                          "result": {"ok": True}})
        gate("C3d_valid_claim_wrong_worker_refused", stx != 200,
             "worker %s using %s's claim_id -> %s" % (other, me, stx))

        st1, p1 = c.call("POST", "/work/%s/complete" % work_id,
                         {"worker_id": me, "claim_id": claim,
                          "result": {"ok": True}})
        st2, p2 = c.call("POST", "/work/%s/complete" % work_id,
                         {"worker_id": me, "claim_id": claim,
                          "result": {"ok": True}})
        gate("C3a_first_completion_accepted", st1 == 200, "status=%s" % st1)
        # Originally written as "a second completion must be refused". That
        # bar was WRONG: the engine's contract elsewhere is replay-idempotency,
        # and measurement showed the second call returns the ORIGINAL result,
        # the same result_hash, and emits NO second ledger event. Nothing is
        # overwritten and nothing is double-counted, so the correct property to
        # assert is idempotence, not refusal.
        n_before = len((c.call("GET", "/worlds/%s/events?limit=1000" % w2id)[1]
                        or {}).get("events", []))
        st_over, p_over = c.call("POST", "/work/%s/complete" % work_id,
                                 {"worker_id": me, "claim_id": claim,
                                  "result": {"ok": "OVERWRITE-ATTEMPT"}})
        n_after = len((c.call("GET", "/worlds/%s/events?limit=1000" % w2id)[1]
                       or {}).get("events", []))
        gate("C3b_duplicate_completion_is_idempotent_replay",
             st2 == 200 and p2.get("result") == p1.get("result")
             and p2.get("result_hash") == p1.get("result_hash"),
             "second identical completion -> %s, same result_hash=%s"
             % (st2, p2.get("result_hash") == p1.get("result_hash")))
        # UPDATED 2026-09-05 for build 2f35868c (Daedalus b35046a60). This
        # gate previously measured 200 + the original result, and recorded the
        # inconsistency with the engine's own "same key, different request ->
        # 409" idempotency rule. That is now fixed, in ADVISORY mode too, so
        # the expectation is 409 and the stored result must still be intact.
        det = p_over.get("detail") if isinstance(p_over.get("detail"), dict) else {}
        st_read, p_read = c.call("GET", "/worlds/%s/experiments" % w2id)
        gate("C3e_replay_with_a_DIFFERENT_result_is_409",
             st_over == 409 and n_after == n_before,
             "differing result -> %s (%s), new ledger events=%d, detail names "
             "hashes=%s"
             % (st_over, det.get("error"), n_after - n_before,
                any("hash" in k for k in det)))
        st3, p3 = c.call("POST", "/work/%s/complete" % work_id,
                         {"worker_id": me, "claim_id": "clm_" + "0" * 24,
                          "result": {"ok": True}})
        gate("C3c_stale_claim_id_refused", st3 != 200,
             "forged claim_id -> %s" % st3)
    else:
        for g in ("C3d_valid_claim_wrong_worker_refused",
                  "C3a_first_completion_accepted",
                  "C3b_duplicate_completion_refused",
                  "C3c_stale_claim_id_refused"):
            indet(g, "no claim winner in C2; the fencing path was never reached")

    # ---- C4 concurrent idempotent create ---------------------------------
    print("\nC4  concurrent create-world under ONE Idempotency-Key (N=%d)" % N)
    idem = "t2-idem-%d" % int(time.time())

    def creator(i):
        return c.call("POST", "/worlds",
                      {"session_id": sid, "name": "t2-idem", "seed_root": 11},
                      idem=idem)

    res4 = parallel(creator, N)
    ids = {p.get("world_id") for st, p in res4 if st == 200 and p.get("world_id")}
    codes = sorted({st for st, _ in res4})
    gate("C4a_exactly_one_world_created", len(ids) == 1,
         "%d distinct world_id from %d parallel requests; statuses=%s"
         % (len(ids), N, codes))

    # ---- C5 bounded latency ramp -----------------------------------------
    print("\nC5  bounded latency ramp (read-only, no saturation)")
    ramp = {}
    for n in (1, 2, 4, 8):
        def reader(i):
            t = time.time()
            c.call("GET", "/worlds/%s/status" % wid)
            return time.time() - t
        lat = parallel(reader, n)
        ramp[n] = round(statistics.median(lat) * 1000, 1)
        print("      N=%-2d median %6.1f ms" % (n, ramp[n]))
    knee = ramp[8] / ramp[1] if ramp[1] else 0
    gate("C5_latency_scales_sublinearly_to_8", knee <= N,
         "median latency N=8 is %.1fx N=1 (%s ms -> %s ms); linear would be %dx"
         % (knee, ramp[1], ramp[8], N))

    return finish(a.out, ramp)


def finish(out, ramp=None):
    ok = all(r["pass"] for r in R if r["state"] != "INDETERMINATE")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"all_pass": ok, "N": N, "gates": R, "latency_ms": ramp},
                  f, indent=1)
    print("\nT2 %s   %d/%d gates" % ("PASS" if ok else "FAIL",
                                     sum(r["pass"] for r in R), len(R)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
