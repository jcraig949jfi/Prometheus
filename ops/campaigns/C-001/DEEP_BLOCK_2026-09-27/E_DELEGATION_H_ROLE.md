# Block E (delegation log) and Block H (role learning) -- Archaeon, 2026-09-27

## E. Delegated work

| worker | host | isolation | model | task | wall | result | relay |
|---|---|---|---|---|---|---|---|
| W1-npe-lens | ubu001 | isolated CLAUDE_CONFIG_DIR (empty; no node memory) | claude-sonnet-5 (default of the empty config) | reconstruct NPE as a lens + audit Archaeon's NPE claims | 11 min | 743-line reconstruction; found my withdrawn NPE host-conditioned claim and two overstatements | bundle -> worker/W1-npe-lens (eff8341bb) -> merged unedited |
| W2-bee-lens | ubu002 | isolated | claude-sonnet-5 | reconstruct BEE + audit Archaeon's BEE claims | 12.5 min | reconstruction; flagged M2-only evidence, a "native" mislabel and lens-invented classes | bundle -> worker/W2-bee-lens (7288ba4f2) |
| W3-ruler-saturation | ubu001 (concurrent with W1) | isolated | claude-sonnet-5 | B7 corpus scan, bounded to 4 cases | 8.5 min | 4 cases, counts, guard quotes | bundle -> worker/W3-ruler-saturation (cb3828f52) |
| block-13 probe | ubu001 | none needed (a script, not an agent) | -- | TH-007 / TH-009 measurement (one deterministic replay) | see probe row | see REPORT | output copied to M2 evidence |

What was learned about portable research execution:
- **Isolation works cheaply.** An empty CLAUDE_CONFIG_DIR plus the node's token env gives a context-free worker: the memory path moved
  into the empty dir, and no "Artemis" identity appeared.
  * Side effect: the model silently changed to the empty config's default (Sonnet 5 instead of the node's Opus 5.5). Isolation removes
    settings as well as memory, so the model must be pinned deliberately.
- **Independence paid off.** Asked for "the engine's own record first, then audit Archaeon's reports", both engine workers found real
  errors in MY claims (the NPE denominator; BEE provenance labels). A worker briefed with my conclusions would likely not have. The
  audit leg is the most valuable part of a delegation.
- **Environment:** no packages were installed by the deep-block workers (apt history checked on both nodes). ubu002 still carries E-002's
  numpy/torch.
- **Concurrency:** two agent workers plus later a replay on a 4-thread / 7 GB node worked. The git worktree ops on a shared clone were
  staggered to avoid lock collisions.
- **Relay:** git bundle -> M2 fetch -> push. It is unedited and cheap, but it is still M2's job (no node push).

## H. What this block suggests about Archaeon's function (not a charter change)
- **Required Archaeon's synthesis:**
  * the three-axis reduction (Block B);
  * the cross-engine claims only three lenses license (Block D s3);
  * the attack on C-OP' and the category error in clause (b);
  * deciding which worker critiques were right (the NPE denominator: yes; "4 P-11 tests": yes; some BEE numbers "unverifiable":
    true but not wrong).
  Integration across engines and against prior art is the part no single-engine seat or worker produced.
- **Better delegated:**
  * per-engine reconstruction;
  * corpus scans;
  * replays.
  The workers were faster, and they were more critical of me than I was.
- **Should become reusable instrumentation:**
  * the observation-only VM transforms (BEE code-material probe, NPE z8taint probe);
  * the C-OP' edge-case battery;
  * the "native vs lens" audit prompt pattern;
  * the IBD / IBS / dependence coordinates for every native field.
- **Merely execution:** the T-001-style replays, bundle relays, and test runs.
- **Where cross-engine mining created value:** the harness-copy hazard (TH-008) and the cargo / machinery asymmetry (TH-007) are
  invisible inside one engine, where each looks like a local bug or a local result.
- **A caution about Archaeon itself:** the lens accumulated three over-claims (NPE host-conditioning, "repaired", "4 P-11 tests") that
  only an independent audit caught. Archaeon's synthesis role needs an adversarial worker attached by default, not optionally.
