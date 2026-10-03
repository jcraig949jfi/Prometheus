"""Generator for EXPECTED_ANSWERS.json (C-004-T005, Pallas). Hand-derived rows; no implementation is imported.

Run: python rso/slice001/expected/_build_expected.py   (writes EXPECTED_ANSWERS.json beside itself, LF, ASCII)
"""
import json
import os

Q = "QUALIFIED@AUTHOR_TESTED"
RESET_REASON = "forbidden influence across boundary <j>, first visible at <episode, tick>"
BLOCK_MISSING = "runtime inside the registered model"


def v(pred, scope, execution, authority, outcome, reason=None, **extra):
    d = {"predicate": pred, "scope": scope, "execution": execution, "authority": authority,
         "outcome": outcome, "reason": reason}
    d.update(extra)
    return d


def row(cid, determinacy, primary, others=(), claims=(), assumptions=(), gaps=(), derivation=""):
    return {"id": cid, "determinacy": determinacy,
            "execution": primary["execution"], "authority": primary["authority"],
            "outcome": primary["outcome"], "reason": primary["reason"],
            "primary": primary, "other_verdicts": list(others), "claims": list(claims),
            "assumptions": list(assumptions), "gaps": list(gaps), "derivation": derivation}


def claim(cid, eligibility, standing, why=None):
    return {"claim": cid, "eligibility": eligibility, "standing": standing, "why": why}


GAPS = {
    "G01": "BLIND FIXTURE DEFINITIONS. The behavioural definition of every A6 fixture except REG and PKTD "
           "(QCARRY, AMNESIAC, FLIP, LAGD, WIPE, PKTD_NOQ, HCOUNT, HEAL, BOOKKEEP, NULL, EVERY3, SLEEPER, SPLIT1, "
           "SPLIT2, OVERDELAY, REG-ONEHOT, REG-FLAT, LOSSY) sits in the A6 'expected' column, which R4 forbids the "
           "independent author to read. Outcome VALUES below come from the definitions, plan s4, A7 and the "
           "polarity in contract.json; first witnesses, boundaries, ticks and statistics that depend on fixture "
           "detail are stated as assumptions or left UNDETERMINED. Structural defect: a fixture's definition and "
           "its expected answer share one column, so the table cannot be both blind and complete.",
    "G02": "NO FAIL REASON FORM for P0 BOUNDS, P7 OBSERVER and P8 TWIN_EQ in draft A A5/A3, while B3.4 requires "
           "'FAIL reasons use the draft A forms'. The typed reason for P0.OVERDELAY, T07.HEAL and E06.LOSSY is "
           "therefore not determined by the readable contract.",
    "G03": "CANONICAL ORDER INCOMPLETE. A5 orders (history, boundary, cut point, target) but not the clamp value "
           "v of P5 nor the partner of a compared pair in P3/P4. P3 says 'any two histories' (79872 unordered "
           "pairs: 2048 + 14336 + 63488) while its eligible count 9600 = 2048 + 3584 + 3968 is (class size - 1) "
           "per class, i.e. comparison against one representative. The verdict is the same either way; the "
           "eligible count and the first-witness pair are not.",
    "G04": "RULER ON CLOCKED. The CLOCKED domain (how many histories; whether u inputs still vary) is not stated, "
           "nor which class-N policy is the RETENTION subject. With u_j fixed, no pair 'differs only in u_j', so "
           "the NEGATIVE condition holds vacuously for every runtime while the clock-following policy also has "
           "s = 1 (POSITIVE). P2's three values are not a partition outside the product domain.",
    "G05": "AUTHORITY WITH THE KEEPER STORE UNSET. B4.3: the consumer reads stages only from records registered "
           "with the keeper; R3: the store locator is UNSET at freeze. Whether in-memory fixture anchors count as "
           "'registered' for stage records (authority QUALIFIED@AUTHOR_TESTED) or every authority is UNQUALIFIED "
           "NO_STAGE_RECORD until Aporia sets the store is not stated. Every row below assumes the former.",
    "G06": "STANDING OF A PREREQUISITE WHOSE RECEIPT FAILS G-BIND (present but not bound) is not defined in B7.2: "
           "it could keep its own standing (headline UNMET through G-BIND FAIL) or count as absent (BLOCKED).",
    "G07": "G-INV PER-CLAIM SCOPE. B6.4 evaluates G-INV 'per claim over the nodes reachable from that claim', but "
           "a COMPLETED inventory row with no receipt is reachable from no node. Whether RUN_UNREPORTED hits one "
           "claim or every claim in the bundle is not determined (E02.MISSING).",
    "G08": "E02.RELABEL REASON CODE. node_id embeds the subject (B3.1). If the relabel renames node_ids the first "
           "failure is IDENTITY_UNKNOWN:<node_id> (or EVIDENCE_MISSING for CL-RET(REG), whose policy-named nodes "
           "vanish); if node_ids are kept it is SCOPE_MISMATCH:physics. The readable text does not say which.",
    "G09": "DANGLING REFERENCE AND UNSPECIFIED PARAMETER FORMATS. B3.1 says trace roles are given in 'B7.3'; no "
           "B7.3 exists. So <role> in BYTES_MISMATCH:<role>, <edge> in DEPENDENCY_MISMATCH:<edge> and <field> in "
           "OUTCOME_MISMATCH:<field> have no registered spelling.",
    "G10": "WHAT IS THE ANCHOR WHEN CUSTODY IS NOT EXERCISED. B9 notation: 'in-memory fixture anchors'. When the "
           "producer re-hashes the manifest (E01.OUTCOME_EDIT) or re-makes anchors (E03.REANCHOR), whether the "
           "consumer still holds the ORIGINAL in-memory anchor (G-BIND FAIL BYTES_MISMATCH) or accepts the "
           "producer's (G-BIND PASS, detection left to G-RECOMP / custody) is not stated.",
    "G11": "CUSTODY WHY LIST. Not stated whether `why` is exhaustive or first-only (E05.FAB_ANCHORS satisfies both "
           "ANCHORS_FROM_PRODUCER and KEEPER_ROW_MISSING). B5.1 prose gives the why as 'keeper named; record not "
           "registered' while B5.3 and R3 type it KEEPER_ROW_MISSING.",
    "G12": "AUTHORITY OF A BLOCKED EVALUATION. With BOUNDS FAIL every other predicate is BLOCKED; A5 preconditions "
           "(CHANNEL/OBSERVER need RESTART PASS) then reference a RESTART that did not run. Whether authority "
           "prints QUALIFIED or UNQUALIFIED PRECONDITION:RESTART on those lines is not stated (standing is "
           "BLOCKED either way).",
    "G13": "TWIN_EQ HAS NO EVIDENCE EDGES to the P0-P7 receipts it compares (B6.2), and TWIN(M, M') lists no "
           "G-BIND/G-INV prerequisite. A withdrawal of the RESTART stage therefore does not reach the TWIN line "
           "by the letter of B6.5, although P8 consumes RESTART outcomes.",
    "G14": "CUSTODY IS NOT A THREE-FIELD VERDICT, yet 'custody QUALIFIED' is a prerequisite of CL-CUST. Its "
           "standing when UNQUALIFIED is assumed UNQUALIFIED; B7.2 does not say.",
    "G15": "E05.KEEPER AND E05.FAB_REGISTERED NEED A SET STORE. Under R3 (store UNSET) the only real-store result "
           "available is UNQUALIFIED KEEPER_ROW_MISSING; the QUALIFIED answers below are for the logic exercised "
           "with fixture keeper rows, or for T020 after amendment v1.0.1.",
}

A_BLIND = "fixture behaviour read only from its name, the plan s4 row, A7 and contract.json polarity (G01)"
A_AUTH = "stage records count as registered under in-memory fixture anchors (G05)"

REG_ALL = [
    v("BOUNDS", "REG", "RAN", Q, "PASS"),
    v("CALIBRATION", "STANDARD", "RAN", Q, "PASS", "max over N = 1/2; u_j balanced 2048/4096 for j = 1, 2, 3",
      eligible_count=98304),
    v("RETENTION", "REG", "RAN", Q, "POSITIVE", statistic="1/1", successes=12288, trials=12288),
    v("ERASE", "REG", "RAN", Q, "PASS", eligible_count=9600),
    v("PRESERVE", "REG", "RAN", Q, "PASS", eligible_count=6144, applicable_count=6144, vacuous=False),
    v("CHANNEL", "REG", "RAN", Q, "PASS", eligible_count=24576),
    v("RESTART", "REG", "RAN", Q, "PASS", eligible_count=237568),
]

G0_CLAIMS = [
    claim("CL-CAL(STANDARD)", "ELIGIBLE", "SATISFIED"),
    claim("CL-RET(REG)", "ELIGIBLE", "SATISFIED", "11 instruments, lowest stage AUTHOR_TESTED"),
    claim("CL-RET(PKTD)", "ELIGIBLE", "SATISFIED"),
    claim("CL-RET(LAGD)", "NOT_ELIGIBLE", "UNMET", "ERASE(LAGD) FAIL; a correctly bound negative, not a binding defect"),
    claim("CL-CUST(G0)", "NOT_ELIGIBLE", "UNQUALIFIED", "custody UNQUALIFIED KEEPER_ROW_MISSING (R3; G14)"),
    claim("TWIN(REG, REG-ONEHOT)", "REPORTED", "SATISFIED", "TWIN_EQ PASS, reported only; one physics"),
]
G0_GATES = [
    v("G-INV", "per claim", "RAN", Q, "PASS"),
    v("G-RECOMP", "per CL-RET claim", "RAN", Q, "PASS", "recomputed CALIBRATION, RETENTION, ERASE, PRESERVE, CHANNEL equal the receipts"),
    v("custody", "G0", "n/a", "n/a", "UNQUALIFIED", "KEEPER_ROW_MISSING"),
]


def g0(cid):
    return row(cid, "DETERMINED_UNDER_ASSUMPTION",
               v("G-BIND", "every claim of G0", "RAN", Q, "PASS", None),
               G0_GATES, G0_CLAIMS, [A_AUTH, "draft A outcomes for REG, PKTD, LAGD as derived in the T rows"],
               ["G05", "G14"],
               "Unedited reference bundle: every node present, bound, deps complete, bytes match, inventory "
               "terminal. Each claim is decided on its own subgraph; LAGD's ERASE FAIL makes CL-RET(LAGD) UNMET "
               "without touching the other claims. Custody is printed UNQUALIFIED and is a prerequisite of "
               "CL-CUST only (R2).")


def with_claims(overrides):
    out = []
    for c in G0_CLAIMS:
        out.append(overrides.get(c["claim"], c))
    return out


ROWS = [
    # ---------------- T01
    row("T01.REG", "DETERMINED", v("RETENTION", "REG on STANDARD", "RAN", Q, "POSITIVE", "s = 1 on the exact domain",
                                   statistic="1/1", successes=12288, trials=12288,
                                   per_boundary=[{"j": 1, "statistic": "1/1"}, {"j": 2, "statistic": "1/1"}, {"j": 3, "statistic": "1/1"}]),
        [REG_ALL[1]], [claim("CL-RET(REG)", "ELIGIBLE", "SATISFIED", "given OBSERVER PASS for its registered observers and the consumer gates")],
        [A_AUTH], ["G05"],
        "REG is defined in readable text: a := u_e at CUE, reset keeps a, PROBE_A of episode j+1 returns a = u_j. "
        "4096 x 3 = 12288 trials, all correct."),
    row("T01.PKTD", "DETERMINED", v("RETENTION", "PKTD on STANDARD", "RAN", Q, "POSITIVE", "s = 1 on the exact domain",
                                    statistic="1/1", successes=12288, trials=12288),
        [], [claim("CL-RET(PKTD)", "ELIGIBLE", "SATISFIED")], [A_AUTH], ["G05"],
        "PKTD differs from REG only in how d is set (k = 0 packet, delivered before PROBE_D of the same episode); "
        "a is handled as in REG."),
    row("T01.QCARRY", "DETERMINED_UNDER_ASSUMPTION",
        v("CHANNEL", "QCARRY", "RAN", Q, "FAIL", "retained answer does not follow the declared allowed channel at 1",
          eligible_count=24576, witness_assumed="history all-zero, boundary 1, v = 1 (y_A = u_1 = 0)"),
        [v("RETENTION", "QCARRY", "RAN", Q, "POSITIVE", statistic="1/1", successes=12288, trials=12288),
         v("ERASE", "QCARRY", "RAN", Q, "PASS", "only allowed content (u_j) crosses, although through chan"),
         v("PRESERVE", "QCARRY", "RAN", Q, "PASS", applicable_count=6144, vacuous=False),
         v("RESTART", "QCARRY", "RAN", Q, "PASS")],
        [claim("CL-RET(QCARRY)", "NOT_ELIGIBLE", "UNMET", "CHANNEL(QCARRY) FAIL")],
        [A_BLIND, "QCARRY sends u with k >= 1, its reset does not flush that packet, PROBE_A answers from the delivery",
         "QCARRY capture/restore is complete (RESTART PASS), else CHANNEL would be UNQUALIFIED PRECONDITION:RESTART and the standing UNQUALIFIED",
         "v is ordered after boundary in the witness order (G03)"], ["G01", "G03"],
        "R1 and A7 (readable): the right answer carried through the FORBIDDEN channel passes ERASE and answers "
        "correctly; clamping a := v after the reset does not move y_A, so P5 FAILs whenever v != u_j (12288 of "
        "24576 clamped runs)."),
    # ---------------- T02
    row("T02.AMNESIAC", "DETERMINED",
        v("RETENTION", "AMNESIAC on STANDARD", "RAN", Q, "NEGATIVE", "y_A never depends on u_j; exact 1/2",
          statistic="1/2", successes=6144, trials=12288),
        [v("CALIBRATION", "STANDARD", "RAN", Q, "PASS", "max over N = 1/2; u_j balanced", eligible_count=98304),
         v("PRESERVE", "AMNESIAC", "RAN", Q, "PASS", "vacuous: 0 applicable", applicable_count=0, vacuous=True),
         v("CHANNEL", "AMNESIAC", "RAN", Q, "UNDETERMINED", "depends on whether AMNESIAC answers from `a` (PASS) or from a constant (FAIL); blind (G01)")],
        [claim("CL-RET(AMNESIAC)", "NOT_ELIGIBLE", "UNMET", "CALIBRATION gate PASS; RETENTION ruler NEGATIVE (exact 1/2): a correct scientific observation")],
        [A_AUTH, A_BLIND], ["G01"],
        "B7.2 and closure C1 (readable) fix this row: a no-carry runtime is inside class N, scores exactly "
        "6144/12288, and the answer is NEGATIVE, never a gate FAIL. PRESERVE vacuous assumes it carries nothing "
        "even without the reset."),
    row("T02.CLOCKED", "PARTLY_UNDETERMINED",
        v("CALIBRATION", "CLOCKED", "RAN", Q, "FAIL", "no-carry class reaches 1/1 > 1/2 at boundary 1"),
        [v("RETENTION", "class-N policy on CLOCKED", "RAN", "UNQUALIFIED: PRECONDITION:CALIBRATION", "UNDETERMINED",
           "the clock-following policy has s = 1 (POSITIVE by the letter) while the NEGATIVE condition also holds vacuously (G04); whatever is printed is not evidence on this world")],
        [claim("CL-CAL(CLOCKED)", "NOT_ELIGIBLE", "UNMET", "CALIBRATION(CLOCKED) FAIL")],
        [A_AUTH, "the policy j -> j mod 2 is in N and matches u_j at every evaluated boundary"], ["G04"],
        "u_j = j mod 2 is a function of j alone, so one of the 8 class-N policies is always right: the exact "
        "maximum over N is 1, not 1/2, and u_j is unbalanced. B4.2 (readable) gives the consequence: RETENTION "
        "runs, its outcome is printed, its authority is UNQUALIFIED. The ruler VALUE on this world is the gap."),
    row("T02.FLIP", "DETERMINED_UNDER_ASSUMPTION",
        v("RETENTION", "FLIP on STANDARD", "RAN", Q, "NOT_SHOWN", "the answer depends on u_j but s != 1",
          statistic_assumed="0/1 (0 of 12288) if FLIP answers the complement of a"),
        [v("CALIBRATION", "STANDARD", "RAN", Q, "PASS")],
        [claim("CL-RET(FLIP)", "NOT_ELIGIBLE", "UNMET", "RETENTION NOT_SHOWN")],
        [A_AUTH, A_BLIND], ["G01"],
        "B4.1 (readable) names T02 FLIP as the ruler's known NOT_SHOWN fire-test case. NOT_SHOWN covers s < 1/2 "
        "and s = 1/2 with dependence; the exact statistic depends on the blind fixture."),
    # ---------------- T03 - T05
    row("T03.REG", "DETERMINED", v("ERASE", "REG", "RAN", Q, "PASS", "no forbidden influence across boundaries 1-3 within H = 3", eligible_count=9600),
        [v("PRESERVE", "REG", "RAN", Q, "PASS", "allowed content survives the reset", eligible_count=6144, applicable_count=6144, vacuous=False)],
        [], [A_AUTH], ["G03", "G05"],
        "After REG's reset the whole state is (a = u_j, d = 0, chan empty), so every later output is a function "
        "of u_j and later inputs. Without the reset y_A still differs on all 6144 u_j-pairs, and with it too."),
    row("T04.LAGD", "DETERMINED_UNDER_ASSUMPTION",
        v("ERASE", "LAGD", "RAN", Q, "FAIL", RESET_REASON.replace("<j>", "1"),
          witness_assumed="boundary 1; pair (all-zero, f_1 = 1); with delay k = 1 first visible at episode 2, PROBE_A (y_D)"),
        [v("RETENTION", "LAGD", "RAN", Q, "POSITIVE", statistic="1/1"),
         v("PRESERVE", "LAGD", "RAN", Q, "PASS"), v("CHANNEL", "LAGD", "RAN", Q, "PASS"),
         v("RESTART", "LAGD", "RAN", Q, "PASS")],
        [claim("CL-RET(LAGD)", "NOT_ELIGIBLE", "UNMET", "ERASE(LAGD) FAIL")],
        [A_AUTH, A_BLIND, "LAGD = REG whose f travels as a packet with k >= 1 and whose reset clears d only"], ["G01", "G03"],
        "Plan T04 / A7: display-only erase, the forbidden packet is delivered after the boundary and changes an "
        "output inside the horizon. d reads 0 immediately after the reset; ERASE is behavioural and still FAILs. "
        "A5 coupling: RETENTION POSITIVE coexists with ERASE FAIL."),
    row("T04.REG", "DETERMINED", v("ERASE", "REG", "RAN", Q, "PASS", "no forbidden influence", eligible_count=9600), [], [], [A_AUTH], ["G05"],
        "Same derivation as T03.REG."),
    row("T05.WIPE", "DETERMINED_UNDER_ASSUMPTION",
        v("PRESERVE", "WIPE", "RAN", Q, "FAIL", "reset at 1 destroys allowed content carried without it",
          eligible_count=6144, applicable_count=6144, vacuous=False,
          witness_assumed="boundary 1; pair (all-zero, u_1 = 1)"),
        [v("ERASE", "WIPE", "RAN", Q, "PASS", "an indiscriminate wipe passes ERASE by construction"),
         v("RETENTION", "WIPE", "RAN", Q, "NEGATIVE", statistic="1/2", successes=6144, trials=12288),
         v("CHANNEL", "WIPE", "RAN", Q, "PASS", "assumed: PROBE_A still answers from a")],
        [claim("CL-RET(WIPE)", "NOT_ELIGIBLE", "UNMET", "PRESERVE FAIL and RETENTION NEGATIVE, both listed")],
        [A_AUTH, A_BLIND, "WIPE = REG whose reset also sets a := 0"], ["G01"],
        "A5 coupling (readable): the wipe is refused by PRESERVE and by RETENTION NEGATIVE, never rewarded. "
        "Without the reset y_A differs on every u_j pair (applicable 6144); with it y_A = 0 on both."),
    row("T05.REG", "DETERMINED", v("PRESERVE", "REG", "RAN", Q, "PASS", "allowed content survives the reset",
                                   eligible_count=6144, applicable_count=6144, vacuous=False), [], [], [A_AUTH], ["G05"],
        "Non-vacuous PASS: 6144 applicable pairs."),
    # ---------------- T06
    row("T06.REG", "DETERMINED", v("RESTART", "REG", "RAN", Q, "PASS", "continuations equal the uninterrupted run", eligible_count=237568), [], [], [A_AUTH], ["G05"],
        "REG's whole state is declared (a, d, chan) and captured; 4096 x 29 x 2 = 237568 continuations."),
    row("T06.PKTD", "DETERMINED", v("RESTART", "PKTD", "RAN", Q, "PASS", "continuations equal the uninterrupted run", eligible_count=237568), [], [], [A_AUTH], ["G05"],
        "The cut after CUE has a k = 0 packet in flight; a complete capture includes chan."),
    row("T06.PKTD_NOQ", "DETERMINED_UNDER_ASSUMPTION",
        v("RESTART", "PKTD_NOQ", "RAN", Q, "FAIL", "capture/restore loses future-influencing state at <cut>, target <t>",
          witness="UNDETERMINED: a cut after a CUE tick; which history/target is first depends on whether restore empties or keeps the stale queue (G01)"),
        [v("CHANNEL", "PKTD_NOQ", "RAN", "UNQUALIFIED: PRECONDITION:RESTART", "PASS"),
         v("OBSERVER", "PKTD_NOQ, any observer", "RAN", "UNQUALIFIED: PRECONDITION:RESTART", "as measured")],
        [claim("CL-RET(PKTD_NOQ)", "NOT_ELIGIBLE", "UNQUALIFIED", "worst standing: CHANNEL/OBSERVER UNQUALIFIED (PRECONDITION:RESTART) outranks RESTART UNMET; both listed")],
        [A_AUTH, A_BLIND, "PKTD_NOQ = PKTD whose capture omits chan"], ["G01"],
        "A7: continuation missing a checkpoint bit. The packet in flight between CUE and PROBE_D is lost (or a "
        "stale one kept under COMPLEMENT_PREFIX), so y_D differs. By B7.2 the headline standing is UNQUALIFIED, "
        "not UNMET."),
    row("T06.HCOUNT", "DETERMINED_UNDER_ASSUMPTION",
        v("RESTART", "HCOUNT", "RAN", Q, "FAIL", "capture/restore loses future-influencing state at <cut>, target <t>",
          witness="UNDETERMINED (G01)"),
        [v("CHANNEL", "HCOUNT", "RAN", "UNQUALIFIED: PRECONDITION:RESTART", "as measured"),
         v("OBSERVER", "HCOUNT, any observer", "RAN", "UNQUALIFIED: PRECONDITION:RESTART", "as measured")],
        [claim("CL-RET(HCOUNT)", "NOT_ELIGIBLE", "UNQUALIFIED", "CHANNEL/OBSERVER UNQUALIFIED (PRECONDITION:RESTART); RESTART UNMET listed")],
        [A_AUTH, A_BLIND, "HCOUNT keeps an undeclared episode counter that capture omits and that changes outputs from the second episode on"], ["G01"],
        "A7: cuts after every reset with continuation to the end of the life expose a counter restored to its "
        "initial value (FRESH) or left stale (COMPLEMENT_PREFIX)."),
    row("T06.LAGD", "DETERMINED_UNDER_ASSUMPTION",
        v("RESTART", "LAGD", "RAN", Q, "PASS", "a perfect capture carries the forbidden packet faithfully", eligible_count=237568),
        [v("ERASE", "LAGD", "RAN", Q, "FAIL", RESET_REASON.replace("<j>", "1"))],
        [claim("CL-RET(LAGD)", "NOT_ELIGIBLE", "UNMET", "ERASE FAIL; RESTART PASS alone does not establish reset")],
        [A_AUTH, A_BLIND], ["G01"],
        "The stated coupling (A5, plan T06): RESTART PASS with ERASE FAIL on the same runtime."),
    # ---------------- T07
    row("T07.HEAL", "DETERMINED_UNDER_ASSUMPTION",
        v("OBSERVER", "(REG, HEAL)", "RAN", Q, "FAIL", "UNDETERMINED: P7 has no registered FAIL reason form (G02)",
          part="OBS_EQ FAIL; CAPTURE_PURE PASS (REG's capture is pure)",
          witness="UNDETERMINED: whether the first difference is an output or a state captured after the observer action (G01)"),
        [], [claim("CL-RET(REG) with HEAL registered as used", "NOT_ELIGIBLE", "UNMET", "OBSERVER(REG, HEAL) FAIL")],
        [A_AUTH, A_BLIND, "HEAL changes a declared ALLOWED/FORBIDDEN component or an output and restores it before the final score"], ["G01", "G02"],
        "Plan T07 / A7 N9: state is captured after every observer action, so a flip repaired before the next "
        "tick is still seen. RESTART(REG) PASS, so the state part has authority."),
    row("T07.BOOKKEEP", "DETERMINED_UNDER_ASSUMPTION",
        v("OBSERVER", "(REG, BOOKKEEP)", "RAN", Q, "PASS", "outputs and declared non-BOOKKEEPING state identical to the null observer",
          eligible_count=196608), [], [claim("CL-RET(REG)", "ELIGIBLE", "SATISFIED")],
        [A_AUTH, A_BLIND, "BOOKKEEP writes only a declared BOOKKEEPING component (log_n)"], ["G01"],
        "BOOKKEEPING components are excluded from the state part and the outputs do not change. "
        "4096 x (24 + 24) = 196608."),
    row("T07.NULL", "DETERMINED", v("OBSERVER", "(REG, NULL)", "RAN", Q, "PASS", "the null observer equals itself; CAPTURE_PURE holds for REG",
                                    eligible_count=196608), [], [claim("CL-RET(REG)", "ELIGIBLE", "SATISFIED")], [A_AUTH], ["G05"],
        "OBS_EQ compares against the null observer; CAPTURE_PURE is a property of REG's capture."),
    # ---------------- T08
    row("T08.EVERY3", "DETERMINED_UNDER_ASSUMPTION",
        v("ERASE", "EVERY3", "RAN", Q, "FAIL", RESET_REASON.replace("<j>", "3"),
          witness_assumed="boundary 3 (the third reset call); boundaries 1 and 2 clean; pair (all-zero, f_3 = 1); first visible at episode 4, PROBE_A if the leak is an uncleared d"),
        [], [claim("CL-RET(EVERY3)", "NOT_ELIGIBLE", "UNMET", "ERASE FAIL")],
        [A_AUTH, A_BLIND, "the leaking call is call 3 (not calls 1 and 4)"], ["G01"],
        "A7: R = 3 exists so that the third call is evaluated. A check of boundary 1 only would pass this runtime."),
    row("T08.SLEEPER", "DETERMINED_UNDER_ASSUMPTION",
        v("ERASE", "SLEEPER", "RAN", Q, "FAIL", RESET_REASON,
          witness="UNDETERMINED: boundary 1 with first visibility in episode 3 if the hidden carry is f_e; boundary 2, episode 3 if it is u_e (forbidden at the NEXT boundary) (G01)"),
        [], [claim("CL-RET(SLEEPER)", "NOT_ELIGIBLE", "UNMET", "ERASE FAIL")], [A_AUTH, A_BLIND], ["G01"],
        "A7: lag 2 <= H = 3 and ERASE is behavioural, so undeclared hidden state is covered."),
    row("T08.SPLIT1", "DETERMINED_UNDER_ASSUMPTION",
        v("ERASE", "SPLIT1", "RAN", Q, "FAIL", RESET_REASON, witness="UNDETERMINED (G01)"),
        [], [claim("CL-RET(SPLIT1)", "NOT_ELIGIBLE", "UNMET", "ERASE FAIL")], [A_AUTH, A_BLIND], ["G01"],
        "Plan T08 / A7 'interacting leaks': forbidden content split into shares that separately look clean; the "
        "recombined influence reaches an output within the horizon."),
    row("T08.SPLIT2", "DETERMINED_UNDER_ASSUMPTION",
        v("ERASE", "SPLIT2", "RAN", Q, "FAIL", RESET_REASON, witness="UNDETERMINED (G01)"),
        [], [claim("CL-RET(SPLIT2)", "NOT_ELIGIBLE", "UNMET", "ERASE FAIL")], [A_AUTH, A_BLIND], ["G01"],
        "As SPLIT1; how the two fixtures differ is blind."),
    row("T08.REG", "DETERMINED", v("ERASE", "REG", "RAN", Q, "PASS", "clean at all three evaluated boundaries under repeated calls", eligible_count=9600),
        [], [], [A_AUTH], ["G05"], "Same derivation as T03.REG; REG's reset is identical on every call."),
    # ---------------- P0, E06
    row("P0.OVERDELAY", "DETERMINED_UNDER_ASSUMPTION",
        v("BOUNDS", "OVERDELAY", "RAN", Q, "FAIL", "UNDETERMINED: P0 has no registered FAIL reason form (G02); the fact is a send with k outside {0,1,2,3}"),
        [v("P1-independent predicates P2-P7", "OVERDELAY", "BLOCKED", "see G12", None, None, missing=[BLOCK_MISSING])],
        [claim("CL-RET(OVERDELAY)", "NOT_ELIGIBLE", "BLOCKED", "every other runtime predicate BLOCKED; BOUNDS UNMET listed")],
        [A_AUTH, A_BLIND, "OVERDELAY sends with k >= 4"], ["G01", "G02", "G12"],
        "A3: BOUNDS FAIL blocks every other predicate for that runtime with missing 'runtime inside the "
        "registered model'; outcome null. CALIBRATION(STANDARD) is a world predicate and is not blocked."),
    row("E06.REG_ONEHOT", "DETERMINED_UNDER_ASSUMPTION",
        v("TWIN_EQ", "(REG, REG-ONEHOT)", "RAN", Q, "PASS", "outcome vector of P0-P7 on the twin equals REG's"),
        [], [claim("TWIN(REG, REG-ONEHOT)", "REPORTED", "SATISFIED", "renders '<M'> has the outcome vector of <M> under <encoding id>; one physics'; no promotion; not an exit criterion")],
        [A_AUTH, A_BLIND, "the predicates are applied to the twin through its named encoding"], ["G01"],
        "A reversible re-encoding of every component preserves behaviour, so each of P0-P7 returns REG's value."),
    row("E06.REG_FLAT", "DETERMINED_UNDER_ASSUMPTION",
        v("TWIN_EQ", "(REG, REG-FLAT)", "RAN", Q, "PASS", "outcome vector of P0-P7 on the twin equals REG's"),
        [], [claim("TWIN(REG, REG-FLAT)", "REPORTED", "SATISFIED", "one physics; no promotion; not an exit criterion")],
        [A_AUTH, A_BLIND], ["G01"], "A flattened transition table of REG has REG's behaviour."),
    row("E06.LOSSY", "PARTLY_UNDETERMINED",
        v("TWIN_EQ", "(REG, LOSSY)", "RAN", Q, "FAIL", "UNDETERMINED: P8 has no registered FAIL reason form (G02)",
          witness="UNDETERMINED: which of P0-P7 differs depends on what the encoding loses (G01)"),
        [], [claim("TWIN(REG, LOSSY)", "REPORTED", "UNMET", "not an exit criterion")], [A_AUTH, A_BLIND], ["G01", "G02"],
        "Polarity false: a non-reversible encoding cannot reproduce REG's outcome vector."),
    # ---------------- E01
    g0("E01.G0"),
    row("E01.OUTCOME_EDIT", "DETERMINED_UNDER_ASSUMPTION",
        v("G-RECOMP", "CL-RET(LAGD)", "RAN", Q, "FAIL", "OUTCOME_MISMATCH:value",
          note="recomputed ERASE(LAGD) from the intact traces is FAIL; the receipt says PASS (witness also differs)"),
        [v("G-BIND", "CL-RET(LAGD)", "RAN", Q, "PASS", "the edit is self-consistent with the producer's re-hashed manifest"),
         v("G-INV", "CL-RET(LAGD)", "RAN", Q, "PASS")],
        with_claims({"CL-RET(LAGD)": claim("CL-RET(LAGD)", "NOT_ELIGIBLE", "UNMET", "G-RECOMP FAIL OUTCOME_MISMATCH:value; never ELIGIBLE")}),
        [A_AUTH, "the re-hashed manifest IS the anchor in non-custody mode (G10); if the consumer holds the original anchor the first failure is G-BIND FAIL BYTES_MISMATCH instead, and with keeper rows custody ROW_BLOB_MISMATCH"],
        ["G06", "G09", "G10"],
        "B10: 'reported outcome changed after the run: IN'. ERASE is in the recompute set, the traces are intact, "
        "so recomputation contradicts the rewritten receipt. The other claims' decision records are unchanged."),
    row("E01.FAB_CONSISTENT", "DETERMINED",
        v("G-BIND", "CL-RET(REG)", "RAN", Q, "PASS", None),
        [v("G-INV", "CL-RET(REG)", "RAN", Q, "PASS"), v("G-RECOMP", "CL-RET(REG)", "RAN", Q, "PASS", "fabricated traces recompute identically"),
         v("custody", "bundle", "n/a", "n/a", "UNQUALIFIED", "KEEPER_ROW_MISSING")],
        with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "ELIGIBLE", "SATISFIED", "NOT DETECTED, by design: the evidence contract passes and asserts nothing about the truth of the observation (B5.4)")}),
        [A_AUTH], ["G05"],
        "Coupling with E05: no predicate detects an internally consistent fabrication made before registration. "
        "The required behaviour is that no report words this PASS as truthful execution."),
    # ---------------- E02
    row("E02.MISSING", "DETERMINED_UNDER_ASSUMPTION",
        v("G-BIND", "CL-RET(REG)", "BLOCKED", Q, None, "EVIDENCE_MISSING:rcpt:REG:P4:STANDARD", missing=["EVIDENCE_MISSING:rcpt:REG:P4:STANDARD"]),
        [v("PRESERVE", "REG", "BLOCKED", "n/a", None, "prerequisite node absent"),
         v("G-INV", "CL-RET(REG)", "RAN", Q, "FAIL", "RUN_UNREPORTED:<run_id of the removed receipt> (if the inventory still lists the run COMPLETED)")],
        with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "NOT_ELIGIBLE", "BLOCKED", "PRESERVE(REG) absent")}),
        [A_AUTH, "node_id spelling rcpt:<subject>:<predicate id P4>:<world>", "other claims unchanged under the per-claim reading of G-INV (G07)"],
        ["G07"],
        "Plan E02: missing -> BLOCKED, not FAIL. B6.3 first check. The removed receipt's run is still in the "
        "terminal inventory, so G-INV also fires on this claim."),
    row("E02.MALFORMED", "DETERMINED_UNDER_ASSUMPTION",
        v("G-BIND", "CL-RET(REG)", "RAN", Q, "FAIL", "SCOPE_MALFORMED:boundary"),
        [], with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "NOT_ELIGIBLE", "UNMET", "G-BIND FAIL SCOPE_MALFORMED:boundary")}),
        [A_AUTH, "the unbound ERASE receipt does not turn the headline into BLOCKED (G06)"], ["G06"],
        "The receipt parses under the closed schema; 'EPISODE_RESET j=1' is not the registered boundary value, "
        "and the well-formedness check precedes every manifest comparison. Contradicted scope -> FAIL with reason."),
    row("E02.RELABEL", "PARTLY_UNDETERMINED",
        v("G-BIND", "the relabelled CL-RET claim", "RAN", Q, "FAIL", "UNDETERMINED among SCOPE_MISMATCH:physics | IDENTITY_UNKNOWN:<node_id> (G08)"),
        [], [claim("CL-RET(REG2)", "NOT_ELIGIBLE", "UNMET", "G-BIND FAIL against the old complete-node anchors"),
             claim("CL-CAL(STANDARD)", "UNDETERMINED", "UNDETERMINED", "CALIBRATION's subject is WORLD; whether 'every node' includes it is blind")],
        [A_AUTH], ["G08"],
        "Plan E02 / B6.1: complete-node anchors exist so that a whole-graph relabel under old anchors FAILs with "
        "a reason; artifact bytes still match, so BYTES_MISMATCH must NOT be the reason. Which typed code fires "
        "first is the gap."),
    row("E02.WRONG_SUBJECT", "DETERMINED_UNDER_ASSUMPTION",
        v("G-BIND", "CL-RET(REG)", "RAN", Q, "FAIL", "SCOPE_MISMATCH:physics"),
        [], with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "NOT_ELIGIBLE", "UNMET", "G-BIND FAIL SCOPE_MISMATCH:physics")}),
        [A_AUTH, "the claim-cell comparison on the substituted receipt is reached before a DEPENDENCY_MISMATCH on the CLAIM node (node order, G08-like)"], ["G06"],
        "PKTD's RESTART receipt is genuine and bound, but its cell.physics is PKTD while the claim's cell is REG "
        "(B6.3 'scope equals the claim's cell where the policy requires'). CL-RET(PKTD) is untouched."),
    g0("E02.G0"),
    # ---------------- E03
    row("E03.STRIP", "DETERMINED",
        v("G-BIND", "CL-RET(REG)", "RAN", Q, "FAIL", "DEPENDENCY_MISMATCH:<edge RETENTION(REG, STANDARD) -> CALIBRATION(STANDARD)>"),
        [], with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "NOT_ELIGIBLE", "UNMET", "G-BIND FAIL DEPENDENCY_MISMATCH")}),
        [A_AUTH], ["G09"],
        "Deps differ from the manifest node's deps AND omit a required B6.2 edge; the deps check precedes the "
        "bytes check, so the reason is DEPENDENCY_MISMATCH, not BYTES_MISMATCH. The spelling of <edge> is G09."),
    row("E03.BYTEFLIP", "DETERMINED",
        v("G-BIND", "CL-RET(REG)", "RAN", Q, "FAIL", "BYTES_MISMATCH:<role of REG's PROBE_A trace>"),
        [], with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "NOT_ELIGIBLE", "UNMET", "G-BIND FAIL BYTES_MISMATCH")}),
        [A_AUTH], ["G09"],
        "Length equal, sha256 differs from the ArtifactRef. G-BIND hashes bytes; it must not need G-RECOMP to see this."),
    row("E03.REANCHOR", "PARTLY_UNDETERMINED",
        v("G-BIND", "CL-RET(REG)", "RAN", Q, "PASS", "bytes match the producer's re-made anchors"),
        [v("custody", "bundle", "n/a", "n/a", "UNQUALIFIED", "ANCHORS_FROM_PRODUCER"),
         v("G-RECOMP", "CL-RET(REG)", "RAN", Q, "UNDETERMINED", "FAIL OUTCOME_MISMATCH if the flipped byte changes a recomputed outcome and the receipts were not rewritten to match; not stated")],
        [claim("CL-RET(REG)", "UNDETERMINED", "UNDETERMINED", "follows G-RECOMP"),
         claim("CL-CUST(bundle)", "NOT_ELIGIBLE", "UNQUALIFIED", "ANCHORS_FROM_PRODUCER")],
        [A_AUTH, "anchors re-made by the producer are accepted by G-BIND in non-custody mode (G10)"], ["G10", "G11"],
        "Coupling with E05: byte integrity against producer-made anchors establishes nothing; only custody can "
        "tell re-made anchors from the registered ones, and it answers UNQUALIFIED."),
    g0("E03.G0"),
    # ---------------- E04
    row("E04.W_RESTART", "DETERMINED",
        v("RESTART", "REG, PKTD, LAGD", "RAN", "UNQUALIFIED: WITHDRAWN:<withdrawal_id>", "PASS", "WITHDRAWN:<withdrawal_id>"),
        [v("CHANNEL", "REG, PKTD, LAGD", "RAN", "UNQUALIFIED: WITHDRAWN:<withdrawal_id>", "PASS"),
         v("OBSERVER", "every (M, o) in G0", "RAN", "UNQUALIFIED: WITHDRAWN:<withdrawal_id>", "PASS")],
        with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "NOT_ELIGIBLE", "UNQUALIFIED", "WITHDRAWN:<withdrawal_id>"),
                     "CL-RET(PKTD)": claim("CL-RET(PKTD)", "NOT_ELIGIBLE", "UNQUALIFIED", "WITHDRAWN:<withdrawal_id>"),
                     "CL-RET(LAGD)": claim("CL-RET(LAGD)", "NOT_ELIGIBLE", "UNQUALIFIED", "WITHDRAWN:<withdrawal_id>; was UNMET, now worse"),
                     "CL-CAL(STANDARD)": claim("CL-CAL(STANDARD)", "ELIGIBLE", "SATISFIED", "outside the closure; decision record byte-identical")}),
        [A_AUTH, "the stage record is per instrument version, so one withdrawal reaches RESTART on every runtime"], ["G13"],
        "Reverse closure over B6.2: STAGE(P6) <- every RESTART receipt <- CHANNEL and OBSERVER receipts <- every "
        "CL-RET claim. Outcomes are unchanged; authority is lost. The TWIN line is not reached by the letter (G13)."),
    row("E04.W_OBS", "DETERMINED",
        v("OBSERVER", "(REG, BOOKKEEP)", "RAN", "UNQUALIFIED: WITHDRAWN:<withdrawal_id>", "PASS", "WITHDRAWN:<withdrawal_id>"),
        [], with_claims({"CL-RET(REG)": claim("CL-RET(REG)", "NOT_ELIGIBLE", "UNQUALIFIED", "WITHDRAWN:<withdrawal_id>")}),
        [A_AUTH], [],
        "Only CL-RET(REG) descends from that receipt. CL-RET(PKTD), CL-RET(LAGD), CL-CAL keep byte-identical records."),
    row("E04.W_UNRELATED", "DETERMINED",
        v("TWIN_EQ", "(REG, REG-ONEHOT)", "RAN", "UNQUALIFIED: WITHDRAWN:<withdrawal_id>", "PASS", "WITHDRAWN:<withdrawal_id>"),
        [], with_claims({"TWIN(REG, REG-ONEHOT)": claim("TWIN(REG, REG-ONEHOT)", "REPORTED", "UNQUALIFIED", "WITHDRAWN:<withdrawal_id>")}),
        [A_AUTH], [],
        "No B7.1 CL claim is in the closure: CL-CAL, CL-RET(REG), CL-RET(PKTD), CL-RET(LAGD) keep byte-identical "
        "decision records. An unrelated withdrawal revokes nothing else."),
    row("E04.W_UNANCHORED", "DETERMINED",
        v("RESTART", "REG, PKTD, LAGD", "RAN", Q, "PASS", "unverified record <id>: not registered"),
        [], G0_CLAIMS, [A_AUTH], ["G05"],
        "B6.5 / FD-B8: a withdrawal not registered with the keeper revokes nothing; eligibility equals G0 and "
        "the note 'unverified record <id>: not registered' is listed on every claim it would have affected."),
    # ---------------- E05
    row("E05.FAB_ANCHORS", "DETERMINED_UNDER_ASSUMPTION",
        v("custody", "bundle", "n/a", "n/a", "UNQUALIFIED", "ANCHORS_FROM_PRODUCER (and KEEPER_ROW_MISSING if whys are exhaustive, G11)"),
        [v("G-BIND", "per claim", "RAN", Q, "PASS", "internally consistent"), v("G-INV", "per claim", "RAN", Q, "PASS")],
        [claim("CL-CUST(bundle)", "NOT_ELIGIBLE", "UNQUALIFIED", "ANCHORS_FROM_PRODUCER"),
         claim("CL-RET(REG)", "ELIGIBLE", "SATISFIED", "printed with 'Custody: UNQUALIFIED (...)'; never evidence of truthful execution")],
        [A_AUTH], ["G11", "G14"],
        "Plan E05: outside authenticated trust; UNQUALIFIED for a custody claim. Anchors handed over in the "
        "producer bundle never qualify (B5.3)."),
    row("E05.LATE_REG", "DETERMINED",
        v("custody", "bundle", "n/a", "n/a", "UNQUALIFIED", "REGISTERED_AFTER_CHECK"),
        [], [claim("CL-CUST(bundle)", "NOT_ELIGIBLE", "UNQUALIFIED", "REGISTERED_AFTER_CHECK")], [], ["G14", "G15"],
        "Registration must precede the consumer's first check of the bundle (B5.3)."),
    row("E05.KEEPER", "DETERMINED_UNDER_ASSUMPTION",
        v("custody", "G0", "n/a", "n/a", "QUALIFIED", None),
        [v("G-BIND", "CL-CUST(G0)", "RAN", Q, "PASS"), v("G-INV", "CL-CUST(G0)", "RAN", Q, "PASS")],
        [claim("CL-CUST(G0)", "ELIGIBLE", "SATISFIED", "renders 'Custody: QUALIFIED -- bytes registered with <keeper> at <utc>; execution not authenticated.'")],
        [A_AUTH, "the consumer itself fetched the rows from a SET store (or fixture keeper rows exercising the logic only)"], ["G15"],
        "All B5.2 records have rows, blobs match, registration precedes the check. With the store UNSET (R3) the "
        "real-store answer is UNQUALIFIED KEEPER_ROW_MISSING instead."),
    row("E05.FAB_REGISTERED", "DETERMINED_UNDER_ASSUMPTION",
        v("custody", "bundle", "n/a", "n/a", "QUALIFIED", None),
        [v("G-BIND", "per claim", "RAN", Q, "PASS"), v("G-INV", "per claim", "RAN", Q, "PASS"), v("G-RECOMP", "CL-RET(REG)", "RAN", Q, "PASS")],
        [claim("CL-CUST(bundle)", "ELIGIBLE", "SATISFIED", "STATED LIMIT: the fabrication is NOT detected"),
         claim("CL-RET(REG)", "ELIGIBLE", "SATISFIED", "STATED LIMIT: not detected; the render says 'execution not authenticated'")],
        [A_AUTH, "as E05.KEEPER for the store"], ["G15"],
        "B5.4: custody establishes byte identity since registration, never execution or truth. The expected "
        "answer is admission plus the printed limit; an implementation or report that claims detection is wrong."),
]

DOC = {
    "schema": "rso.slice001.expected_answers.v1",
    "packet": "C-004-T005",
    "author": "Pallas[harry1-da86cf98], claude-fable-5-1",
    "contract": {"version": "1.0.0", "contract_json_sha256": "e98bb0c6c45e51bcf876eca84aa8a7fb4a2b1b380f6733b97997779c93279d85",
                 "frozen_commit": "595916f9c"},
    "independence": "Derived before reading draft A A6 'expected'/'outcomes', draft B B9 'expected'/'reason codes', "
                    "B8.2, A8-A10, B11-B13 and any implementation file. See EXPOSURE.md.",
    "conventions": {
        "row_fields": "execution/authority/outcome/reason at row level are those of `primary`, the verdict the case exists to exercise",
        "authority": "QUALIFIED@AUTHOR_TESTED is the expected stage at S2 freeze (B4.3), conditional on G05",
        "determinacy": {
            "DETERMINED": "follows from readable contract text",
            "DETERMINED_UNDER_ASSUMPTION": "the primary outcome follows; a listed assumption carries the rest",
            "PARTLY_UNDETERMINED": "a field is UNDETERMINED; the gap is named",
            "UNDETERMINED": "the primary outcome is not determined"},
        "UNDETERMINED": "never a guess: the contract text available to the independent author does not fix the value",
        "claims": "eligibility per B7.2 (worst standing); REPORTED marks TWIN lines, which are not exit criteria",
    },
    "gaps": GAPS,
    "rows": ROWS,
}

CASE_IDS = ["T01.REG", "T01.PKTD", "T01.QCARRY", "T02.AMNESIAC", "T02.CLOCKED", "T02.FLIP", "T03.REG", "T04.LAGD",
            "T04.REG", "T05.WIPE", "T05.REG", "T06.REG", "T06.PKTD", "T06.PKTD_NOQ", "T06.HCOUNT", "T06.LAGD",
            "T07.HEAL", "T07.BOOKKEEP", "T07.NULL", "T08.EVERY3", "T08.SLEEPER", "T08.SPLIT1", "T08.SPLIT2",
            "T08.REG", "P0.OVERDELAY", "E06.REG_ONEHOT", "E06.REG_FLAT", "E06.LOSSY", "E01.G0", "E01.OUTCOME_EDIT",
            "E01.FAB_CONSISTENT", "E02.MISSING", "E02.MALFORMED", "E02.RELABEL", "E02.WRONG_SUBJECT", "E02.G0",
            "E03.STRIP", "E03.BYTEFLIP", "E03.REANCHOR", "E03.G0", "E04.W_RESTART", "E04.W_OBS", "E04.W_UNRELATED",
            "E04.W_UNANCHORED", "E05.FAB_ANCHORS", "E05.LATE_REG", "E05.KEEPER", "E05.FAB_REGISTERED"]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    ids = [r["id"] for r in ROWS]
    assert len(ids) == 48 and len(set(ids)) == 48, (len(ids), len(set(ids)))
    assert ids == CASE_IDS, [i for i in CASE_IDS if i not in ids]
    with open(os.path.join(here, "..", "contract", "contract.json"), encoding="utf-8") as fh:
        contract_ids = [c["id"] for c in json.load(fh)["cases"]]
    assert contract_ids == ids, set(contract_ids) ^ set(ids)
    used = {g for r in ROWS for g in r["gaps"]}
    assert used <= set(GAPS), used - set(GAPS)
    text = json.dumps(DOC, indent=1, ensure_ascii=True) + "\n"
    with open(os.path.join(here, "EXPECTED_ANSWERS.json"), "w", encoding="ascii", newline="\n") as fh:
        fh.write(text)
    print("rows", len(ids), "gaps", len(GAPS), "bytes", len(text))
