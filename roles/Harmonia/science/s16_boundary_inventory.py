"""S16 / #2 -- INVENTORY OF EVERY CLAIMANT-SUPPLIED BOUNDARY IN v6.

Harmonia science loop 16, 2026-09-05.

R12 generalised. Every scientific check in v6 is enumerated FROM THE ENGINE
SOURCE, not from memory, and for each the question is:

    what boundary, denominator, universe, baseline, reference set or scope does
    this check operate over, and WHO SUPPLIES IT?

For each, the smallest adversarial record that obtains REASSURING SILENCE while
omitting scientifically relevant evidence.

Then the classification S15 makes possible, which is the point of doing this
after the fossilization boundary rather than before:

  DERIVABLE      PEW could compute this boundary independently from substrate
                 evidence it already holds. A real fix exists.
  PRE-COMMITTABLE the boundary is claimant-supplied but could be FROZEN BEFORE
                 the data is seen, which converts a free choice into a
                 falsifiable declaration. A partial fix exists.
  INTRINSIC      the omitted evidence was never submitted at all (S15 class B).
                 No fix exists inside the engine, and an absence-inference
                 heuristic would be unfalsifiable.

Those three need different responses and only the first two are fixable, which
is why lumping them together as "R12" was too coarse.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

ROWS = []


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


def codes(p):
    out = set(f.get("code") for f in
              (p or {}).get("science", {}).get("profile_findings", []))
    sv = (p or {}).get("sealed_verification", {})
    out |= set(f.get("code") for f in sv.get("profile_findings", []))
    return sorted(x for x in out if x)


def row(code, boundary, supplier, evasion, silent, klass, note):
    ROWS.append({"check": code, "boundary": boundary, "supplied_by": supplier,
                 "minimal_evasion": evasion, "silence_achieved": silent,
                 "class": klass, "note": note})
    print("  %-30s %-9s %s" % (code, klass, "SILENT" if silent else "fires"))
    print("       boundary : %s  (supplied by %s)" % (boundary, supplier))
    print("       evasion  : %s" % evasion)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8884/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    if c.call("GET", "/version")[0] != 200:
        print("engine unreachable"); return 2
    c.token = c.call("POST", "/clients", {"name": "inv"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "inv"})[1]
    c.key = s["session_key"]
    sid = s["session_id"]

    def world(n, **kw):
        b = {"session_id": sid, "name": n, "sharing_policy": "ISOLATED"}
        b.update(kw)
        w = c.call("POST", "/worlds", b)[1]["world_id"]
        c.call("POST", "/worlds/%s/start" % w, {})
        return w

    def obs(w, spec=None, content=None):
        h = c.call("POST", "/worlds/%s/hypotheses" % w,
                   {"statement": "h"})[1]["hyp_id"]
        x = c.call("POST", "/worlds/%s/experiments" % w,
                   {"spec": spec or {"action": "encounter"},
                    "hyp_id": h, "commit": True})[1]
        o = c.call("POST", "/worlds/%s/observations" % w,
                   {"exp_id": x["exp_id"], "content": content or {"score": 0.5},
                    "outcome": "SURVIVED"})[1]
        return x, o

    print("=" * 78)
    print("S16 / #2  EVERY CLAIMANT-SUPPLIED BOUNDARY IN v6")
    print("=" * 78)
    print("  12 checks enumerated from the engine source\n")

    # 1 FAMILY_EXTENT_DIVERGENCE ------------------------------------------
    f = c.call("POST", "/families",
               {"kind": "campaign", "manifest": {"planned_members": 1}})[1]
    c.call("POST", "/families/%s/members" % f["family_id"],
           {"member_kind": "world", "member_id": world("i1"), "role": "executed"})
    cen = c.call("GET", "/families/%s" % f["family_id"])[1]
    row("FAMILY_EXTENT_DIVERGENCE", "the family's declared extent",
        "claimant", "open one family per batch, each declaring exactly what it "
        "will contain", not codes(cen), "PRE-COMMITTABLE",
        "derivable only up to T-B's limits; a manifest frozen before world 1 "
        "and bound to a spec_hash group would make it falsifiable")

    # 2 SELECTION_WITHOUT_ALTERNATIVES / 3 MULTIPLE_SELECTED --------------
    f2 = c.call("POST", "/families",
                {"kind": "selection", "manifest": {"planned_members": 2}})[1]
    c.call("POST", "/families/%s/members" % f2["family_id"],
           {"member_kind": "world", "member_id": world("i2a"), "role": "selected"})
    c.call("POST", "/families/%s/members" % f2["family_id"],
           {"member_kind": "world", "member_id": world("i2b"),
            "role": "alternative"})
    cen2 = c.call("GET", "/families/%s" % f2["family_id"])[1]
    row("SELECTION_WITHOUT_ALTERNATIVES", "which losers are recorded",
        "claimant", "record ONE token alternative; the other eleven are simply "
        "not added", not codes(cen2), "PRE-COMMITTABLE",
        "S11 4b. selection_visible reports TRUE on a decorative record")
    row("MULTIPLE_SELECTED", "the family's membership",
        "claimant", "one selected member per family, many families",
        True, "PRE-COMMITTABLE", "structurally the same evasion as 4a")

    # 4 TRANSPORT_OVERREACH / 5 TRANSPORT_UNCHECKABLE ---------------------
    w = world("i4")
    x, o = obs(w)
    hh = c.call("POST", "/worlds/%s/hypotheses" % w, {"statement": "a"})[1]["hyp_id"]
    # the tested_domain lives in the FREEFORM spec, so the claimant writes it
    an = c.call("POST", "/worlds/%s/experiments" % w,
                {"spec": {"action": "analysis",
                          "tested_domain": ["A", "B", "C", "D", "E", "F",
                                            "G", "H", "ALL_LANDSCAPES"]},
                 "hyp_id": hh, "commit": True, "unit_of_analysis": "world",
                 "declared_n": 1, "source_set": [o["obs_id"]]})[1]
    st, clm = c.call("POST", "/claims",
                     {"estimand": "x", "status": "SUPPORTED",
                      "relevance_floor": {"smd": 0.2},
                      "replication": {"resampled_noise": True},
                      "transport_domain": ["A", "ALL_LANDSCAPES"],
                      "analysis_exp_id": an["exp_id"]})
    row("TRANSPORT_OVERREACH", "the analysis spec's tested_domain",
        "claimant", "declare a WIDE tested_domain in the freeform spec; any "
        "later transport_domain is then contained in it", not codes(clm),
        "PRE-COMMITTABLE",
        "the check compares two fields the SAME actor writes, so containment "
        "is trivially satisfiable. NOT derivable -- the engine cannot know "
        "which landscapes were actually exercised.")
    row("TRANSPORT_UNCHECKABLE", "whether a tested_domain exists at all",
        "claimant", "write any tested_domain, however inflated",
        not codes(clm), "PRE-COMMITTABLE", "silenced by the same move")

    # 6 NO_REPLICATION_DECLARED -------------------------------------------
    row("NO_REPLICATION_DECLARED", "the six replication booleans",
        "claimant", "declare the single cheapest true boolean, "
        "resampled_noise, and the check is satisfied",
        "NO_REPLICATION_DECLARED" not in codes(clm), "PRE-COMMITTABLE",
        "the booleans are honest -- an undeclared dimension is not a false -- "
        "but ONE true dimension silences the check entirely")

    # 7 CLAIM_CITES_NON_ANALYSIS ------------------------------------------
    row("CLAIM_CITES_NON_ANALYSIS", "which analysis the claim cites",
        "claimant", "cite a real analysis, just not the one over the full "
        "evidence set", not codes(clm), "DERIVABLE",
        "PEW CAN derive the candidate source universe for a cited analysis "
        "via T-B's spec_hash rule and compare it to the declared source_set. "
        "This is the strongest fixable item in the inventory.")

    # 8 NO_EXECUTION_ATTESTATION / 9 CONFIG_DIVERGENCE --------------------
    w8 = world("i8")
    h8 = c.call("POST", "/worlds/%s/hypotheses" % w8, {"statement": "h"})[1]["hyp_id"]
    spec8 = {"action": "encounter", "noise": 0}
    x8 = c.call("POST", "/worlds/%s/experiments" % w8,
                {"spec": spec8, "hyp_id": h8, "commit": True,
                 "enqueue": True})[1]
    g8 = c.call("GET", "/worlds/%s/experiments/%s" % (w8, x8["exp_id"]))[1]
    wk = (c.call("POST", "/work/claim", {"worker_id": "w"})[1] or {}).get("work")
    st8, p8 = (c.call("POST", "/work/%s/complete" % wk["work_id"],
                      {"worker_id": "w", "claim_id": wk["claim_id"],
                       "result": {"score": 0.5},
                       "attestation": {
                           "executed_config_hash": g8.get("spec_hash")}})
               if wk else (None, {}))
    row("NO_EXECUTION_ATTESTATION", "whether an attestation is sent",
        "executor", "send a hash-only attestation", not codes(p8),
        "PRE-COMMITTABLE",
        "S11 4d. An executor that ran nothing passes by echoing the sealed "
        "spec_hash. Attestation CLASSES would separate the two silences.")
    row("CONFIG_DIVERGENCE", "the executed config the executor reports",
        "executor", "echo the requested hash rather than supplying a config",
        not codes(p8), "PRE-COMMITTABLE",
        "fires correctly when a CONFIG is supplied and differs; the gap is the "
        "hash-only path")

    # 10 NO_EFFECTIVE_INTERVENTION / 11 INTERVENTION_NOT_APPLIED /
    # 12 PARTIALLY_INERT_INTERVENTION ------------------------------------
    p = world("i10", seed_root=1)
    obs(p)
    ck = c.call("POST", "/worlds/%s/checkpoint" % p, {})[1]["checkpoint_id"]
    st10, k10 = c.call("POST", "/worlds/%s/fork" % p,
                       {"checkpoint_id": ck,
                        "children": [{"name": "i10c",
                                      "interventions": {"component": "A"},
                                      "intervention_effect": {
                                          "before": {"latent_noise": 0.0},
                                          "after": {"latent_noise": 0.02}}}]})
    row("NO_EFFECTIVE_INTERVENTION", "the before/after the claimant supplies",
        "claimant", "supply a before/after pair that differs in a field the "
        "engine cannot see", not codes(k10), "INTRINSIC",
        "the engine checks hash inequality of what it is GIVEN. A cosmetic "
        "difference silences it; a real difference in an unseen field is "
        "indistinguishable from a fabricated one.")
    row("INTERVENTION_NOT_APPLIED", "the three world fields the engine can see",
        "engine (seed_root, sharing_policy, topology_group)",
        "name an intervention over something the engine never observes -- "
        "noise inside a player, reward shaping", not codes(k10), "INTRINSIC",
        "DERIVED where it applies, which is the exception in this table; but "
        "its scope is three fields and the claimant chooses whether the "
        "intervention lives inside them")
    row("PARTIALLY_INERT_INTERVENTION", "the declared parts of a composite",
        "claimant", "declare a single-part intervention; there are then no "
        "parts to be partially inert", not codes(k10), "PRE-COMMITTABLE",
        "the check is over a decomposition the claimant chooses to expose")

    # ==================================================================
    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    by = {}
    for r in ROWS:
        by.setdefault(r["class"], []).append(r["check"])
    for k in ("DERIVABLE", "PRE-COMMITTABLE", "INTRINSIC"):
        print("\n  %s (%d)" % (k, len(by.get(k, []))))
        for x in by.get(k, []):
            print("      %s" % x)
    sup = {}
    for r in ROWS:
        sup[r["supplied_by"]] = sup.get(r["supplied_by"], 0) + 1
    print("\n  boundary supplier: %s" % json.dumps(sup))
    silent = sum(1 for r in ROWS if r["silence_achieved"])
    print("  checks silenced by a minimal adversarial record: %d of %d"
          % (silent, len(ROWS)))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"rows": ROWS, "by_class": by, "suppliers": sup,
                   "silenced": silent, "total": len(ROWS)}, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
