# DISCARDED-LANGUAGE LEXICON (directive §10)

Search vocabulary for finding what researchers noticed but did not pursue. **Leads, never evidence.** Most hits are noise; the job is the tiny fraction that survives interrogation.

Rule: these terms are used in *retrieval within a field's own corpus*. They are never combined with Prometheus vocabulary, and a hit is logged in `D_FAILURE_ANOMALY_REGISTRY.jsonl` with its verbatim quote and locator before any interpretation is attached.

---

## Core list (from the directive, all fields)

unexpected · surprisingly · anomalous · transient · unstable · unexplained · incidental · spontaneous · emergent · neutral · deleterious · pathological · degenerate · idiosyncratic · seed-dependent · run-dependent · unusual · unanticipated · difficult to reproduce · rare · disappeared · temporary · plateau · collapse · cycling · stalled · failed to converge · outlier · excluded · discarded

## Field-specific extensions

**Evolutionary computation / GA**
premature convergence · hitchhiking · deception · loss of diversity · stagnation · epistasis (as complaint) · "we do not understand why" · "for reasons that remain unclear" · disruptive crossover · lethal offspring · "runs were terminated early" · "one run in twenty"

**Genetic programming**
bloat · introns · non-effective code · destructive crossover · code growth · "the solution was difficult to interpret" · unexpectedly large · "we removed the redundant code" · hyperselection · population collapse

**Digital evolution / artificial life**
parasite · cheater · hyper-parasite · exploit · degenerate replicator · sterile lineage · extinct · quasi-species collapse · mutational meltdown · "the population died" · "this occurred only once" · "an artifact of the implementation"

**Neuroevolution / evolutionary robotics**
reality gap · brittle · overfit to the simulator · "exploited a bug in the physics" · fell over · degenerate gait · "the controller did nothing" · sensor exploitation · noise-dependent

**Evolvable hardware**
substrate-dependent · did not transfer to another chip · temperature-sensitive · "the circuit stopped working when we" · disconnected cells · analogue behaviour · unrepeatable

**Cellular automata / computational mechanics**
metastable · epoch · particle · domain wall · defect · "the rule ceased to work at larger lattice sizes" · scaling failure · symmetry breaking · "an unusual space-time pattern"

**Artificial chemistry**
elastic collapse · trivial fixed point · organisation dissolved · "the reactor converged to a single species" · unproductive · self-maintaining but not evolving

**Coevolution**
Red Queen · cycling · loss of gradient · mediocre stable state · disengagement · forgetting · intransitive · "progress could not be measured"

**Learning / meta-learning precursors**
catastrophic forgetting · did not generalise · overfit · "learning was unstable" · "we could not reproduce the reported result" · schedule-sensitive

---

## Where to search, in order

1. **Discussion and future-work sections** — where anomalies are confessed and abandoned.
2. **Theses and dissertations** — they contain the experiments that did not make the paper, including negative ones.
3. **Source-code comments** — `XXX`, `HACK`, `this shouldn't happen`, `weird`, `why does this work`, disabled blocks, and commented-out experiments.
4. **Workshop and late-breaking papers** — lower editorial pressure to report only successes.
5. **Technical reports and archived project pages** — parameter sweeps and run logs that never appeared in print.
6. **Errata, retrospectives and anniversary reflections** — authors saying what they would do differently.

## Anti-pattern warning

This lexicon retrieves *language*, and language is produced by authors, not by systems. Two failure modes to guard against:

- **Author-style confound.** Some researchers write "surprisingly" habitually. Frequency of anomaly language is a property of the writer before it is a property of the experiment.
- **Publication-era confound.** Candour about failure varies by decade and venue. A 1994 workshop paper and a 2019 conference paper differ in how much they admit, independent of what happened.

Both mean the lexicon can only ever open a file. The evidence is in what the system did, not in how it was described.
