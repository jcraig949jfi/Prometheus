# DreamCoder -- failure landscape, the four blockers read as substrate, decoys

Currency: 2026-09-11. Grades per nyx/README.md. The operator's direction
(2026-09-11) asked whether Techne's blockers expose hidden architectural
assumptions, inseparable interfaces, representation dependencies,
environmental assumptions, or mechanisms transferable in prose but not
operationally. Each row answers with the receipt beside it.

## The measured boundary, read as failure substrate (all T1-LOCAL unless marked)

B1  BLK-DC-2, the OCaml solver. opam and ocaml absent; the README's
    switch is 4.06.1+flambda with ten packages; "every domain script
    invokes them" (first_useful_check receipt).
    Exposes: an INSEPARABLE INTERFACE. The enumerator is a separate
    binary in a second language, reached over a wire protocol. In prose,
    "enumerate typed programs in weighted order" is a function; as
    pinned, it is a process tree with a 2018 toolchain. The organ
    organ.dreamcoder.recognition_guided_enumeration.v0 is therefore
    graded: transferable in prose, NOT transferable operationally from
    this source. The design already anticipated the shape (H0-H5 design
    line 130: an external solver needs a bounded backend contract).
    Gradient: cut the enumerator away from the recogniser and rebuild
    the enumerator natively on the Proteus grammar; do not port the
    OCaml.

B2  BLK-DC-1, the Python stack. 38 exact pins from 2019 (numpy 1.16.4,
    torch 1.1.0, scikit-learn 0.21.2, pygame 1.9.6, Box2D-kengz 2.3.3);
    14 of 38 wheel-installable on 3.12 and on 3.11; 22 sdist-only; 0
    gone from PyPI.
    Exposes: a REPRESENTATION DEPENDENCY and an ENVIRONMENTAL
    ASSUMPTION. The recognition model is bound to a specific torch and
    the domains to specific simulators (Box2D, pygame: the physics and
    drawing domains ship inside the system). The mechanism "task ->
    production weights" is representation-bound per domain; the pins
    say the domains are part of the architecture, not plug-ins.
    Gradient: a task encoder is domain machinery, never a transferable
    organ; the transferable part is "weights order the search", which
    needs no network to test (see the organ's CONTROL).

B3  The recipe. README names docs/official_experiments, which does not
    exist at the pin; the root file of that name holds 331 non-blank
    lines of which 199 are `bin/launch.py -z <machine>` GCP invocations
    (60.1%), machine types up to x1.32xlarge and n1-megamem-96, per-run
    timeouts from 1 s to 57,600 s.
    Exposes: a HIDDEN ARCHITECTURAL ASSUMPTION -- the published
    behaviour is a property of (algorithm x compute envelope), and the
    envelope is a cloud fleet. No local recipe exists; Techne's receipt
    says so and asserts no replication. The wake budget is the hidden
    parameter of every published number.
    Gradient: any organ from this specimen carries cost_class and a
    note that its fitness value was demonstrated at a scale this
    program does not have; a soup organism inheriting the loop inherits
    a budget assumption it cannot meet.

B4  BLK-DC-4, the resource envelope. Local ceiling 7,200 s on 16
    logical CPUs, no cloud launcher authorised; "none of the official
    commands fits any declared profile, at any tolerance".
    Exposes: the same ENVIRONMENTAL ASSUMPTION as B3 made quantitative:
    a factor of 8 in wall time and 6 in CPUs between the smallest
    published run and the local ceiling. The charter's compute
    discipline (XIV) reads this as: resource appetite is part of the
    phenotype, and this specimen's appetite is recorded, not excused.

B5  Blocker count. The receipt's prose says four independent blockers;
    its blockers array carries BLK-DC-1, -2 and -4 with no -3. The
    fourth boundary is the recipe (B3), reported in the same receipt
    under recipe_location.CLAIM. Recorded as a reporting-shape fact
    about the receipt, not corrected.

B6  Licence. The only LICENSE file is the AngularJS MIT text
    ("Copyright (c) 2010-2020 Google LLC"); GitHub's "MIT" classifier
    inherits the mistake (techne/LICENSING_AND_COSTS_2026-09-10.md).
    Exposes: a PROVENANCE defect in the ancestor itself. Under NYX-25
    the organ is admitted with its ancestry recorded; nothing from the
    DreamCoder code is redistributable. The executable organ Prometheus
    holds is Stitch's, MIT (Bowers), which is why the compression organ
    carries two ancestors.

B7  Submodules: pyccg pinned to a moving branch (forced to c465a23);
    pregex and pinn declared over SSH (transport rewritten). Exposes:
    the system's identity depends on three other repositories' states.
    A specimen is a graph, not a commit.

## Failures observed on Prometheus's own corpus (T1-LOCAL)

F1  EMPTY. Stitch on PHASE1_3 (the only corpus a held-out evaluation
    permits): 0 abstractions, cost 906 -> 906. Archaeon's repeated-
    subtree extractor: 0 of 3 candidates kept. "Three solutions of 2-4
    grammar nodes contain no subexpression repeated across two of them.
    That is a fact about the corpus, not about either extractor."
    Failure shape: the ORGAN is fine and the WORLD has no recurring
    structure at the scale of its solutions. The eligibility count for
    pressure.dreamcoder.recurring_structure.v0 on this corpus is 0.
    Gradient: the H0 'library' cells cannot fire on the H1 split as it
    stands; a task family with shared parts must be constructed (that
    is Vivarium's and Archaeon's work, and it is the delivery).

F2  LEAK. Stitch on ALL_17: 3 abstractions, 6548 -> 2912, and all
    three ARE held-out phase-2 solutions; a search given them finds the
    targets as size-1 leaves; viv_library_leak verdict SOLVES_A_TASK;
    Techne refuses the export. Failure shape: the cheat control fired as
    a defect in the wild. Gradient: this is the strongest evidence in
    the specimen -- the leak detector can see the thing it claims to
    see -- and every library cell must run the cheat beside it.

F3  SYNTAX-BOUND. "stitch abstracts over SYNTAX" (Techne): two
    semantically equal programs written differently share nothing.
    Failure shape: the organ's notion of 'part' is a human
    representation choice. Gradient: a canonicaliser upstream is a
    separate organ with its own leak risk.

F4  Techne's own threshold (T1-LOCAL that it was measured; the number
    is in techne/acquisition/checks/stitch_on_boolean.py's receipts,
    not re-read here): abstractions became non-empty at 3 programs on
    synthetic fixtures that SHARED structure by construction; the real
    corpus of 3 did not. Failure shape: a threshold measured on a
    population that was built to have the property.

## Remembered from the lineage (T2; not quoted)

F5  Cold start: if the first wake solves nothing, sleep has nothing to
    compress (T3: reasoned from the mechanism; PHASE1_3 is the local
    instance of the state).
F6  Library bloat / memorisation when abstractions are chosen from few
    solutions (T2 that the lineage discusses it; F2 is the local
    instance).

## Decoys and broken variants ready for a soup (charter XIII)

D1  DECOY re-description: rename random subtrees of random size,
    reporting a 'compression' that is the renaming's byte saving.
    Passes a cost-only read-out; solves nothing faster.
D2  BROKEN compression: the leak variant -- the compressor's input
    includes the targets (F2 is the fixture; no construction needed).
D3  BROKEN compression: arity cap 0 (whole-subtree repeats only, no
    holes) = Archaeon's extractor; on a corpus where the two differ this
    is the ablation of holes.
D4  DECOY ordering: weights drawn at random per task (the cheat
    inverted): must do no better than uniform.
D5  BROKEN loop: sleep runs before any wake (compress an empty corpus,
    then search): must equal the no-loop baseline exactly.

None is implemented; D2 exists as a measured receipt already.
