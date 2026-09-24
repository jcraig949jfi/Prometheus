"""Cycle-8 reconciler notes, part A: P-J01 (successor worlds), P-J02 (mutational distance), P-J05 (genealogy),
P-J07 (invasion), P-J04 (forensics), P-J08 (grammar B), P-J09 (geometry), fillers P-D08 / P-A02 / P-C05; defect D091."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

LEDGER = HERE.parent / "DEFECTS.jsonl"
D091 = {"id": "CW01-D091", "experiment_id": "cw01-loop8", "phase": "EXECUTE", "severity": "low", "category": "driver", "status": "FIXED",
        "defect_class": "B - a guard that cannot fire (material flag read from a key the statistic never writes)",
        "title": "P-C05's material rule ('the paired band excludes 0') was computed from sf['band'] / sf['ci'], keys paired_signflip never returns; the flag was always False and run 1 recorded a 0.26 paired difference above the p95 of .09 as not material.",
        "evidence": "P-C05 RESULT_prev1.json material False with above_p95 True.", "proposed_fix": "APPLIED: material = above_p95 or below_p05; rerun (RESULT.json material True); the run-1 evidence line is superseded.", "found_by": "reconciler read"}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    if D091["id"] not in existing:
        rec = {"id": D091["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
        rec.update({k: v for k, v in D091.items() if k != "id"})
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)

    L.append_evidence("T-X21", "P-J01", "RECONCILER: the SUCCESSOR WORLDS are not crossed either. A' (regime 1 expects v XOR 1, one bit from identity) top-4 held-out .48-.52 (threshold .90), B' .44-.52 (.80), C' .50 (.80, at the cue-follow floor); destroyed-cue controls indistinguishable; crossing generation None in 9/9 runs; the best-by-training individual's held-out is flat at .52 from generation 0 to 119 (P-J05). Read separately: A' - no immediate conditional computation leaves the identity plateau even when the transform is one bit; B' - no persistent state is recruited for the gone cue; C' - nothing exceeds cue-following. The one-bit successor removed the 'complement is far' explanation: the obstruction is not the size of the transform.", True,
                      state="ACTIVE", state_reason="the obstruction is now located structurally (P-J02): answer-before-read; continuation = a successor world that FORCES the ask tick to be read before the answer")
    L.append_evidence("T-R01", "P-J02", "RECONCILER: ACTUAL MUTATIONAL DISTANCE, measured. (0) STRUCTURE: on 5 of 6 plateau genomes the answering OUT fires with all 3 words of the ask tick still unread (2 on the sixth); no register holds the regime word at that moment (literal or cross-set lookup): the organism answers from persisted state BEFORE reading the ask tick, so no edit of the answer's computation can make it conditional - the read must be added first. (1) WITNESSES (instruments): XOR-1 needs 4 inserted instructions (IN, IN, IN, XOR; 3 on one genome), XOR-15 needs 12 (a PUT-neutral read-and-transform block); two genomes (seed 2, ask-time shaped) admit no template witness at all. (2) INTERMEDIATES: every prefix of the XOR-1 witness scores 0.0 (the partial read consumes the words the plateau needs) and the gain appears only at the fourth instruction; the XOR-15 path is .03 for 8 prefixes then .56, .56, .56, 1.0: DELETERIOUS VALLEYS with all instructions individually necessary (4/4, 12/12). (3) EXHAUSTIVE ONE-EDIT CENSUS: 12880 structured insertions / replacements per genome (8 ops x every position x every register): 0 hits, 0 beneficial (4-set confirmed), 88-93 percent neutral, the rest deleterious, identical on xor 1 and xor 15. (4) GRAMMAR SAMPLES: 2000 one-operator mutants per genome: hit 0, beneficial 0, neutral .876, deleterious .124; 2000 two-operator: hit 0, beneficial 0, neutral .77; best mutant on 2 sets .604 = the plateau's own 2-set score. (5) the grammar's exact per-birth probability of a one-edit hit is 0 (there are none); expected hits per P-J01 run 0. ROUTE: NO_ONE_OR_TWO_EDIT_HIT on both worlds; the nearest conditional program is 4 edits away through a valley of fitness 0. The identity plateau is a fitness plateau with a moat: every step toward reading the cue destroys the identity answer before the conditional answer exists.", True,
                      state="ACTIVE", state_reason="distance measured: 4 (xor 1) / 12 (xor 15) instructions through a valley; continuation: worlds where the first step (reading the ask tick) is itself rewarded")
    L.append_evidence("T-X21", "P-J07", "RECONCILER: SELECTION DYNAMICS ARE NOT THE OBSTRUCTION. One verified XOR-1 witness (held 1.0) among 95 plateau individuals in A' FIXES in 10 of 12 runs (generation 7-9 under the P-J01 regime, 7-8 with 64 asks, 11-13 under tournament 2) and is lost in 2 (its first mutated offspring miss, generation 1 and 3: every birth is a mutation); the witness lineage's mean fitness stays .81-.92 under mutational load and the crossed populations hold top-4 held-out 1.0. With the one-bit successor unreachable in 9/9 plain runs and a single copy fixing in 10/12, P-J01's failure is an ENCODING-DISTANCE failure (P-J02), not a search-dynamics failure; no population or episode dose is warranted.", True)
    L.append_evidence("T-X21", "P-J05", "RECONCILER: genealogy of the 9 plain runs: no crossing, route NOT_APPLICABLE. The final best's lineage changes at every generation (every birth is a mutation; 'copy' never occurs), held-out along the lineage is .52 from generation 0 (the identity plateau is the INITIAL condition of the walker population, not an evolved state), and the final populations coalesce to one ancestor by generation 0-62 in 6/9 runs (3 keep several ancestors): 120 generations of neutral drift on a plateau. The genealogy store (every generation, pid / op / fitness, gzip) is the instrument the crossing genealogy will use.", False)
    L.append_evidence("T-X21", "P-J04", "RECONCILER: forensics after crossing NOT_APPLICABLE for A' / B' / C'. The A' instruments were validated on 4 witnesses: cue causality (the ask tick's regime word overwritten) moves the answer in 100 percent of asks; knocking out the witness's XOR drops reward to 0-.125; the register-override instrument acts at the tick boundary only and cannot lesion a register written inside the ask tick (its reach is recorded); overwriting the value register before the ask changes 88-100 percent of answers (it holds v, the persisted answer).", False)
    L.append_evidence("T-ARCH5", "P-J08", "RECONCILER: grammar B and grammar v0.4 have the SAME one-operator neighbourhood of the identity plateau (6 genomes x 2000 each, same-slice baseline, 4-set confirmation): hit 0 / 0, beneficial 0 / 0, neutral .881 / .872, deleterious .119 / .128, best mutant .604 / .604. Representation is not an accessibility coordinate for this plateau: the moat (P-J02) is in the program's topology, not in the operator set.", False,
                      state="TEMPORAL_STASIS(scope: representation as an accessibility coordinate of the identity plateau)", state_reason="two grammars, identical neighbourhoods; reactivates when a world rewards the first step of the read")
    L.append_evidence("T-X20", "P-J09", "RECONCILER: the XOR-1 and XOR-15 witnesses keep their parents' temporal geometry exactly (immune -> immune on 4 genomes; the 2 ask-time parents admit no witness); no crossed organism exists. Context computation, when inserted, does not move a program on the temporal manifold: the two coordinates are independent in this substrate.", False)
    L.append_evidence("T-X05", "P-D08", "RECONCILER: e08 fossil ablation (256 representatives): re-drawing the rank profile at the same total bond width WITH the cores re-drawn destroys capability in every arm (held64 155-171 -> 78-91, all below the competence floor 166.5; retained excess 0), scrambling the read mask at the same bit count retains a fraction (-> 118-127; retained excess .04-.15, corr .27), both worst. The candidate's (i) arm confounds the profile with the cores (as preregistered), so it cannot separate WHICH bonds from HOW MANY; the mask result says the read set matters partly. Not material; P-A02 (independent draw) agrees (ranks 72-91, masks 118-128).", False,
                      state="TEMPORAL_STASIS(scope: fossil ablations that re-draw the cores)", state_reason="the axis needs a profile-preserving core transplant; the descriptive e08 anomaly stands")
    L.append_evidence("T-ARCH4/M1", "P-C05", "RECONCILER: single-word edits on 47 viable parents (8 draws per family): OPCODE-word edits lose function in .47 of draws vs .20 for OPERAND-word edits (paired difference .26, sign-flip band [-.09, .09]: outside), displacement .42 vs .16, held-out change -.21 vs -.09; the ordering holds in every stratum (shelf .37/.14, W0 solvers .52/.16, delay-general .47/.23; gen-0 random 1.0/1.0). The damage cliff is 2.3x an opcode phenomenon per word, consistent with the operand-slot ordering promoted in cycle 7 (P-H06): the word kind is a locality coordinate. (Run 1's material flag was a guard that could not fire, D091; rerun.)", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes A appended")


if __name__ == "__main__":
    main()
