# Operator rulings on fabric v0.1 (verbatim, 2026-09-28, received ~20:44Z)

adapt as you see fit.  I ‘d lime to pilot this with another seat at some point, one that is running on the same machine:

This is enough to call the architectural hypothesis validated at v0.1. Not “A2A solved,” and not fleet-ready yet—but the important part worked: durable tasks, isolated workers, capability routing, crash recovery, resource waiting, artifact return, and real science all happened below the principal Claude session.

The D2 result is especially valuable. The fabric didn’t merely shuttle a toy task around; it produced two independent reviews quickly enough to uncover a real security failure that the existing self-tests missed. That is the kind of leverage we wanted.

My rulings

P2 cross-host: finish it. Artemis being offline should no longer be relevant—that is itself precisely the old-model failure we are trying to remove. Start a disposable fabric worker on ubu002 directly under the fabric worker runtime, run the frozen cross-host claim race, and shut it down afterward. Do not wait for Artemis’s persistent seat. If Odysseus cannot launch it remotely with existing access, post a capability request through the fabric/comms and let any authorized process on ubu002 start it. The test passes only if ubu001 and ubu002 race for the same durable Task and exactly one Attempt acquires it.

The Fabric lease becomes the canonical lease authority for new work. Do not maintain two equal lease systems. From now on, new fabric-mediated substantial work uses the atomic shared Fabric/Postgres lease. The existing Ananke/Nestor host-file leases become a migration compatibility surface, not an alternative authority.

During migration, the fabric should detect legacy host leases before granting a conflicting fabric lease. Legacy scripts can continue temporarily, but they must not be invisible to Fabric. The target is one authority, not a permanent dual-reader architecture. Once active heavy-engine seats have moved, retire the host-file convention.

And importantly: no silent fallback from the Fabric lease to a local file if the canonical store is unavailable. For shared heavy resources, inability to see the global lease state means wait, not “probably free.”

A couple of cleanup rulings

Remove the two deliberate canary files now that the isolation test is complete. Their continued presence has no experimental value and creates needless future ambiguity.

Keep ~/fabric-venvs/sci, but record its package manifest and treat it as an explicit capability environment, e.g. python.numpy / python.scipy, rather than “Python worker.” The numpy 2.5.3 versus 2.2.6 discrepancy is fine for the Fabric self-tests, but not for any scientific procedure whose frozen environment calls for 2.2.6. Exact-environment tasks should refuse that worker rather than silently accepting “has numpy.”

The four failed Tasks are actually useful. Don’t erase or cosmetically relabel them. They demonstrate the right failure semantics: bad capability declaration → failed Attempt with captured error → corrected Task/Attempt succeeds. That history is evidence that the runtime is doing its job.

What I think we should do next

Do not immediately migrate every seat.

The next phase should be a measured adoption experiment. Put perhaps three classes of work through Fabric:

1. disposable research workers
   literature / repo archaeology / adversarial review
2. deterministic light compute
   replay / analysis / verification jobs
3. one real multi-worker scientific workflow
   where the principal delegates several Tasks and synthesizes returned Artifacts

Artemis’s 36-run self-test is the perfect historical baseline, but I would not retrofit its still-frozen scoring stage mid-experiment. Finish Artemis normally. Then use its orchestration ledger as the control condition against the next comparable workload run through Fabric.

The metric isn’t throughput alone. We should count principal coordination actions. Artemis had to manually dispatch runs, notice completions, recover report writes, inspect worker isolation, manage concurrency, archive outputs, and shepherd scoring. A Fabric workload should make most of those disappear.

One architectural change I’d make immediately

The fabric worker should become a generic executor identity, not masquerade as the persistent seat whose machine it happens to occupy.

So:

Odysseus
    = scientific / infrastructure principal
worker.ubu001.<instance>
worker.ubu002.<instance>
    = disposable executors
Nestor / Archaeon / Artemis / ...
    = research principals and/or specialized capability providers

That distinction matters. Otherwise we’ll recreate the old confusion where “Artemis is offline” means “ubu002 cannot execute work.” Those should be completely independent facts.

Persistent seats can later expose specialized A2A skills, but generic worker availability should belong to the node/runtime.

D2 should stay FAIL

Don’t let the clean Fabric execution blur the scientific outcome. Nestor’s D2 firewall is currently invalid for its intended assurance. The five demonstrated bypass classes—especially unbound imports in the key-holding process and same-user secret readability—mean the audit boundary isn’t real yet.

Nestor should repair it and resubmit a new Fabric Task for re-audit, ideally without choosing the individual reviewers. That’s a beautiful first example of the new loop:

Nestor repairs
      ↓
submits capability=audit.security.adversarial
      ↓
Fabric routes two independent Attempts
      ↓
Artifacts returned
      ↓
Nestor sees PASS/FAIL evidence

No seat polling. No “has Odysseus read #855?” No operator assigning reviewers.

What has actually changed

Before this, adding another agent often added another inbox, another session to watch, another comms loop, another place where a report could disappear, and another human coordination edge.

Now we have the beginning of a structure where adding a worker can mean simply:

worker announces capabilities
          ↓
more Tasks become executable

That is the scaling property we’ve been trying to get.

I would tell Odysseus: finish P2, make Fabric leases authoritative for new work, clean the canaries, document the capability environment, then stop feature-building and run the next real multi-Task science pilot. No dashboard, no streaming, no push notifications, no scheduler sophistication yet.

The thing to prove next is not another protocol feature. It’s that a research principal can genuinely stop shepherding workers.
