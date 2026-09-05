"""S2 -- ABLATION HONESTY. Harmonia science loop 2, 2026-09-05.

T6 established that the engine records a declared intervention verbatim and
never interprets it, so a world can declare A while its executor applies
something else. That was one case. An ablation claim needs the whole family.

Six executions, all declaring or applying some part of {A, B, C}, written to a
real engine. For each, the question is not "was it refused" -- none of them
will be -- but:

    FROM THE FOSSIL RECORD ALONE, can this be distinguished from an honest
    ablation? And if so, by WHICH field?

The answer separates two very different situations that look identical in a
results table:

    DETECTABLE    the record contains two independent statements that
                  disagree, so an auditor can catch it after the fact
    INVISIBLE     the record contains only what the client chose to write, so
                  no amount of later analysis can recover the truth

Only the second class blocks scientific claims outright. The first class is a
missing CHECK, which is cheap. The second is a missing MEASUREMENT, which is
not.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

CASES = []


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8896/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    c.token = c.call("POST", "/clients", {"name": "s2"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "s2"})[1]
    c.key = s["session_key"]

    parent = c.call("POST", "/worlds", {"session_id": s["session_id"],
                                        "name": "s2-parent", "seed_root": 7,
                                        "sharing_policy": "ISOLATED"})[1]
    pwid = parent["world_id"]
    c.call("POST", "/worlds/%s/start" % pwid, {})
    ck = c.call("POST", "/worlds/%s/checkpoint" % pwid, {})[1]["checkpoint_id"]

    # (label, declared interventions, the spec the executor actually ran,
    #  what REALLY happened -- ground truth, known only to this script)
    PLAN = [
        ("HONEST",
         {"component": "A"}, {"action": "encounter", "ticks": 8, "applied": "A"},
         "declared A, applied A"),
        ("LIE_declared_A_executed_notA",
         {"component": "A"}, {"action": "encounter", "ticks": 8, "applied": "NOT_A"},
         "declared A, applied NOT-A"),
        ("INVERSE_declared_none_executed_A",
         {}, {"action": "encounter", "ticks": 8, "applied": "A"},
         "declared nothing, applied A"),
        ("PARTIAL_A",
         {"component": "A", "parts": ["a1", "a2"]},
         {"action": "encounter", "ticks": 8, "applied": "A_partial_a1_only"},
         "declared A={a1,a2}, applied a1 only"),
        ("REORDERED_AB",
         {"component": "A+B", "order": ["A", "B"]},
         {"action": "encounter", "ticks": 8, "applied": "B_then_A"},
         "declared A then B, applied B then A"),
        # The one that matters. The executor applies an EXTRA, UNDECLARED
        # co-intervention C and simply does not mention it anywhere.
        ("CO_INTERVENTION_unrecorded",
         {"component": "A"}, {"action": "encounter", "ticks": 8, "applied": "A"},
         "declared A, applied A *and* undeclared C"),
    ]

    kids = c.call("POST", "/worlds/%s/fork" % pwid,
                  {"checkpoint_id": ck,
                   "children": [{"name": lbl, "interventions": iv}
                                for lbl, iv, _, _ in PLAN]})[1]
    kids = kids.get("children", kids)

    record = {}
    for (lbl, declared, spec, truth), kid in zip(PLAN, kids):
        wid = kid["world_id"]
        c.call("POST", "/worlds/%s/start" % wid, {})
        h = c.call("POST", "/worlds/%s/hypotheses" % wid,
                   {"statement": lbl})[1]
        x = c.call("POST", "/worlds/%s/experiments" % wid,
                   {"spec": spec, "hyp_id": h["hyp_id"],
                    "commit": True, "enqueue": True})[1]
        wk = (c.call("POST", "/work/claim", {"worker_id": lbl})[1] or {}).get("work")
        st_c = st_o = None
        if wk:
            st_c = c.call("POST", "/work/%s/complete" % wk["work_id"],
                          {"worker_id": lbl, "claim_id": wk["claim_id"],
                           "result": {"score": 0.5}})[0]
            st_o = c.call("POST", "/worlds/%s/observations" % wid,
                          {"exp_id": x["exp_id"], "work_id": wk["work_id"],
                           "content": {"score": 0.5},
                           "outcome": "SURVIVED"})[0]
        # what the RECORD holds, read back
        evs = c.call("GET", "/worlds/%s/events?limit=200" % wid)[1]["events"]
        wf = next(e for e in evs if e["event_type"] == "WORLD_FORKED")
        pl = wf["payload"]
        pl = json.loads(pl) if isinstance(pl, str) else pl
        got = c.call("GET", "/worlds/%s/experiments/%s" % (wid, x["exp_id"]))[1]
        record[lbl] = {
            "world_id": wid, "truth": truth,
            "recorded_interventions": pl.get("interventions"),
            "recorded_spec": got.get("spec"),
            "spec_hash": got.get("spec_hash"),
            "accepted": {"complete": st_c, "observation": st_o},
        }

    print("=" * 74)
    print("S2  ABLATION HONESTY -- six executions, one checkpoint")
    print("=" * 74)
    for lbl, r in record.items():
        print("\n  %s" % lbl)
        print("      ground truth   : %s" % r["truth"])
        print("      recorded decl. : %s" % json.dumps(r["recorded_interventions"]))
        print("      recorded spec  : %s" % json.dumps(r["recorded_spec"]))
        print("      engine accepted: complete=%s observation=%s"
              % (r["accepted"]["complete"], r["accepted"]["observation"]))

    # ------------------------------------------------------------------
    # DETECTABILITY. An auditor holds only the record. Two statements exist:
    # the DECLARED interventions and the EXECUTED spec. A case is detectable
    # only if those two disagree in a way an auditor can name.
    # ------------------------------------------------------------------
    honest = record["HONEST"]
    print("\n" + "=" * 74)
    print("DETECTABILITY FROM THE RECORD ALONE")
    print("=" * 74)
    verdicts = {}
    for lbl, r in record.items():
        decl = r["recorded_interventions"] or {}
        spec = r["recorded_spec"] or {}
        applied = spec.get("applied", "")
        claimed = decl.get("component")
        if lbl == "HONEST":
            v, why = "N/A (reference)", "the honest case"
        elif not claimed and applied:
            v, why = "DETECTABLE", ("spec says applied=%s while NOTHING was "
                                    "declared" % applied)
        elif claimed and applied and claimed not in applied:
            v, why = "DETECTABLE", ("declared %s vs spec applied=%s -- two "
                                    "recorded statements disagree"
                                    % (claimed, applied))
        elif claimed and applied and applied != claimed and claimed in applied:
            v, why = "DETECTABLE", ("declared %s vs spec applied=%s -- "
                                    "disagreement is visible IF an auditor "
                                    "parses the spec string"
                                    % (claimed, applied))
        else:
            v, why = "INVISIBLE", ("the record is INDISTINGUISHABLE from the "
                                   "honest case: declared %s, spec applied=%s, "
                                   "identical shape. Nothing the executor did "
                                   "beyond this was ever written down."
                                   % (json.dumps(decl), applied))
        verdicts[lbl] = {"verdict": v, "why": why}
        same_as_honest = (r["recorded_interventions"] ==
                          honest["recorded_interventions"]
                          and r["recorded_spec"] == honest["recorded_spec"])
        verdicts[lbl]["byte_identical_to_honest_record"] = same_as_honest
        print("\n  %-34s %s" % (lbl, v))
        print("      %s" % why)
        if same_as_honest and lbl != "HONEST":
            print("      *** its record is BYTE-IDENTICAL to the honest run ***")

    invisible = [k for k, v in verdicts.items()
                 if v["verdict"] == "INVISIBLE" and k != "HONEST"]

    print("\n" + "=" * 74)
    print("FINDING")
    print("=" * 74)
    print("""
  Five of six dishonest or degraded ablations ARE detectable, but only
  because the client wrote TWO statements that can be compared: the declared
  interventions and the executed spec. That is a missing CHECK, and a cheap
  one -- an auditor, or the engine, can compare them.

  The sixth is different in kind. An UNRECORDED CO-INTERVENTION produces a
  record byte-identical to the honest run: %s

  No later analysis can recover it, because the information was never
  written. This is the case that blocks ablation claims, and it is not
  fixable by any engine-side check -- the engine cannot know what it was
  never told.

  MINIMUM ATTESTATION REQUIRED BEFORE AN ABLATION CLAIM IS PERMITTED:
    the EXECUTOR must emit a content hash of the CONFIGURATION IT ACTUALLY
    RAN -- not a label, a hash over the full executed configuration -- and
    the engine must bind that hash to the work result. Then:
      * declared-vs-executed disagreement becomes a hash mismatch, checkable
        mechanically rather than by parsing a free-text spec;
      * an undeclared co-intervention CHANGES the executed configuration and
        therefore changes the hash, which makes the invisible case visible;
      * two runs claimed as replicates must carry the same executed hash, so
        'same run' becomes checkable instead of asserted.
    Without it, 'we ablated A' is a claim about the executor's honesty, not
    a claim the record supports.
""" % (invisible or "none in this sample"))

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"record": record, "verdicts": verdicts,
                   "invisible_cases": invisible}, f, indent=1)
    print("rows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
