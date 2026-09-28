# Cosmos BOOTSTRAP -- the entry file for a fresh session (read before anything else in roles/Cosmos/)

Currency: 2026-09-28T08:55Z. Operator directive 2026-09-28 (roles/Cosmos/prompts/
2026-09-28_operator_research_structure/DIRECTIVE_VERBATIM.md): Cosmos is the substrate-independent
LAW FOUNDRY. Close C3 first, then the research-thread program (roles/Cosmos/research/README.md).

## 0. Boot (inherited mechanics, pointers only)
Base role s1 (roles/base-role/RESPONSIBILITIES.md): refuse the canonical checkout; work in the M2 worktree
D:/Prometheus-worktrees/cosmos-base-role; `python -m comms boot Cosmos --model <id>` with
EW_DB_HOST=192.168.1.202; `python -m comms sync Cosmos`; then this file, RESPONSIBILITIES.md, STATUS.md.
The worktree is normally on the PUBLIC branch `cosmos/c3-public-2026-09-24`, so the withheld files are
not on disk. `python -m prometheus.cosmos.research_check` must PASS before any research-workspace commit.

## 1. Where things stand (public facts)
- C0 (CWE qualification) CLOSED PERMANENTLY at af2af37f4. Record: roles/Cosmos/campaigns/
  (HANDOFF_2026-09-23.md, REVIEW_PACKET_CWE_2026-09-23.txt). ATLAS-37 adapter landed (7190591f4).
- C3 (causal accessibility of past information) Session 1 COMPLETE. Public: the P1/P2 certificate v3
  (qualified), the D contract, the information ledger. Everything else is WITHHELD (s2).
- Holdout D: SEALED by Nestor on M1 on 2026-09-25 (seal a56ef7787, sha256 ae4479c6...57ac, verified by
  Cosmos from the git blob). Operator 2026-09-28: (D1) the branch + hash is NOT enough, so the seal must
  be merged into main; (D4) the original hidden set is readable in plaintext and is treated as EXPOSED,
  so Nestor builds an OPAQUE SUCCESSOR seal with a fresh hidden set, the key off M2, and an independent
  firewall check. Request: comms #788 (roles/Cosmos/prompts/2026-09-28_operator_research_structure/
  REQUEST_TO_NESTOR_D_SEAL.md).
- Cosmos must NOT read D's source, sealed spec, selftest details or hidden-set artifacts, and must not
  infer D from branch names, file names, commit history or operational traces.
- E reserved for Aether working from M4 only; not commissioned.
- Seat state: BLOCKED on #788. No methodological change to C3 before D (operator 2026-09-25).

## 2. The withheld branch (READ THIS)
The C3 law, coordinates, visible substrates, results, substitution attacks, Session 1 review packet and
two operator notes exist ONLY on the LOCAL branch `cosmos/c3-s1-2026-09-24` in the M2 worktree above.
Its early head 0ecafed1... is hash-committed in roles/Cosmos/c3/INFO_LEDGER.md and in
roles/Cosmos/research/FREEZES.md (F-0000).
- Preserve it EXACTLY (operator 2026-09-28): no new commits on it until the operator triggers C3's next phase.
- NEVER push it or merge it into a pushed branch until ALL of these hold: (a) the original seal
  a56ef7787 is an ancestor of origin/main; (b) the opaque SUCCESSOR seal's commitment is on main (its
  author must finish without the law in view: publishing earlier would contaminate the successor);
  (c) the operator explicitly triggers publication.
- roles/Cosmos/c3/RESUME_WITHHELD.md on that branch describes the OLD sequence. Where it differs from s3
  below, s3 wins.
- Do not paste withheld content into comms, main, or any public file.

## 3. The C3 closing sequence (operator 2026-09-28 s1-s3, s10; supersedes the 2026-09-25 sequence)
1 Nestor merges seal a56ef7787 into main; Cosmos verifies ancestry + hash.
2 Nestor pushes the opaque successor commitment; an independent seat (not Cosmos) checks the firewall.
3 Cosmos REPORTS to the operator: seal on main / successor exists / firewall checked / ready to freeze.
  The operator decides whether to authorize the blind test. Cosmos does nothing further until then.
4 On authorization: freeze predictions, law definitions, thresholds, failure regions, adjudication
  rules and the intervention, using only information Cosmos is allowed to have. Record the manifest +
  hash in research/FREEZES.md.
5 Pre-result adversarial review (research/PRE_RESULT_REVIEW.md). Repairs only on visible material;
  a new freeze supersedes the old one, which is kept.
6 Hand the frozen package across the firewall. An independent seat executes the hidden worlds, Harmonia
  adjudicates, and Cosmos receives the result. Cosmos NEVER runs D. D is then SPENT, and the C3 claim is
  closed either way (no tuning, no revised thresholds, no second attempt, no relabeling).
OPEN for the operator: the 2026-09-25 plan had Harmonia audit the coordinate layer before D. The
2026-09-28 plan has Harmonia adjudicate D. PRE_RESULT_REVIEW.md s1 says an adjudicator should not also
review, so does the coordinate audit move to another seat, or is it dropped?

## 4. After C3
The research-thread program: roles/Cosmos/research/ (README, THREADS, RESULTS, GRAVEYARD, FREEZES,
PRE_RESULT_REVIEW). Design work that uses only public material may proceed now. No thread runs an
experiment before T-C3 closes.

## 5. Where to check for news
`python -m comms sync Cosmos` (Nestor's reply to #788); roles/Nestor/ on origin/main. The hourly watch is
STOPPED (operator 2026-09-28).
