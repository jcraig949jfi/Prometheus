# V2B FROZEN COPY (C-006 Beta-01, DEV-1, 2026-10-04): byte-identical body of
#   roles/Aphrodite/science/arc3/w7_instrument_hygiene/tribunal_t4_v1a.py  (git blob cf93795d99a3a7d3554f5a2575019bf1df0772ac, sha256 630dc0092a1cce99ecb014d527ca4babd3db0f38b57bb56d672bd35cff80eaf5)
# Frozen as an apparatus instrument of v2b-1. The historical instrument it repairs is untouched.
"""DRAFT -- TRIBUNAL T4 v1a: counterexample queries aligned with the dev domain.

W7 (ARC3, PKG-6 fix (a)). NEW MODULE; engine/tribunal_t4.py is imported and
never modified. NOTHING HERE IS ADOPTED: it becomes an instrument only if the
Aphrodite seat freezes it in a dated AMENDMENT.

Defect addressed (W2 F4/F5.5). The dev distribution and Q2 draw queries from
3..97 (a17.Prov.task), but T4 v1 declares the query domain 1..97 and draws the
counterexample query as r.choice([1, 2, r.randint(3, 97)]), i.e. about 2/3 of
the 40 counterexample items use query 1 or 2. An artifact that is extensionally
equal to the witness on the TRAINING domain (queries 3..97) but differs at
query 1 or 2 (e.g. `acc // last`, `acc % (last - 1)`, `v % (v * last)`,
`1 // last`) fails T4 by construction: the dev data can never distinguish it.

Change (the ONLY behavioural changes relative to T4 v1):
  1. Counterexample battery: the query is the SAME r.randint(3, 97) value that
     v1 already draws (the rng stream, list lengths and list values are
     byte-identical; only items whose v1 query was 1 or 2 change, and they
     change to the query v1 drew but discarded).
  2. Family profile totality probes: queries (3, 41, 97) instead of
     (1, 2, 3, 41, 97). The declared domain becomes query 3..97, the dev domain.
Everything else (ladder, thresholds, junk rules, ext/stress/order batteries,
which already use 3..97) is v1 unchanged.

Consequence to state in any amendment: v1a certifies NOTHING about queries 1
and 2. If query-1/2 behaviour matters scientifically, use fix (b)
(a17_dev197.py: widen the dev/Q2 draw to 1..97) instead.
"""
import random
import re
from collections import Counter
from typing import Dict, List, Optional

import tribunal_t4 as T4
import engine as E

NAME = "TRIBUNAL_T4_ORDER_AWARE_v1a_DRAFT"
QUERY_LO = 3
PROFILE_QUERIES = (3, 41, 97)

run = T4.run
use_provider = T4.use_provider
_PROFILE: Dict[tuple, Dict] = {}
_BAT: Dict[tuple, Dict[str, List[Dict]]] = {}


def family_profile(witness) -> Dict:
    """v1 family_profile with totality probes restricted to queries 3..97.
    Implemented by temporarily narrowing the probe tuple through a local copy of
    the v1 code path (the v1 function hard-codes (1, 2, 3, 41, 97))."""
    key = tuple(witness)
    got = _PROFILE.get(key)
    if got is not None:
        return got
    rng = random.Random("APHRODITE/T4/PROFILE/v1/" + repr(key))   # v1 seed: same draws
    reasons, guard = [], 0

    def total_on(L, nrand):
        nonlocal guard
        probes = [(xs, m) for xs in T4._extremes(L) for m in PROFILE_QUERIES]
        probes += [(T4._rand_list(rng, L), rng.randint(1, 97)) for _ in range(nrand)]
        # NOTE: the random probes keep v1's randint(1, 97) so the rng stream is
        # identical; a query < QUERY_LO is lifted into the domain deterministically.
        for xs, m in probes:
            m = m if m >= QUERY_LO else m + QUERY_LO + 38     # 1 -> 42, 2 -> 43
            out, g = run(witness, xs, m)
            guard += g
            if out is None or g:
                return False
        return True

    base_ok = all(total_on(L, 6) for L in T4.BASE_LENGTHS)
    l_max = None
    if base_ok:
        for L in T4.LADDER:
            if not total_on(L, 16):
                break
            l_max = L
    if not base_ok:
        reasons.append("NONE_OR_GUARD_ON_DEV_LENGTHS")
    elif l_max is None:
        reasons.append("DOMAIN_TOO_SHORT")
    outs, copies, mid_ch, last_ch = [], 0, 0, 0
    for _ in range(60):
        xs = T4._rand_list(rng, rng.randint(5, 9))
        m = rng.randint(3, 97)
        o, g = run(witness, xs, m)
        guard += g
        outs.append(o)
        copies += o is not None and (o in xs or o == m)
        i = len(xs) // 2
        ys = list(xs)
        ys[i] = rng.choice([u for u in range(2, 31) if u != xs[i]])
        mid_ch += run(witness, ys, m)[0] != o
        zs = list(xs)
        zs[-1] = rng.choice([u for u in range(2, 31) if u != xs[-1]])
        last_ch += run(witness, zs, m)[0] != o
    cnt = Counter(outs)
    distinct = len([o for o in cnt if o is not None])
    mode_share = cnt.most_common(1)[0][1] / len(outs)
    mid_s, last_s, copy_s = mid_ch / 60, last_ch / 60, copies / 60
    absorbed, n_abs = 0, 0
    La = min(30, l_max or 30)
    for _ in range(30):
        tr = []
        out, g = run(witness, T4._rand_list(rng, La), rng.randint(3, 97), trace=tr)
        if len(tr) > 6:
            n_abs += 1
            absorbed += len(set(tr[5:])) == 1
    absorb_s = absorbed / n_abs if n_abs else 0.0
    if None in cnt:
        reasons.append("NONE_ON_DEV_DISTRIBUTION")
    if distinct < T4.K_DISTINCT or mode_share > T4.MODE_MAX:
        reasons.append("CONSTANT_OR_NEAR_CONSTANT")
    if mid_s < T4.SENS_MIN:
        reasons.append("MIDDLE_INSENSITIVE")
    if last_s < T4.SENS_MIN:
        reasons.append("LAST_INSENSITIVE")
    if copy_s > T4.COPY_MAX:
        reasons.append("COPIES_INPUT")
    if absorb_s >= T4.ABSORB_MAX:
        reasons.append("FIXED_POINT_DYNAMICS")
    if guard:
        reasons.append("POW_GUARD_HIT")
    prof = {"L_max": l_max, "base_ok": base_ok, "distinct": distinct,
            "mode_share": round(mode_share, 3), "middle_sensitivity": round(mid_s, 3),
            "last_sensitivity": round(last_s, 3), "copy_share": round(copy_s, 3),
            "absorbed_share": round(absorb_s, 3), "pow_guard_hits": guard,
            "reasons": sorted(set(reasons)), "admissible": not reasons}
    _PROFILE[key] = prof
    return prof


def batteries(family: str, witness, l_max: Optional[int], n: int = 150) -> Dict[str, List[Dict]]:
    """v1 batteries; counterexample queries drawn from 3..97 (same rng stream)."""
    key = (family, tuple(witness), l_max, n)
    got = _BAT.get(key)
    if got is not None:
        return got
    base = T4.batteries(family, witness, l_max, n)          # ext / stress / order: identical
    L = l_max or T4.EXT_LO

    def mk(xs, m, tag, i):
        out, g = run(witness, xs, m)
        return {"family": family, "prompt": T4._prompt(family, xs, m),
                "gold": str(out), "key": "t4-%s-%d" % (tag, i), "_guard": g}

    ce = []
    for i in range(40):
        r = random.Random(E.tribunal_entropy("t4-" + family, 10_000 + i))
        k = r.choice([2, 3, min(80, L), L])
        xs = [r.randint(2, 30)] * k if i % 3 == 0 else T4._rand_list(r, k)
        q = r.randint(QUERY_LO, 97)
        r.choice([1, 2, q])                    # consumed exactly as v1 does; discarded
        ce.append(mk(xs, q, "ce", i))
    bat = {"ext": base["ext"], "stress": base["stress"], "ce": ce, "order": base["order"]}
    _BAT[key] = bat
    return bat


class TribunalT4v1a(T4.TribunalT4):
    NAME = NAME

    def __init__(self, family):
        if re.search(r"\d", family):
            raise ValueError("T4: family names must be digit-free: %r" % family)
        self.family = family
        self.witness = T4._P.witness(family)
        self.profile = family_profile(self.witness)

    def score(self, artifact, n=150) -> Dict:
        bat = batteries(self.family, self.witness, self.profile["L_max"], n)
        reasons = list(self.profile["reasons"])
        allt = [t for v in bat.values() for t in v]
        if any(t["gold"] == "None" for t in allt):
            reasons.append("NONE_ON_DOMAIN")
        if any(t["_guard"] for t in allt):
            reasons.append("GUARD_ON_DOMAIN")

        def acc(instances):
            rr = E.Recipient.fresh(seed=4242)
            rr.load(artifact)
            inst = [{k: v for k, v in t.items() if k != "_guard"} for t in instances]
            return rr.run_tasks(inst, E.Escrow(10 ** 7))["accuracy"]

        return {"tribunal": NAME,
                "held_out_extrapolation": acc(bat["ext"]),
                "stress_at_domain_max": acc(bat["stress"]),
                "counterexample_accuracy": acc(bat["ce"]),
                "order_battery_accuracy": acc(bat["order"]),
                "domain_L_max": self.profile["L_max"],
                "family_admissible": not reasons,
                "family_reasons": sorted(set(reasons))}


# ---------------------------------------------------------------- direct (program-level) scoring
_NUM = re.compile(r"-?\d+")


def direct_score(prog, family, witness, version="v1", n=150):
    """Program-level T4 score without artifact emission: runs `prog` on the
    battery inputs and compares with the witness gold. Same thresholds as
    TribunalT4.qualified. Validated against a18_c1.t4_qualified in
    w7_t4dev.py (validation block)."""
    prof = (T4.family_profile if version == "v1" else family_profile)(witness)
    bat = (T4.batteries if version == "v1" else batteries)(family, witness, prof["L_max"], n)
    reasons = list(prof["reasons"])
    allt = [t for v in bat.values() for t in v]
    if any(t["gold"] == "None" for t in allt):
        reasons.append("NONE_ON_DOMAIN")
    if any(t["_guard"] for t in allt):
        reasons.append("GUARD_ON_DOMAIN")
    accs, fails = {}, {}
    for k, items in bat.items():
        ok, fl = 0, []
        for t in items:
            nums = [int(x) for x in _NUM.findall(t["prompt"])]
            got = run(prog, nums[:-1], nums[-1])[0]
            if str(got) == t["gold"]:
                ok += 1
            else:
                fl.append((len(nums) - 1, nums[-1]))
        accs[k] = ok / len(items)
        fails[k] = fl
    q = (not reasons) and all(a >= T4.THRESH for a in accs.values())
    return {"qualified": q, "acc": accs, "fails": fails, "reasons": sorted(set(reasons)),
            "L_max": prof["L_max"]}
