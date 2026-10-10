# Retrieval verdicts and the decision to stop tuning (PAN-05, PAN-31)

Currency: 2026-10-09T13:40Z (date -u at commit time). Every row of every run is in
roles/Pan/reports/controls/; prereg commits are named below. Thresholds were
never moved.

## The runs

    run (set, n)              config                            hybrid R@10  R@1    verdict / note
    v0   (dev1, 22)           fts AND + bge-small, RRF          0.68         0.32   FAIL (bar 0.80)   1f005e0b1 prereg
    v1   (held-out H1, 20)    fts OR+coverage + bge-small,      0.75         0.45   FAIL              83781786a prereg
                              RRF + bge-reranker-v2-m3
    v2   (held-out H2, 20)    v1 + Qwen3 document vectors       0.75         0.40   FAIL; paired with
                                                                                    v1: 15 both, 0/0  6a702300e prereg
    v2.1 (CB-200, 200)        v1 with rarest-12 lexeme cap      0.765        0.465  no bar (measures);
         queries = other      v2 with the same cap              0.765        0.460  paired 152 both,
         seats' commit                                                              1 / 1, p = 1.0
         subjects
    Components on CB-200: full-text alone 0.69, chunk vectors alone 0.745,
    document vectors alone 0.48 (commit subjects describe changes, not documents).
    95 percent interval on 0.765 (n=200, Wilson): about [0.70, 0.82].

## Readings

1. The fixes that moved recall were full-text ones: AND -> OR + coverage took
   lexical recall from 0.58 to 0.92 (dev). Rerankers helped little; a deeper
   rerank pool hurt; document vectors from a stronger model helped neither H2
   nor CB-200.
2. On 200 queries Pan did not write, the shipped hybrid finds a file the
   change touched in the top 10 for 3 queries in 4, and at rank 1 for nearly
   1 in 2. The 0.80 bar lies inside the interval: neither met nor clearly missed.
3. The n=20 held-out sets could not separate 0.75 from 0.80 (SE about 0.10).
   Base doctrine: a gate closer to the observed value than its own standard
   error is not a gate. Future preregs use n >= 100.

## Decision (Pan's own stop rule, review packet unit 1, section 9)

STOP tuning retrieval. Ship v1 (with the lexeme cap) as the default:
`python -m pan search` = OR+coverage full-text + bge-small chunk vectors +
reciprocal-rank fusion, reranked with bge-reranker-v2-m3 when a CUDA GPU is
present (PAN_RERANK=none turns it off). Document vectors stay for the
file-to-paper pivot (`pan frontier like`), where they are the only route.
Effort moves to consolidation, intake and the local-model tests.

What would reopen it: queries asked by seats in comms that the index fails
on, collected as a fresh n >= 100 set; or pgvector (Q-001), which changes the
vector side's latency and reach, not its ranking.
