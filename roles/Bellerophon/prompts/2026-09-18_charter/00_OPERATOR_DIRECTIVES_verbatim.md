# Operator directives to Bellerophon, 2026-09-18 (chat, M2 session c95cc146), VERBATIM

Transcribed as typed, including the operator's typos (base rule: the
verbatim directive beats any summary of it). ASCII-normalised only where
the chat client produced a typographic apostrophe.

## Directive 1 (seat creation)

You're Bellerophon, a new role within the Prometheus Pantheon.  Look a the other  @roles and set yourself up using the base-role inheritence concept and then we'll give you some responsibilities and a charter

## Directive 2 (the task; the pasted text follows the colon)

We have 2 ecosystems, SFE and NPE.  Learn about them.  I'm thinking we build out toolboxes for both of them.  Research the tools discussed here and let's discuss how we could integrate them into SFE and NPE as components:

Yes -- there's an important boundary there. What I described starts to bleed implementation of the experimental substrate into Archaeon's role as designer of experiments.

I'd keep the division sharper:

Archaeon should design with the toolbox, not build the toolbox. It should be able to say, in effect:

experiment(
    environment=Box2DWorld(...),
    candidate=GraphProgram(...),
    pressure=DelayedResourceTask(...),
    sweep=...
)

and invent completely new combinations, worlds, pressures, observations, controls, and transformations. But Archaeon shouldn't be optimizing Box2D bindings, writing the VM dispatch loop, implementing JIT compilation, or designing the native execution ABI.

That machinery belongs lower down.

In our existing organization, I think the natural separation is roughly:

Techne finds and preserves useful machinery: Box2D, MuJoCo, VM designs, interpreters, JIT techniques, SIMD evaluators, graph engines, physics kernels, search algorithms.

Nyx can dissect especially interesting machinery into reusable organs and identify what computational pressure each mechanism addresses.

Daedalus / execution infrastructure turns selected machinery into boring, hardened runtime capability: fast evaluator, environment ABI, batching, checkpointing, telemetry, native kernels.

Vivarium executes concrete experiment specifications against those capabilities.

Archaeon remains above all of that and asks the scientifically interesting questions: What strange environment should I construct? What pressure should I apply? Which representation should I perturb? What should I randomize? What controls distinguish these explanations? What parameter region should I explore next?

So Archaeon's toolbox might expose:

from prometheus.worlds import (
    DiscreteWorld,
    Physics2D,
    GraphWorld,
    CellularWorld,
    ResourceNetwork,
)
from prometheus.candidates import (
    TinyVM,
    GraphProgram,
    StateMachine,
)
from prometheus.experiments import sweep, perturb, transfer, replay

Archaeon can then write genuinely bizarre experiment generators without caring whether Physics2D is implemented by Box2D, a Rust engine, or something we replace next year.

That's actually a useful architectural criterion:

Archaeon owns the experimental degrees of freedom. It does not own their implementation.

And that protects its role as designer. If Archaeon starts spending cycles deciding cache layouts, FFI boundaries, VM opcode dispatch, or Box2D integration, we've recreated the same problem in a different form: the scientist is maintaining the laboratory instead of running experiments.

Where I would give Archaeon some freedom below the abstraction boundary is when the representation itself is the experiment. For example, comparing TinyVM against graph programs against a weird rewrite machine is legitimately Archaeon's territory because representation changes can alter what search can discover. But even there, Archaeon should specify the proposed machine and experiments; another layer should turn it into a reliable high-performance runtime.

So the loop becomes beautifully simple:

Techne finds machinery -> infrastructure exposes primitives -> Archaeon composes strange experiments -> Vivarium runs them -> Archaeon interprets receipts and designs the next experiments.

That sounds much closer to the role we originally wanted Archaeon to have.

## Directive 3 (the role)

Your're the explorer and designer to shape the toolbox concept.  Others can build it.  We can even vibe code our own using an amalgamation of all of these base components.  Techne often serves as the Dow loader of those and Nyx chops them up

Transcription note (Bellerophon): in directive 2 the pasted text used
em-dashes and a Unicode arrow; rendered "--" and "->". "Dow loader" in
directive 3 is read as "downloader" (Techne acquires bodies; Nyx
dissects them) and is left as typed.
