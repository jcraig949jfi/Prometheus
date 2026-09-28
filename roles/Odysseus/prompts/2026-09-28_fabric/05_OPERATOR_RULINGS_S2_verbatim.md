# Operator rulings after S2 (verbatim, 2026-09-28, received ~21:20Z)

This is the first result that makes me comfortable saying the old coordination model should now be considered legacy.

The S2 result is not a fair performance benchmark against Artemis—the tasks differ too much—but it is a strong architectural result. The fabric took over dispatch, completion detection, isolation, artifact capture, routing, and concurrency, leaving Odysseus mostly with actual epistemic decisions. That is exactly the separation we wanted.

The observed coordination burden went from 3.5 principal actions/run in the Artemis control to 0.28/run in S2. I would record that as a large measured reduction under a lighter workload, not yet a general 12× improvement claim.

Immediate rulings

D12 blocks the next adoption experiment. Fix Git read access first. Don’t broaden workers back to arbitrary shell. Replace brittle command-string matching with a small read-only Git executor that parses argv and explicitly permits the operations researchers actually need: status, rev-parse, log, show, diff, grep, ls-tree, cat-file, for-each-ref, branch --contains, etc. It should handle git -C <worktree> ..., constrain paths to the assigned worktree, disable hooks/external diff machinery, and reject mutating/subprocess-capable operations. Give it adversarial tests. This is an instrument repair, not a new platform feature.

Let the old ubu002 pilot worker expire. It behaved correctly and actually strengthened P2/S2, but it predates the cleaned-up persistent-runtime arrangement. Don’t spend coordination effort trying to kill it remotely. Once it idle-exits, any future ubu002 worker should be launched from a pinned Fabric runtime as worker.ubu002..., independent of Artemis.

D2 remains FAIL. No further operator action. Nestor owns the repair and should submit the v2 re-audit through audit.security.adversarial --replicas 2. Odysseus should not chase Nestor or manually create the job for him. When artifacts arrive, Odysseus can perform the explicitly retained auditor-of-record adjudication. This is a good test that the new system reduces polling rather than simply moving the polling somewhere else.

Finish lease migration now. Fabric is the authority, but right now legacy helpers can still acquire leases Fabric knows about only after observing their comms/file side effects, while legacy helpers cannot see Fabric holdings. That’s transitional, not acceptable steady state. I would make roles/Ananke/research/lease.py and roles/Nestor/tools/nestor_lease.py thin compatibility frontends onto the shared Fabric lease API. Preserve their CLI if useful so experiments don’t break, but stop creating new host-file leases. Then test a legacy helper and a Fabric Attempt racing for the same resource: exactly one must win. Once both active users are migrated, retire the host-file acquisition path entirely.

The compatibility behavior should be:

old experiment
     |
 legacy lease CLI
     |
     v
 Fabric/Postgres lease authority
     |
 same atomic resource row

not:

legacy files <---- bridge ----> Fabric leases

The latter would become permanent dual-authority complexity.

Then stop building infrastructure

After D12 and the lease cutover, freeze Fabric v0.2 for an adoption experiment. No dashboard, streaming, push, scheduler, priority optimizer, or more protocol work.

The next test should be S3: open-research adoption, because S2 was too easy compared with Artemis.

I would use a principal other than Odysseus and give the fabric roughly 8–12 genuine open research packages with 30–90 minute budgets. They should require repo archaeology, evidence comparison, some coding/analysis, and substantive written conclusions—the same class of work Archaeon and Artemis have been manually farming out.

Freeze beforehand:

* workload;
* budgets;
* required artifacts;
* worker isolation;
* what counts as a principal coordination action;
* what counts as rescue;
* artifact-quality criteria;
* abort conditions.

Then the principal gets one submission action and one completion barrier, not 12 miniature babysitting loops. Workers should run across both Linux nodes as available.

The key measures aren’t only action count. Ask whether the returned work is scientifically usable: fraction producing durable artifacts without rescue, lost/duplicate work, principal interventions, contamination, worker crashes recovered, turnaround, and how many results require the principal to redo the worker’s work.

If Fabric gets coordination below ~1 action/execution and the research quality remains comparable to the manually shepherded workers, that’s the real migration gate.

The same-machine seat experiment should be inside S3

Put another research principal on ubu001 while generic worker.ubu001.* executors are also running there. That tests something important:

host identity, seat identity, worker identity, and scientific context remain separate even when they share the physical machine.

Plant context canaries again temporarily for this test, but make them seat-specific and remove them afterward. A generic worker must not inherit Odysseus’s or the second seat’s memory merely because it runs on ubu001.

This is more valuable than another synthetic protocol test because it attacks the distinction the architecture depends on.

One thing S2 already changes

We should stop writing prompts that say things like:

“Launch four researchers, watch them, collect their reports, and return when all finish.”

For Fabric-enabled seats, the instruction should increasingly become:

“Delegate independent work where it increases epistemic pressure. Use the Fabric for execution; you own question formulation, evidence integration, and scientific judgment.”

That’s a meaningful reduction in prompt complexity. The seat no longer needs detailed instructions about tmux, workers, polling, report deposition, machine selection, or crash handling.

And there’s a bigger conceptual consequence: a seat no longer has to be alive for its workers to be useful, and a worker no longer belongs to a seat. That is the break from the old model.

I’d have Odysseus do exactly four things now: repair D12, migrate the two legacy lease frontends, freeze Fabric v0.2, and prepare S3 with a different research principal. After that, his job should shift from building the fabric to trying to break it under real science.
