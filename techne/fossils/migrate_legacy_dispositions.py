"""Evidence audit + migration of the 15 legacy tag-based dispositions (batch 10 P3).

Charter: "Do not grandfather them... The objective is not to preserve the loser count. The
objective is to discover how much of the old loser count survives evidentiary scrutiny."

Each legacy claim below was read from the record's own lineage text, then judged against evidence
I can actually cite. Four outcomes are possible and all four occur:

  CONFIRMED     the legacy tag was a loser claim and the evidence supports a non-ACTIVE state
  RECLASSIFIED  the evidence supports a DIFFERENT non-ACTIVE state than the tag implied
  NOT_A_LOSER   the tag was never a disposition claim (successor / predecessor / redesign) or the
                software is current; state becomes ACTIVE and it LEAVES the loser count
  UNKNOWN       the historical record does not settle it; the citations are kept, the claim is not

    python -m techne.fossils.migrate_legacy_dispositions [--apply]
"""
from __future__ import annotations

import argparse
import json
import time

from . import record, vault


def ev(kind, ref, says):
    return {"kind": kind, "ref": ref, "says": says}


# --------------------------------------------------------------------------------------------
# The audit. "verdict" is the audit outcome; "state" is what the record will carry afterwards.
AUDIT = {
 # ---- CONFIRMED: the tag claimed a loss and the evidence supports one ------------------------
 "bsd-tcp-4.2-1983": {
   "legacy_tags": ["known_bad", "failed_branch"], "verdict": "CONFIRMED",
   "state": "FAILED", "failure_reasons": ["incorrect_assumptions", "performance_collapse"],
   "superseded_by": "bsd-tcp-4.3-tahoe-1988",
   "evidence": [ev("original_paper", "Jacobson & Karels, Congestion Avoidance and Control, SIGCOMM 1988",
                   "In October 1986 the LBL-to-Berkeley path collapsed from 32 kbit/s to 40 bit/s; the paper "
                   "attributes this to TCP lacking congestion control and introduces slow start and congestion "
                   "avoidance as the fix.")],
   "note": "This design failed in production on the real Internet, not merely in comparison."},

 "zchaff-2007": {
   "legacy_tags": ["failed_branch", "loser"], "verdict": "CONFIRMED",
   "state": "LOSING_RIVAL", "failure_reasons": ["superior_rival"],
   "superseded_by": "minisat-2.2.0", "rival_of": "minisat-2.2.0",
   "evidence": [ev("original_paper", "Moskewicz, Madigan, Zhao, Zhang, Malik, Chaff: Engineering an Efficient SAT Solver, DAC 2001",
                   "Chaff introduced VSIDS and two-literal watching, the techniques later CDCL solvers adopted."),
                ev("original_paper", "Een & Sorensson, An Extensible SAT-solver, SAT 2003",
                   "MiniSat reimplements the same CDCL techniques in a far smaller core, and became the solver "
                   "subsequent work built on."),
                ev("benchmark_history", "SAT Competition results (zChaff 2002; MiniSat placements from 2005)",
                   "zChaff won the 2002 competition; MiniSat and its descendants displaced it in later years.")],
   "note": "Historically pivotal AND displaced -- the ideas won while the implementation lost."},

 "bsd-4.3-distribution-tape-1986": {
   "legacy_tags": ["known_bad_lineage"], "verdict": "CONFIRMED",
   "state": "SUPERSEDED", "failure_reasons": ["incorrect_assumptions"],
   "superseded_by": "bsd-4.3-reno-distribution-tape-1990",
   "evidence": [ev("original_paper", "Jacobson & Karels, Congestion Avoidance and Control, SIGCOMM 1988",
                   "The congestion-control algorithms absent from 4.3BSD were added in 4.3BSD-Tahoe, making the "
                   "plain 4.3BSD TCP the pre-fix design."),
                ev("standards_history", "4.3BSD -> 4.3BSD-Tahoe -> 4.3BSD-Reno -> 4.4BSD release lineage",
                   "Each BSD release supersedes the previous distribution.")],
   "note": "Superseded as a DISTRIBUTION; its TCP is the before-point of the congestion lineage."},

 "compact-4.2bsd-1983": {
   "legacy_tags": ["failed_branch", "loser"], "verdict": "CONFIRMED",
   "state": "SUPERSEDED", "failure_reasons": ["superior_rival"],
   "superseded_by": "compress (LZW), later gzip-1.2.4-1993",
   "evidence": [ev("original_paper", "Welch, A Technique for High-Performance Data Compression, IEEE Computer 1984",
                   "LZW is presented as a fast, high-ratio compression technique; compress implemented it and "
                   "became the standard Unix compressor, displacing the adaptive-Huffman compact."),
                ev("project_documentation", "4.xBSD distribution contents (compact in ucb/, later absent)",
                   "compact shipped in 4.xBSD and did not survive into later standard Unix toolsets.")],
   "note": "Beaten on both speed and ratio; the rival that beat it was itself later displaced by gzip "
           "under patent pressure, which is a separate disposition."},

 "minisat-1.14-2006": {
   "legacy_tags": ["predecessor"], "verdict": "CONFIRMED",
   "state": "SUPERSEDED", "failure_reasons": [],
   "superseded_by": "minisat-2.2.0",
   "evidence": [ev("original_paper", "Een & Sorensson, An Extensible SAT-solver, SAT 2003",
                   "Describes the MiniSat core that 1.14 represents."),
                ev("release_notes", "MiniSat 2.0/2.2 release history",
                   "The 2.x line rewrote the solver (SimpSolver, new restart and clause-reduction policies) and "
                   "replaced the 1.x line.")],
   "note": "Superseded by its OWN successor version, not out-competed by a rival. No failure reason "
           "applies; recording one would overstate the evidence."},

 # ---- RECLASSIFIED: evidence supports a different non-ACTIVE state than the tag implied -------
 "bsd-tcp-4.3-tahoe-1988": {
   "legacy_tags": ["historical_redesign"], "verdict": "RECLASSIFIED",
   "state": "SUPERSEDED", "failure_reasons": ["superior_rival"],
   "superseded_by": "bsd-tcp-4.3-reno-1990",
   "evidence": [ev("original_paper", "Fall & Floyd, Simulation-based Comparisons of Tahoe, Reno and SACK TCP, CCR 1996",
                   "Compares the variants directly; Tahoe collapses its window to one segment on loss, which "
                   "Reno's fast recovery avoids.")],
   "note": "The tag said 'redesign', which is not a disposition. The redesign WAS the fix for 4.2 -- and was "
           "itself then superseded by Reno."},

 "bsd-tcp-4.3-reno-1990": {
   "legacy_tags": ["successor"], "verdict": "RECLASSIFIED",
   "state": "SUPERSEDED", "failure_reasons": ["incorrect_assumptions"],
   "superseded_by": "NewReno (RFC 3782) / SACK (RFC 2018)",
   "evidence": [ev("original_paper", "Fall & Floyd, Simulation-based Comparisons of Tahoe, Reno and SACK TCP, CCR 1996",
                   "Reno performs poorly when multiple segments are lost from one window."),
                ev("standards_history", "RFC 2018 (TCP Selective Acknowledgment) and RFC 3782 (NewReno)",
                   "Both were standardised specifically to address Reno's behaviour under multiple losses.")],
   "note": "Tagged 'successor' because it succeeded Tahoe -- but being a successor is not a disposition, and "
           "Reno was in turn superseded."},

 "bsd-4.3-reno-distribution-tape-1990": {
   "legacy_tags": ["successor"], "verdict": "RECLASSIFIED",
   "state": "SUPERSEDED", "failure_reasons": [],
   "superseded_by": "4.4BSD",
   "evidence": [ev("standards_history", "4.3BSD-Reno -> 4.4BSD / 4.4BSD-Lite release lineage",
                   "4.4BSD superseded 4.3BSD-Reno as the Berkeley distribution.")],
   "note": "Tagged 'successor'; as a DISTRIBUTION it was itself superseded."},

 "spin-pathfinder-priority-inversion-1997": {
   "legacy_tags": ["pathology"], "verdict": "RECLASSIFIED",
   "state": "FAILED", "failure_reasons": ["concurrency_failure"],
   "superseded_by": "the same system with priority inheritance enabled",
   "evidence": [ev("retrospective", "Glenn E. Reeves (JPL), What Really Happened on Mars Rover Pathfinder, 1997",
                   "Repeated spacecraft resets were caused by priority inversion: a low-priority task held a mutex "
                   "needed by a high-priority task while a medium-priority task ran; the fix was to enable priority "
                   "inheritance on that mutex.")],
   "note": "The FAILED subject is the deployed configuration the model encodes, not the SPIN model itself. "
           "This is a real failure that happened on another planet and was diagnosed and patched in flight."},

 # ---- NOT_A_LOSER: the tag was never a disposition claim, or the software is current ----------
 "glibc-rwlock-writer-starvation-2.36": {
   "legacy_tags": ["documented_pathology"], "verdict": "NOT_A_LOSER",
   "state": "ACTIVE", "failure_reasons": [], "superseded_by": "",
   "evidence": [ev("project_documentation", "pthread_rwlockattr_setkind_np(3)",
                   "PTHREAD_RWLOCK_PREFER_READER_NP 'may result in writer starvation'. This documents a BEHAVIOUR "
                   "of a currently shipped design, not its defeat.")],
   "note": "glibc still ships this. A documented failure MODE is not a historical disposition. The starvation is "
           "already captured behaviourally in the fossil's receipt (1 writer acquisition vs 4,950,536). "
           "LEAVES the loser count."},

 "gzip-1.2.4-1993": {
   "legacy_tags": ["historical_redesign"], "verdict": "NOT_A_LOSER",
   "state": "ACTIVE", "failure_reasons": [], "superseded_by": "",
   "evidence": [ev("standards_history", "RFC 1951 (DEFLATE)",
                   "gzip's DEFLATE was standardised and remains in ubiquitous use.")],
   "note": "gzip is the WINNER of the compression displacement, not a loser. The patent pressure that drove the "
           "redesign is a disposition of compress/LZW, not of gzip. LEAVES the loser count."},

 "libcorrect-quiet": {
   "legacy_tags": ["successor"], "verdict": "NOT_A_LOSER",
   "state": "ACTIVE", "failure_reasons": [], "superseded_by": "", "rival_of": "libfec-karn",
   "evidence": [],
   "note": "Tagged 'successor' -- a relationship, not a disposition. Current software. LEAVES the loser count."},

 "odepack-netlib": {
   "legacy_tags": ["pathology"], "verdict": "NOT_A_LOSER",
   "state": "ACTIVE", "failure_reasons": [], "superseded_by": "",
   "evidence": [],
   "note": "The 'pathology' is stiffness -- a property of the PROBLEM that makes a non-stiff method exhaust its "
           "step budget. That is mathematics behaving correctly, not software that failed. ODEPACK remains in use "
           "(scipy's LSODA wraps it). LEAVES the loser count."},

 # ---- UNKNOWN: the historical record does not settle it ---------------------------------------
 "redlock-py-redis-2014": {
   "legacy_tags": ["contested_design"], "verdict": "UNKNOWN",
   "state": "UNKNOWN", "failure_reasons": [], "superseded_by": "",
   "evidence": [ev("archived_technical_discussion", "Kleppmann, How to do distributed locking (2016)",
                   "Argues Redlock is unsafe for correctness-critical locking because it depends on bounded clock "
                   "drift and pause times."),
                ev("archived_technical_discussion", "antirez, Is Redlock safe? (2016 response)",
                   "Disputes that analysis and defends the algorithm's assumptions.")],
   "note": "Genuinely CONTESTED and never settled by the historical record. Both citations are kept; neither "
           "establishes a disposition. Declaring a winner here would be my judgement, not evidence."},

 "tinystm-marlier": {
   "legacy_tags": ["superseded_design"], "verdict": "UNKNOWN",
   "state": "UNKNOWN", "failure_reasons": [], "superseded_by": "",
   "evidence": [ev("retrospective", "Cascaval et al., Software Transactional Memory: Why Is It Only a Research Toy?, CACM 2008",
                   "Documents large STM runtime overheads and argues the approach had not become practical. This "
                   "supports a documented CRITIQUE; it does not establish that TinySTM was superseded.")],
   "note": "The tag claimed supersession. I cannot cite a source establishing that STM lost to a named rival, so "
           "the claim is DEMOTED rather than migrated. The critique is preserved as evidence of the argument, not "
           "of an outcome."},
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    rows, counts = [], {}
    for sid, au in sorted(AUDIT.items()):
        rec = record.load(sid)
        before = (rec.get("historical_disposition") or {}).get("state", "UNKNOWN")
        hd = {"state": au["state"], "failure_reasons": au.get("failure_reasons", []),
              "superseded_by": au.get("superseded_by", ""), "rival_of": au.get("rival_of", ""),
              "evidence": au.get("evidence", []), "audit_note": au["note"],
              "legacy_tags": au["legacy_tags"], "audit_verdict": au["verdict"],
              "audited_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        rec["historical_disposition"] = hd
        probs = record.validate(rec)
        if a.apply and not probs:
            record.save(rec)
        counts[au["verdict"]] = counts.get(au["verdict"], 0) + 1
        rows.append({"specimen_id": sid, "legacy_tags": au["legacy_tags"], "verdict": au["verdict"],
                     "state_before": before, "state_after": au["state"],
                     "n_evidence": len(au.get("evidence", [])), "validate_problems": probs})
        print("%-40s %-13s %-8s -> %-26s ev=%d %s" % (
            sid, au["verdict"], before, au["state"], len(au.get("evidence", [])),
            "" if not probs else probs))

    doc = {"schema": "techne.fossil.disposition_audit/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "applied": bool(a.apply), "legacy_claims_entered": len(AUDIT), "by_verdict": counts,
           "rule": "A non-ACTIVE state requires at least one citation (record.validate enforces it). "
                   "A tag that merely names a relationship (successor, predecessor, redesign) is not a "
                   "disposition. A documented failure MODE of current software is not a disposition.",
           "rows": rows}
    if a.out:
        __import__("pathlib").Path(a.out).write_text(json.dumps(doc, indent=1) + "\n",
                                                     encoding="utf-8", newline="\n")
    print("\nby verdict:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
