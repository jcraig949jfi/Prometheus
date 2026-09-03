"""G15 HOSTILE QUALIFICATION HARNESS.

Attacks the frozen ledger candidate as a hostile distributed financial
system. Success criterion for the attacker: ANY accepted history violating
the conserved-risk criteria (mission section III, A-N).

Battery sections:
  H1  torn-tail purchase erasure           (attack N/G: rollback via crash)
  H2  anchor-window suffix replacement     (attack C/G)
  H3  logical-time bomb + freeze           (attack L: TTL semantics)
  H4  geometric reservation grab           (attack: 25%-cap circumvention)
  H5  free-form rule commitment            (attack E: doctored R / tie / bet)
  H6  block-id burn griefing               (attack D: cross-candidate DoS)
  H7  namespace laundering                 (attack K: calib -> scientific)
  H8  canonicalization collisions          (attack I)
  H9  duplicate/replay/reorder/corrupt log (attack L)
  H10 crash injection at every append      (attack G)
  H11 concurrency: second writer           (attack H)
  H12 generative fuzz: random op storms with conservation asserted after
      every accepted transition, plus differential service-vs-verifier check
  H13 halt-state bypass attempts
  H14 K/TTL/rational boundary cases

Each attack reports ATTACK-SUCCEEDED (a defect: preserved, then fixed) or
REFUSED/CONSERVED. The harness is version-agnostic: run it against the
frozen v1.0 candidate to harvest exploits, and against the repaired version
to verify regressions.

Run:  python -m prodledger.hostile <workdir>
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from .core import Refused, derived_block_id
from .store import LedgerStore, HeadAnchor, StoreError, ROOT
from .canon import candidate_id, canonical_candidate, CanonError, canon_bytes
from . import LEDGER_VERSION
from .verify import verify, VerifyError, human_report

RESULTS = []


def report(attack, outcome, detail=""):
    RESULTS.append((attack, outcome, detail))
    mark = {"DEFECT": "!! ATTACK SUCCEEDED", "OK": "   refused/conserved",
            "INFO": "   info"}[outcome]
    print(f"{mark} | {attack}" + (f" -- {detail}" if detail else ""))


def fresh(workdir, name):
    d = os.path.join(workdir, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    anchor = HeadAnchor(os.path.join(d, "anchor.jsonl"))
    store = LedgerStore(os.path.join(d, "ledger.jsonl"), anchor)
    store.append({"type": "GENESIS", "lt": 0,
                  "ledger_version": LEDGER_VERSION, "config_hash": "cfg-test"})
    return store, d


def base_candidate(ns="SCIENTIFIC", K=1000, fam="famA", **kw):
    d = {"schema_version": "cand.v1", "namespace": ns, "family_id": fam,
         "subject": "subj-1", "delta_star": "d-1",
         "ref_rule": "CANON-R-V1", "context_rule": "CANON-W-V1",
         "role_rule": "CANON-PI-V1", "tie_rule": "BEACON_UNIFORM",
         "detector": "det-1", "betting_rule": "LAM-MIX-V1",
         "K": K, "block_budget": 32}
    d.update(kw)
    return d


def reg_event(store, cand, lt, sel=()):
    cid = candidate_id(cand)
    store.append({"type": "CANDIDATE_REGISTER", "lt": lt, "cand_id": cid,
                  "family_id": cand["family_id"], "ns": cand["namespace"],
                  "K": cand["K"], "block_budget": cand["block_budget"],
                  "m_refs": cand.get("m_refs", 3),
                  "selection_blocks": list(sel),
                  "commit_hash": cid, "betting_rule": cand["betting_rule"],
                  "ref_rule": cand["ref_rule"],
                  "context_rule": cand["context_rule"],
                  "role_rule": cand["role_rule"],
                  "tie_rule": cand["tie_rule"], "detector": cand["detector"]})
    return cid


def seal_mock(store, cid, lt, anchor_time=200):
    store.append({"type": "ANCHOR_ATTEST", "lt": lt, "cand_id": cid,
                  "payload_hash": cid, "anchor_time": anchor_time,
                  "anchor_id": f"a-{cid[:8]}", "provider": "mock-anchor",
                  "mock": True})
    store.append({"type": "BEACON_ATTEST", "lt": lt + 1, "cand_id": cid,
                  "round_id": 21, "round_id_expected": 21,
                  "round_time": anchor_time + 10, "value_hex": "beef" * 8,
                  "provider": "mock-beacon", "mock": True})


# ======================================================================
def h1_torn_tail(workdir):
    """Append an acknowledged purchase, then truncate the file mid-line
    (crash simulation). If restart silently drops the purchase and the
    verifier accepts the shortened history, purchased risk was refunded."""
    store, d = fresh(workdir, "h1")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    cid = reg_event(store, base_candidate(), 2)      # acknowledged purchase
    path, anchors = store.path, store.anchor.path
    store.close()
    raw = open(path, "rb").read()
    open(path, "wb").write(raw[:len(raw) - 9])       # torn tail
    try:
        s2 = LedgerStore(path, HeadAnchor(anchors))
        gone = cid not in s2.state.candidates
        purchased = s2.state.pools["SCIENTIFIC"]["purchased"]
        s2.close()
        if gone and purchased == 0:
            try:
                verify(path)
                report("H1 torn-tail purchase erasure", "DEFECT",
                       "acknowledged 1/K purchase erased by crash recovery; "
                       "verifier accepts the shortened history")
            except VerifyError:
                report("H1 torn-tail purchase erasure", "OK",
                       "verifier rejected")
        else:
            report("H1 torn-tail purchase erasure", "OK",
                   "purchase survived recovery")
    except StoreError as e:
        report("H1 torn-tail purchase erasure", "OK", f"refused start: {e}")


def h2_suffix_replacement(workdir):
    """Truncate back to the last ANCHORED head and append a different valid
    suffix. If the service restarts happily, everything between anchors is
    rewritable -- purchases, halts, co-signs."""
    store, d = fresh(workdir, "h2")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    anchored_lines = sum(1 for _ in open(store.path))  # after any sync anchor
    last_anchor = store.anchor.latest()
    cid = reg_event(store, base_candidate(), 2)        # maybe unanchored
    path, anchors = store.path, store.anchor.path
    store.close()
    lines = open(path, "rb").read().splitlines(keepends=True)
    n_anch = last_anchor["n"] if last_anchor else 1
    open(path, "wb").write(b"".join(lines[:n_anch]))   # roll back to anchor
    try:
        s2 = LedgerStore(path, HeadAnchor(anchors))
        refunded = s2.state.pools["SCIENTIFIC"]["purchased"] == 0 \
            and cid not in s2.state.candidates
        s2.close()
        if refunded:
            report("H2 anchor-window suffix replacement", "DEFECT",
                   "purchase between anchors erased; restart accepted the "
                   "rolled-back log")
        else:
            report("H2 anchor-window suffix replacement", "OK")
    except StoreError as e:
        report("H2 anchor-window suffix replacement", "OK",
               f"refused start: {e}")


def h3_lt_bomb(workdir):
    """Submit an event with lt=2^60. If accepted (or if its refusal advances
    the clock), every family TTL detonates and future lt is unusable."""
    store, d = fresh(workdir, "h3")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 100})
    bombed = False
    try:
        store.append({"type": "FAMILY_OPEN", "lt": 1 << 60,
                      "family_id": "famB", "ns": "CALIBRATION",
                      "reserve": "1/4", "ttl_lt": 10})
        bombed = True
    except Refused:
        pass
    famA = store.state.families["famA"]
    clock = store.state.lt
    store.close()
    if bombed or clock >= (1 << 60):
        report("H3 logical-time bomb", "DEFECT",
               f"clock advanced to {clock}; famA open={famA['open']}")
    elif not famA["open"]:
        report("H3 logical-time bomb", "DEFECT",
               "refused event still mass-expired families")
    else:
        report("H3 logical-time bomb", "OK",
               f"clock={clock}, famA still open")


def h4_geometric_grab(workdir):
    """Repeated compliant opens: does one actor capture most of the pool
    without a co-signature?"""
    store, d = fresh(workdir, "h4")
    grabbed = Fraction(0)
    n = 0
    try:
        for i in range(17):
            u = store.state.pools["SCIENTIFIC"]["unreserved"]
            r = u * Fraction(1, 4)
            if r <= 0:
                break
            store.append({"type": "FAMILY_OPEN", "lt": 1 + i,
                          "family_id": f"grab{i}", "ns": "SCIENTIFIC",
                          "reserve": f"{r.numerator}/{r.denominator}",
                          "ttl_lt": 1_000_000})
            grabbed += r
            n += 1
    except Refused:
        pass
    frac_of_pool = grabbed / Fraction(1, 10)
    store.close()
    if frac_of_pool > Fraction(1, 2):
        report("H4 geometric reservation grab", "DEFECT",
               f"{n} compliant opens captured {float(frac_of_pool):.0%} "
               f"of the scientific pool, no co-signature")
    else:
        report("H4 geometric reservation grab", "OK",
               f"capped at {float(frac_of_pool):.0%}")


def h5_freeform_rules(workdir):
    """Register with doctored rule commitments: a bespoke reference rule, a
    'delta* wins ties' tie rule, a super-fair betting rule. If the ledger
    accepts arbitrary strings, the rank lemma's validation clause is void."""
    store, d = fresh(workdir, "h5")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    doctored = base_candidate(ref_rule="my-rejection-sampler-v2",
                              tie_rule="CANDIDATE_WINS_TIES",
                              betting_rule="pay-3.25-top-AND-0.5-bottom")
    try:
        reg_event(store, doctored, 2)
        report("H5 free-form rule commitment", "DEFECT",
               "doctored R / tie / betting rules accepted as commitments")
    except Refused as e:
        report("H5 free-form rule commitment", "OK", str(e)[:60])
    store.close()


def h6_block_burn(workdir):
    """Attacker consumes a victim's predictable future block ids."""
    store, d = fresh(workdir, "h6")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    victim = reg_event(store, base_candidate(subject="victim"), 2)
    attacker = reg_event(store, base_candidate(subject="attacker"), 3)
    seal_mock(store, victim, 4)
    seal_mock(store, attacker, 6, anchor_time=300)
    vict_b0 = derived_block_id(victim, 0)
    try:
        store.append({"type": "EVIDENCE_BLOCK", "lt": 8,
                      "cand_id": attacker, "block_id": vict_b0,
                      "wealth": "2/1", "derivation_beacon": "beef" * 8})
        try:
            store.append({"type": "EVIDENCE_BLOCK", "lt": 9,
                          "cand_id": victim, "block_id": vict_b0,
                          "wealth": "2/1", "derivation_beacon": "beef" * 8})
            report("H6 block-id burn griefing", "OK", "no collision")
        except Refused:
            report("H6 block-id burn griefing", "DEFECT",
                   "attacker consumed the victim's block id; victim refused")
    except Refused as e:
        report("H6 block-id burn griefing", "OK", str(e)[:60])
    store.close()


def h7_namespace_laundering(workdir):
    """Every path from calibration rights to scientific admission."""
    store, d = fresh(workdir, "h7")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "cal",
                  "ns": "CALIBRATION", "reserve": "1/1", "ttl_lt": 10_000})
    defects = []
    # (a) calibration candidate with K below scientific floor, then try to
    # admit it with a SCIENTIFIC record type
    cand = base_candidate(ns="CALIBRATION", fam="cal", K=100)
    cid = reg_event(store, cand, 2)
    seal_mock(store, cid, 3)
    store.append({"type": "EVIDENCE_BLOCK", "lt": 6, "cand_id": cid,
                  "block_id": derived_block_id(cid, 0), "wealth": "200/1",
                  "derivation_beacon": "beef" * 8})
    try:
        store.append({"type": "ADMISSION", "lt": 7, "cand_id": cid,
                      "record_type": "SCIENTIFIC_ADMITTED"})
        defects.append("calibration candidate admitted as SCIENTIFIC")
    except Refused:
        pass
    # (b) scientific candidate riding mock attestations to admission
    store.append({"type": "FAMILY_OPEN", "lt": 8, "family_id": "sci",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    cand2 = base_candidate(fam="sci")
    cid2 = reg_event(store, cand2, 9)
    seal_mock(store, cid2, 10)                    # mock=True attestations
    store.append({"type": "EVIDENCE_BLOCK", "lt": 13, "cand_id": cid2,
                  "block_id": derived_block_id(cid2, 0), "wealth": "2000/1",
                  "derivation_beacon": "beef" * 8})
    try:
        store.append({"type": "ADMISSION", "lt": 14, "cand_id": cid2,
                      "record_type": "SCIENTIFIC_ADMITTED"})
        defects.append("scientific admission on MOCK attestations")
    except Refused:
        pass
    # (c) same canonical candidate re-registered across namespaces
    try:
        cand3 = dict(cand2)
        cand3["namespace"] = "CALIBRATION"
        cand3["family_id"] = "cal"
        cid3 = candidate_id(cand3)
        if cid3 == cid2:
            defects.append("cross-namespace id collision")
    except CanonError:
        pass
    store.close()
    if defects:
        report("H7 namespace laundering", "DEFECT", "; ".join(defects))
    else:
        report("H7 namespace laundering", "OK",
               "all three laundering paths refused")


def h8_canonicalization(workdir):
    """Field order, unicode forms, explicit defaults, duplicate keys."""
    a = base_candidate(subject="café")                 # composed
    b = dict(reversed(list(base_candidate(subject="café").items())))
    c = base_candidate(subject="café", m_refs=3)       # explicit default
    ia, ib, ic = candidate_id(a), candidate_id(b), candidate_id(c)
    ok = (ia == ib == ic)
    try:
        from .canon import parse_strict
        parse_strict('{"K":1000,"K":100}')
        dup_ok = False
    except CanonError:
        dup_ok = True
    try:
        candidate_id(base_candidate(evil="x"))
        unknown_ok = False
    except CanonError:
        unknown_ok = True
    if ok and dup_ok and unknown_ok:
        report("H8 canonicalization collisions", "OK",
               "NFC + order + defaults collapse; dup keys and unknown "
               "fields refused")
    else:
        report("H8 canonicalization collisions", "DEFECT",
               f"identity stable={ok} dup_refused={dup_ok} "
               f"unknown_refused={unknown_ok}")


def h9_log_tampering(workdir):
    """Replay, reorder, interior corruption -- verifier and restart must
    reject all three."""
    store, d = fresh(workdir, "h9")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    reg_event(store, base_candidate(), 2)
    path, anchors = store.path, store.anchor.path
    store.close()
    lines = open(path, "rb").read().splitlines(keepends=True)
    outcomes = []
    for name, mutant in [
            ("replay", lines + [lines[1]]),
            ("reorder", [lines[0], lines[2], lines[1]] + lines[3:]),
            ("interior-corrupt", [lines[0], lines[1][:40] + b"X" +
                                  lines[1][41:]] + lines[2:])]:
        mpath = os.path.join(d, f"mut-{name}.jsonl")
        open(mpath, "wb").write(b"".join(mutant))
        try:
            verify(mpath)
            outcomes.append(f"{name}: ACCEPTED")
        except (VerifyError, Exception):
            outcomes.append(f"{name}: rejected")
    bad = [o for o in outcomes if "ACCEPTED" in o]
    report("H9 replay/reorder/corrupt", "DEFECT" if bad else "OK",
           "; ".join(outcomes))


def h10_crash_everywhere(workdir):
    """Truncate the log at EVERY byte boundary of the final record and
    restart: state must always equal a fold of some acknowledged prefix,
    and conservation must hold."""
    store, d = fresh(workdir, "h10")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    reg_event(store, base_candidate(), 2)
    path, anchors = store.path, store.anchor.path
    store.close()
    raw = open(path, "rb").read()
    tail_start = raw.rfind(b"\n", 0, len(raw) - 1) + 1
    failures = 0
    for cut in range(tail_start + 1, len(raw)):
        open(path, "wb").write(raw[:cut])
        try:
            s2 = LedgerStore(path, HeadAnchor(anchors))
            s2.state.assert_conserved()
            s2.close()
        except StoreError:
            pass                                   # refuse-to-start is fine
        except AssertionError:
            failures += 1
        for lock in [path + ".lock"]:
            if os.path.exists(lock):
                os.remove(lock)
    open(path, "wb").write(raw)
    report("H10 crash injection at every tail byte",
           "DEFECT" if failures else "OK",
           f"{len(raw)-tail_start-1} cut points, {failures} conservation "
           f"breaks")


def h11_second_writer(workdir):
    store, d = fresh(workdir, "h11")
    try:
        s2 = LedgerStore(store.path, store.anchor)
        s2.close()
        report("H11 second concurrent writer", "DEFECT", "lock bypassed")
    except StoreError:
        report("H11 second concurrent writer", "OK", "exclusive lock held")
    store.close()


def h12_fuzz(workdir, n_ops=30_000):
    """Random op storm; after every ACCEPTED op, assert conservation and
    (periodically) differential-check service state vs independent verifier."""
    from wforge.world import stream
    rng = stream("g15-fuzz")
    store, d = fresh(workdir, "h12")
    lt = [1]
    fams = []
    cands = []
    accepted = refused = 0

    def nlt():
        lt[0] += rng.below(3)
        return lt[0]

    for i in range(n_ops):
        op = rng.below(10)
        try:
            if op <= 2:
                fid = f"f{rng.below(200)}"
                ns = "SCIENTIFIC" if rng.below(2) else "CALIBRATION"
                num = 1 + rng.below(50)
                den = 40 + rng.below(4000)
                store.append({"type": "FAMILY_OPEN", "lt": nlt(),
                              "family_id": fid, "ns": ns,
                              "reserve": f"{num}/{den}",
                              "ttl_lt": 1 + rng.below(5000)})
                fams.append((fid, ns))
            elif op <= 4 and fams:
                fid, ns = fams[rng.below(len(fams))]
                K = [100, 999, 1000, 2000, 5000][rng.below(5)]
                cand = base_candidate(ns=ns, fam=fid, K=K,
                                      subject=f"s{i}")
                cid = reg_event(store, cand, nlt())
                cands.append(cid)
            elif op == 5 and fams:
                fid, _ = fams[rng.below(len(fams))]
                store.append({"type": "FAMILY_CLOSE", "lt": nlt(),
                              "family_id": fid})
            elif op == 6 and cands:
                cid = cands[rng.below(len(cands))]
                seal_mock(store, cid, nlt(),
                          anchor_time=200 + rng.below(1000))
            elif op == 7 and cands:
                cid = cands[rng.below(len(cands))]
                idx = store.state.candidates.get(cid, {}).get("blocks", 0)
                bid = (derived_block_id(cid, idx) if rng.below(4)
                       else f"forged-{rng.below(99)}")
                store.append({"type": "EVIDENCE_BLOCK", "lt": nlt(),
                              "cand_id": cid, "block_id": bid,
                              "wealth": f"{rng.below(3000)}/1",
                              "derivation_beacon": "beef" * 8})
            elif op == 8 and cands:
                cid = cands[rng.below(len(cands))]
                ns = store.state.candidates.get(cid, {}).get("ns")
                rt = ("SCIENTIFIC_ADMITTED" if ns == "SCIENTIFIC"
                      else "CALIBRATION_ADMITTED")
                if rng.below(6) == 0:              # forgery attempt
                    rt = ("CALIBRATION_ADMITTED" if rt.startswith("SCI")
                          else "SCIENTIFIC_ADMITTED")
                store.append({"type": "ADMISSION", "lt": nlt(),
                              "cand_id": cid, "record_type": rt})
            else:
                malformed = {"type": ["FAMILY_OPEN", "XX", "ADMISSION"]
                             [rng.below(3)], "lt": nlt() if rng.below(2)
                             else -5, "family_id": "f0", "ns": "Scientific",
                             "reserve": "0.1"}
                store.append(malformed)
            accepted += 1
        except (Refused, CanonError):
            refused += 1
        except StoreError:
            break
        store.state.assert_conserved()
    sci = store.state.pools["SCIENTIFIC"]
    over = sci["purchased"] > sci["budget"]
    path = store.path
    store.close()
    rep = verify(path)                             # differential + audit
    report("H12 generative fuzz", "DEFECT" if over else "OK",
           f"{accepted} accepted / {refused} refused ops; scientific "
           f"purchased={sci['purchased']} <= 1/10; verifier: "
           f"{rep['records']} records re-verified at every prefix")


def h13_halt_bypass(workdir):
    store, d = fresh(workdir, "h13")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    store.append({"type": "HALT_SET", "lt": 2, "reason": "sham-arm signal"})
    defects = []
    try:
        reg_event(store, base_candidate(subject="during-halt"), 3)
        defects.append("scientific purchase during halt")
    except Refused:
        pass
    try:
        store.append({"type": "HALT_LIFT", "lt": 4, "actor": "operator",
                      "adjudication_ref": "self"})
        defects.append("operator lifted the halt")
    except Refused:
        pass
    cal = base_candidate(ns="CALIBRATION", fam="calfam", K=100,
                         subject="cal-during-halt")
    store.append({"type": "FAMILY_OPEN", "lt": 5, "family_id": "calfam",
                  "ns": "CALIBRATION", "reserve": "1/1", "ttl_lt": 10_000})
    try:
        reg_event(store, cal, 6)                   # calibration must proceed
    except Refused:
        defects.append("halt wrongly blocked segregated calibration work")
    store.close()
    report("H13 halt-state bypass", "DEFECT" if defects else "OK",
           "; ".join(defects) if defects else
           "scientific blocked, operator lift refused, calibration allowed")


def h14_boundaries(workdir):
    store, d = fresh(workdir, "h14")
    store.append({"type": "FAMILY_OPEN", "lt": 1, "family_id": "famA",
                  "ns": "SCIENTIFIC", "reserve": "1/40", "ttl_lt": 10_000})
    cases = []
    for K, bb, want in [(999, 32, False), (1000, 32, True),
                        (10**9, 4, False), (0, 32, False), (-5, 32, False),
                        (1000, 10**7, False)]:
        cand = base_candidate(K=K, subject=f"k{K}-{bb}")
        cand["block_budget"] = bb
        try:
            reg_event(store, cand, 2)
            cases.append((K, bb, True))
        except (Refused, CanonError):
            cases.append((K, bb, False))
    bad = [(K, bb) for (K, bb, got), (_, _, want) in
           zip(cases, [(999, 32, False), (1000, 32, True), (10**9, 4, False),
                       (0, 32, False), (-5, 32, False), (1000, 10**7, False)])
           if got != want]
    store.close()
    report("H14 K/TTL boundary cases", "DEFECT" if bad else "OK",
           f"mismatches: {bad}" if bad else "floor/ceiling/reachability all "
           "enforced")


def main():
    workdir = sys.argv[1] if len(sys.argv) > 1 else "g15_work"
    os.makedirs(workdir, exist_ok=True)
    print("=" * 74)
    print("G15 HOSTILE LEDGER QUALIFICATION")
    print("=" * 74)
    for fn in [h1_torn_tail, h2_suffix_replacement, h3_lt_bomb,
               h4_geometric_grab, h5_freeform_rules, h6_block_burn,
               h7_namespace_laundering, h8_canonicalization,
               h9_log_tampering, h10_crash_everywhere, h11_second_writer,
               h12_fuzz, h13_halt_bypass, h14_boundaries]:
        try:
            fn(workdir)
        except Exception as e:
            report(fn.__name__, "DEFECT", f"harness crash: {e!r}")
    n_def = sum(1 for _, o, _ in RESULTS if o == "DEFECT")
    print("=" * 74)
    print(f"ATTACKS SUCCEEDED: {n_def} / {len(RESULTS)}")
    print("=" * 74)
    return n_def


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
