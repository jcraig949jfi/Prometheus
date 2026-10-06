# S1 contract amendment v1.0.5 (B3.3 governs run attribution; POST-OBSERVATION operator amendment, OP6)

Amends contract v1.0.4. Written by Palamedes[harry1-679179c6], 2026-10-06. STATUS: ADOPTED; contract.json is updated by
C-004-T046 (Argus) in the same commit as its repair and the test that pins the contract version.

THIS IS A POST-OBSERVATION AMENDMENT (CONTRACT.md s7: a change to a predicate's meaning after S2 outcomes are
observed goes to the operator). It was made by the operator after the S4 closure observed the STALE_RUN probe
being ADMITTED. The S4 closure result (rso/slice001/challenge/S4/REPORT.md) is NOT rewritten: under contract
v1.0.4 the probe was admitted, it is recorded so, and that record stands as observed.

Authority: C-004-OP6 (operator, 2026-10-06), part 2: "B3.3 governs. A receipt must cite the inventory/run evidence
that actually launched and produced it. An earlier-window run of the same node does not satisfy a later receipt
merely because the ledger is cumulative. Historical rows remain valid provenance, but they cannot substitute for the
execution evidence belonging to the receipt being adjudicated. Therefore the S4 STALE_RUN probe should refuse with
RECEIPT_WITHOUT_RUN, consistent with the F3 attribution repair."

Y1  Reading of B6.4 G-INV under a cumulative ledger: draft B B3.3 governs. A receipt's execution.run_id must name the
    inventory row that launched and produced THAT receipt: a row whose node_id is the receipt's node (V7, already
    enforced since T042) AND which belongs to the launch that produced the receipt (not an earlier window's run of the
    same node). A receipt citing any other row: G-INV FAIL RECEIPT_WITHOUT_RUN:<node_id>.
Y2  Earlier-window rows remain valid provenance in the inventory; they are not errors and are not RUN_UNREPORTED merely
    for being older (their own receipts belong to their own bundles).
Y3  Scope: run attribution only. No other predicate, threshold or case expectation changes.
