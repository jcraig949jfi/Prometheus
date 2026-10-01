# U-02 method (frozen before the evidence reading) -- Artemis, 2026-09-30

Assignment: Aporia #1149 (CWO-2026-09-30C s7), unowned item U-02. Read-only on others' data. Nothing is re-run,
no bar is changed, no seeds are added. Base: origin/main at the freeze commit of this file.

Already known before this freeze (so it is not a blind check): D002-07 printed a top-tercile load-bearing rate
of 0.0997 against the D001-07 worker's bar of 0.10, and IQ-NULL deltas of 0.0, ADVANCE, "partition-like keys: NONE".

## Q1 -- is the IQ-NULL partition key recoverable from committed material?
1. From aporia/iq/FINDINGS_SCHEMA_FIX_2026-08-26.md and the gate code it names: the exact required field (name,
   type, semantics), where it had to be written (which file or record, and which writer), and the rule that makes
   its absence INADMISSIBLE.
2. Search the committed IQ-NULL material (prereg, RESULT_IQ_NULL.json, run/driver code, ledgers, commits touching
   aporia/iq around 2026-08-25) for that field, or for information from which it follows deterministically.
3. Decision:
   - RECOVERABLE only if the value follows mechanically from artifacts written at run time or frozen before the run
     (prereg, config, code at the run commit), with no judgement added now. Then re-derive it, show the derivation,
     and state which gate status the result would then take under the gate's own code/rule.
   - Otherwise INADMISSIBLE, naming the exact missing field and where it would have had to be written.
   - If the gate's rule is itself ambiguous about what satisfies it: UNDETERMINED, quoting the ambiguity.
     I do not resolve it by choosing.

## Q2 -- the 0.0997 vs 0.10 bar
1. Exact counts: re-count from the committed forge/verdicts/*_verdict.json (read-only, in my own code), following
   the D001-07 script's definitions (overall_score terciles, |delta| >= 0.20 = load-bearing, ablations with a
   delta). Report the numerator/denominator, and whether they match D002-07.
2. The rule as frozen: quote it verbatim with its source and hash (D001-07 analysis.py, Fabric artifact sha256
   d793080d...), and the D001-07 REPORT text around it.
3. Was the bar frozen before the number was seen? Establish (a) who authored the 0.10 bar, and when; (b) whether
   any committed document stated a top-tercile load-bearing rate, or the counts that give it, before the bar was
   written (search Lexis / forge / aporia material for the tercile split); (c) whether the D001-07 worker could have
   computed it by hand from what it read.
   Answer YES / NO / UNDETERMINED with the evidence.
4. Also report, without re-scoring: how sensitive "0.0997 < 0.10" is to definitional choices the script made
   (tercile boundary ties, the 3 ablation errors). This is reported as fragility, not as a new verdict.

## Output
roles/Artemis/u02/RESULT.md: what the artifacts say, what my counting produced, what I infer, kept separate.
Completion message to Aporia (CWO-C s24), then READY.
