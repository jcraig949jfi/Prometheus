# Clymene -- the March 2026 queue, classified

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Base SHA 8714b2709ffa3f1a5d55781d476c3eba4c97a898,
worktree Prometheus-worktrees/clymene-base-role, host M2.

Base role, seat states: "Booting an old seat is an archaeological
event, not an instruction to resume its last queue. Existing backlog is
not permission to resume an obsolete mission." Categories are
STILL_LIVE, NEEDS_REPREMISE, PARKED, SUPERSEDED, TRANSFERRED, RETIRED.
Only STILL_LIVE is executable.

The queue below is reconstructed from what the agent was BUILT to do
(agents/clymene/README.md, configs/manifest.yaml, src/clymene.py and
agents/pronoia/README.md step 5), not from recall. Clymene never kept
a TODO file.

## 1. Classification

    C-A  Clone and keep current the 26 manifest repositories
         (tensor 6, mech-interp 7, evolutionary 4, agents 4,
         datasets 5).
         STATUS THEN: 26 of 26 acquired, refreshed on 4 runs.
         STATUS NOW:  the trees exist on M2 but 0 of 26 contain a .git
                      directory, so "keep current" is not executable
                      against them at all -- there is nothing to pull.
         CLASS: NEEDS_REPREMISE. The premise was "archive before the
         window closes" (availability). The question the program can
         actually use is "can an experiment's external inputs be
         reconstructed" (provenance). Those are different jobs and the
         second one does not start by cloning anything.

    C-B  Download the 20 manifest models under the 28 GB VRAM line,
         chosen for architecture diversity (11 families), to test
         whether signatures are architecture-universal.
         STATUS THEN: 14 of 20; 9 downloaded, 3 already cached, 2
                      failed 403 on a gated repository.
         STATUS NOW:  9 real model trees on M2 plus the 2 stubs. No
                      code resolves them by vault path.
         CLASS: NEEDS_REPREMISE. Whether the program wants a local
         model vault at all is Apollo's and Techne's question, not this
         seat's, and the answer has moved twice since March (see
         project memory on the model/compute shelf). The seat does not
         assume the March answer still holds.

    C-C  Archive the 8 manifest datasets (semantic-scholar-cs-papers,
         openalex-snapshot, pile-uncopyrighted, neuronpedia-sae-
         features, alpaca-eval, openwebmath, IRIS, DeerFlow).
         STATUS THEN: 0 of 8. Declared in the manifest, documented in
                      the README, given a table in the registry, never
                      executed. The registry's datasets table has 0
                      rows and has always had 0 rows.
         STATUS NOW:  unchanged.
         CLASS: PARKED. This is the clearest case of a declared
         capability that was never a capability. It is recorded here
         because a declared-but-never-run stage is exactly the shape
         base rule 8 exists to make visible, and because pile-
         uncopyrighted and openwebmath are large enough that executing
         it later would be a real resource decision, not a chore.

    C-D  Run a full hoard cycle every 72 hours, gated on
         data/last_run.txt, invoked as step 5 of the Pronoia pipeline.
         STATUS THEN: 4 cycles, 2026-03-22 to 2026-03-31.
         STATUS NOW:  the host is gone. pronoia.py is not in the tree
                      at 8714b2709 (agents/pronoia/ holds a README and
                      logs only) and the orchestrator's audit logs stop
                      2026-04-01.
         CLASS: SUPERSEDED. A loop whose only host has been removed is
         not a loop waiting to be restarted; and under base rule 8 a
         loop with no consumer is not a monitor. Registered DORMANT in
         roles/base-role/MONITORS.md with the cause named, not
         relaunched.

    C-E  Emit a dated hoard report for the Hermes digest and the
         operator's email.
         STATUS THEN: 3 reports committed; 42 Hermes digests over 9
                      days.
         STATUS NOW:  Hermes was deliberately deprecated and autopsied
                      (engine/ledger/AGENT_AUTOPSIES.jsonl, Aporia P63,
                      2026-08-21). The autopsy's finding is one level
                      up from Hermes: the alerting function has been
                      rebuilt four times with no durable owner, and
                      Alethelia is the current implementation.
         CLASS: RETIRED. The consumer is gone and its replacement is
         owned by another seat. This seat does not rebuild a reporting
         surface that has already churned four times.

    C-F  Maintain data/vault_registry.db as the catalogue: three
         tables (repos, models, datasets) with commit hashes, sizes,
         VRAM estimates, timestamps and status.
         STATUS THEN: 40 rows written across two tables.
         STATUS NOW:  the rows are intact and are the ONLY surviving
                      record of which upstream commit each vault tree
                      came from -- the trees themselves lost their .git
                      directories. The paths in it are M1 paths and do
                      not resolve on M2.
         CLASS: TRANSFER PROPOSED, not transferred. This is an
         acquisition-provenance ledger, which is Mnemosyne's substrate
         question (durability, provenance integrity, lineage
         preservation), not a hoarding question. Proposing it; not
         moving it, not touching another seat's store. Needs the
         operator or Mnemosyne to accept or decline.

## 2. Counts

    STILL_LIVE         0
    NEEDS_REPREMISE    2   (C-A, C-B)
    PARKED             1   (C-C)
    SUPERSEDED         1   (C-D)
    RETIRED            1   (C-E)
    TRANSFER PROPOSED  1   (C-F)

Nothing is executable today. Three outcomes are legitimate for a
historical seat per the base role (revived as an instrument, probed
then returned to PARKED, or identity re-adjudicated). This seat's own
reading, with its conflict of interest declared in STATUS.md section 4,
is the second: one bounded probe that can return a verdict against the
seat, then PARKED unless it changes a decision.

## 3. What was NOT classified, and why

- The 26 repositories' scientific relevance. Whether TransformerLens,
  qdax or nnsight still matter to the program is not this seat's call
  and was not assessed. Only acquisition state was measured.
- The vault's disposition (keep, prune, move, delete). 51 GB on a
  shared disk is a destructive-action surface and an operator decision.
  This pass wrote and deleted nothing in it.
- Whether the two gated meta-llama models should be re-attempted with a
  credential. That is an acquisition action; the seat has no charter to
  acquire, and the project instruction routes any key through keys.py.

## 4. One methodological note, recorded because it nearly fooled this pass

Checking vault freshness with `git -C vault/repos/<name> log -1` returns
today's date for all 26 trees. It looks like a fresh archive. It is
not: none of those directories is a git repository, so git walks up to
the enclosing Prometheus checkout and reports THAT repository's HEAD.
The label said fresh; the property is that these trees have no upstream
at all. Caught by testing for .git rather than trusting the command's
exit status, which is the base role's capability-over-labels rule in
its smallest possible form. Logged in calibration/LEDGER.md.
