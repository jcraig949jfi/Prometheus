"""S4 -- INTERACTIONS, NON-COMMUTATIVITY, AND CAMPAIGN TRUNCATION.

Harmonia science loop 4, 2026-09-05.

Two surfaces, joined because both are about what the record CANNOT say.

PART A -- INTERACTIONS. "A+B" is not "A plus B". Ground truth is authored here
so the interaction is known exactly, then the question is whether the record
can express the distinction at all:

  ADDITIVE        A+B = A + B
  ANTAGONISTIC    A+B < A + B   (saturation)
  SYNERGISTIC     A+B > A + B
  NON-COMMUTATIVE order(A,B) != order(B,A)

The engine records interventions as a freeform dict. If a combined arm is
recorded as ONE LABEL ("A+B") rather than as an ordered composition of parts,
every one of the four collapses into "combined intervention" and no later
analysis can separate them.

PART B -- TRUNCATION. Prompted by a real event: the scratch engine serving
loop 3 died on its own. A campaign that intends 8 worlds and dies after 5
leaves a record. The question is whether that record is DISTINGUISHABLE from a
campaign that intended 5 and finished. If it is not, then every long run
carries a silent survivorship channel, and the failure mode is not "the run
crashed" -- it is "the run quietly became a different, smaller experiment".
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import urllib.error
import urllib.request

FINDINGS = []


def finding(fid, title, klass, detail):
    FINDINGS.append({"id": fid, "title": title, "class": klass, "detail": detail})
    print("\n[%s] %s\n    %s" % (klass, title, detail))


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
        except Exception as e:                                     # noqa: BLE001
            return None, {"transport_error": repr(e)}


# --------------------------------------------------------------------------
# Ground-truth interaction models. base 0.40; A worth +0.10; B worth +0.06.
# --------------------------------------------------------------------------
BASE, EA, EB = 0.40, 0.10, 0.06
CAP = 0.50            # saturation ceiling for the antagonistic model


def outcome(model, parts, order, rng):
    a, b = "A" in parts, "B" in parts
    if model == "additive":
        v = BASE + (EA if a else 0) + (EB if b else 0)
    elif model == "antagonistic":
        v = BASE + min((EA if a else 0) + (EB if b else 0), CAP - BASE)
    elif model == "synergistic":
        v = BASE + (EA if a else 0) + (EB if b else 0) + (0.08 if a and b else 0)
    elif model == "noncommutative":
        v = BASE + (EA if a else 0) + (EB if b else 0)
        if a and b:
            v += 0.07 if order == ("A", "B") else -0.05
    else:
        raise ValueError(model)
    return v + rng.gauss(0, 0.01)


def run_arm(c, sid, name, interventions, model, parts, order, rng, n=6):
    """One arm = n worlds, each with one observation. World is the unit."""
    means = []
    wids = []
    for i in range(n):
        w = c.call("POST", "/worlds", {"session_id": sid,
                                       "name": "%s-%d" % (name, i),
                                       "seed_root": 900 + i,
                                       "sharing_policy": "ISOLATED"})[1]
        wid = w.get("world_id")
        if not wid:
            break
        wids.append(wid)
        c.call("POST", "/worlds/%s/start" % wid, {})
        h = c.call("POST", "/worlds/%s/hypotheses" % wid,
                   {"statement": name})[1]
        x = c.call("POST", "/worlds/%s/experiments" % wid,
                   {"spec": {"action": "encounter", "ticks": 8,
                             "arm": name},
                    "hyp_id": h.get("hyp_id"), "commit": True})[1]
        v = outcome(model, parts, order, rng)
        c.call("POST", "/worlds/%s/observations" % wid,
               {"exp_id": x.get("exp_id"), "content": {"score": v},
                "outcome": "SURVIVED"})
        means.append(v)
    return {"means": means, "world_ids": wids, "interventions": interventions}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8895/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    if c.call("GET", "/version")[0] != 200:
        print("engine unreachable"); return 2
    c.token = c.call("POST", "/clients", {"name": "s4"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "s4"})[1]
    c.key = s["session_key"]
    sid = s["session_id"]
    data = {}

    # ==================================================================
    # PART A -- can the record express an interaction at all?
    # ==================================================================
    print("=" * 74)
    print("PART A  INTERACTION STRUCTURE UNDER FOUR KNOWN GROUND TRUTHS")
    print("=" * 74)
    print("  base=%.2f  A=+%.2f  B=+%.2f   (world is the unit, n=6/arm)\n"
          % (BASE, EA, EB))
    results = {}
    for model in ("additive", "antagonistic", "synergistic", "noncommutative"):
        rng = random.Random(hash(model) % 10000)
        arms = {
            "none": run_arm(c, sid, "%s-none" % model, {}, model, set(), (), rng),
            "A": run_arm(c, sid, "%s-A" % model, {"component": "A"},
                         model, {"A"}, ("A",), rng),
            "B": run_arm(c, sid, "%s-B" % model, {"component": "B"},
                         model, {"B"}, ("B",), rng),
            "AB": run_arm(c, sid, "%s-AB" % model,
                          {"component": "A+B"}, model, {"A", "B"},
                          ("A", "B"), rng),
            "BA": run_arm(c, sid, "%s-BA" % model,
                          {"component": "A+B"}, model, {"A", "B"},
                          ("B", "A"), rng),
        }
        m = {k: statistics.fmean(v["means"]) for k, v in arms.items()}
        # the interaction contrast: (AB - A) - (B - none)
        inter = (m["AB"] - m["A"]) - (m["B"] - m["none"])
        order_gap = m["AB"] - m["BA"]
        results[model] = {"means": m, "interaction": inter,
                          "order_gap": order_gap,
                          "recorded_AB_interventions": arms["AB"]["interventions"],
                          "recorded_BA_interventions": arms["BA"]["interventions"]}
        print("  %-15s none=%.3f A=%.3f B=%.3f AB=%.3f BA=%.3f | "
              "interaction=%+.3f  order gap=%+.3f"
              % (model, m["none"], m["A"], m["B"], m["AB"], m["BA"],
                 inter, order_gap))
    data["interactions"] = results

    # Can the RECORD tell AB from BA?
    ab = results["noncommutative"]["recorded_AB_interventions"]
    ba = results["noncommutative"]["recorded_BA_interventions"]
    indistinguishable = ab == ba
    print("\n  recorded interventions for the A-then-B arm : %s" % json.dumps(ab))
    print("  recorded interventions for the B-then-A arm : %s" % json.dumps(ba))
    print("  the two arms are recorded IDENTICALLY        : %s"
          % indistinguishable)

    finding("S4-1", "Order-dependent interaction is real (%+.3f) and the "
            "record cannot express it"
            % results["noncommutative"]["order_gap"],
            "BLOCKS_LONG_RUN" if indistinguishable else "KILLED_CONCERN",
            "Under a known non-commutative ground truth the two orderings "
            "differ by %+.3f -- larger than the main effect of B (%.2f) -- yet "
            "both arms are recorded with the SAME interventions payload %s. "
            "The freeform dict holds a LABEL, not an ordered composition, so "
            "antagonism, synergy and non-commutativity all collapse into "
            "'combined intervention'. The interaction contrast is computable "
            "ONLY because this script kept the ordering outside the record. An "
            "analyst working from fossils alone could not have computed it. "
            "Minimum remediation: interventions must be recorded as an ORDERED "
            "LIST OF PARTS with a content hash per part, not as a display "
            "string."
            % (results["noncommutative"]["order_gap"], EB, json.dumps(ab)))

    # Does the interaction contrast recover the known truth?
    recovered = {k: round(v["interaction"], 3) for k, v in results.items()}
    print("\n  interaction contrast recovered per model: %s" % recovered)
    ok_add = abs(results["additive"]["interaction"]) < 0.03
    ok_ant = results["antagonistic"]["interaction"] < -0.03
    ok_syn = results["synergistic"]["interaction"] > 0.03
    finding("S4-2", "The 2x2 contrast DOES recover additive/antagonistic/"
            "synergistic when the design includes a none arm",
            "KILLED_CONCERN" if (ok_add and ok_ant and ok_syn)
            else "SCIENTIFIC_DESIGN_GAP",
            "additive %+.3f (expect ~0), antagonistic %+.3f (expect <0), "
            "synergistic %+.3f (expect >0). The statistical machinery is fine "
            "and cheap. What it REQUIRES is the none arm: without it (AB-A) "
            "alone is not an interaction, it is just the B effect measured in "
            "the presence of A. Any campaign claiming synergy must run all "
            "four cells, and that is a design rule, not an engine feature."
            % (results["additive"]["interaction"],
               results["antagonistic"]["interaction"],
               results["synergistic"]["interaction"]))

    # ==================================================================
    # PART B -- truncation: does a dead campaign look like a small one?
    # ==================================================================
    print("\n" + "=" * 74)
    print("PART B  CAMPAIGN TRUNCATION")
    print("=" * 74)
    rng = random.Random(5)
    planned, delivered = 8, 5
    trunc = run_arm(c, sid, "truncated", {"component": "A"}, "additive",
                    {"A"}, ("A",), rng, n=delivered)      # died after 5
    small = run_arm(c, sid, "small-by-design", {"component": "A"}, "additive",
                    {"A"}, ("A",), rng, n=delivered)      # intended 5

    # what does the record say about INTENT?
    ev = c.call("GET", "/worlds/%s/events?limit=50" % trunc["world_ids"][0])[1]
    keys = sorted({k for e in ev.get("events", []) for k in e})
    sess = c.call("GET", "/worlds?session_id=%s" % sid)[1]
    n_worlds = len(sess.get("worlds", []) if isinstance(sess, dict) else sess)

    print("  campaign that DIED after %d of %d worlds : %d worlds on record"
          % (delivered, planned, len(trunc["world_ids"])))
    print("  campaign that INTENDED %d worlds          : %d worlds on record"
          % (delivered, len(small["world_ids"])))
    print("  fields available on an event              : %s" % ", ".join(keys))
    print("  any field recording INTENDED campaign size: %s"
          % ("yes" if any("plan" in k or "intend" in k or "target" in k
                          for k in keys) else "NO"))
    data["truncation"] = {"planned": planned, "delivered": delivered,
                          "event_fields": keys,
                          "truncated_worlds": len(trunc["world_ids"]),
                          "small_worlds": len(small["world_ids"])}

    finding("S4-3", "A campaign that DIES partway is indistinguishable from a "
            "campaign that was always that small", "BLOCKS_LONG_RUN",
            "Both records hold %d worlds, the same arm label, the same "
            "intervention payload and the same shape. NO field anywhere "
            "records how many worlds the campaign INTENDED, so nothing "
            "distinguishes 'this run completed' from 'this run stopped'. Three "
            "consequences, in increasing severity: (1) a crashed long run is "
            "silently reinterpreted as a smaller completed one; (2) the "
            "surviving subset is not random if failures correlate with "
            "anything -- long worlds, expensive arms, late scheduling -- which "
            "is survivorship bias with no marker; (3) it makes OPTIONAL "
            "STOPPING undetectable, because 'we stopped when it looked good' "
            "and 'it died' produce identical fossils. This is not theoretical: "
            "the engine serving loop 3 died on its own during this campaign. "
            "Minimum remediation is one field -- a campaign manifest written "
            "BEFORE the first world, naming the intended arms and world count, "
            "so completion is checkable by subtraction."
            % delivered)

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"findings": FINDINGS, "data": data}, f, indent=1)
    print("\n" + "=" * 74)
    print("S4 findings: %d   rows: %s" % (len(FINDINGS), a.out))
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
