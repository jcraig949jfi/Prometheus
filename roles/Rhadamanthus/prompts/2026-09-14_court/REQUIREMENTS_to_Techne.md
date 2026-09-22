# Requirements to Techne (and others) from the court build, 2026-09-14

Source: engine/necropolis/workshop/FORENSIC_QUESTIONS.md (question -> instrument
map, generated, validator-enforced) and case POLLUX (see case_pollux/).  These are
GAPS, stated as the observation each missing organ would make possible.  None of
them is an instruction to build; empty cells are a product, and a Techne lane that
chooses not to fill one should say so in its own record.

## From the map (13 charter questions + 3 surfaced)

  RQ-1  FQ-02 positive control.  No admissible instrument PLANTS an effect of a
        named claim class and shows a candidate statistic detects it at a rate
        not pinned at alpha.  DISP-001 (CR-001) died on exactly this: its split-
        half positive control was pinned at alpha by the statistic's own
        construction.  Needed: a planted-shift generator keyed by claim class
        (location / scale / rank / dependence / changepoint), Keeper-controlled,
        that any future CORONER plan can cite as its positive control.
        Consumer: coroner_run.py plan.controls.positive; the CR-001 descendant
        cannot be written without it.

  RQ-2  FQ-05 leakage.  Admissible detectors (NT-030, NT-021) see EXACT-equality
        leaks only.  The 2026-08-12 ladder leak was exact; the next one will not
        be.  Needed: a derived-leak probe (can a k-line reader of the judge's
        visible fields recover the answer above chance) with its own chance
        floor.  NT-001 remains UNTRUSTED and is the object of this probe, not a
        component of it.

  RQ-3  FQ-10 semantic comparator.  Degeneracy, costume and scale are detectable;
        "the code computes X while the claim says Y, both non-degenerate" is not.
        Needed at the SUBSTRATE, not the workshop: a declared-quantity field in
        every claim record (what is measured, over what population, in what
        units) so a reader can exist.  Without the field there is nothing to read.

  RQ-4  FQ-11 environment.  Store identity and cwd convention are covered (NT-043,
        NT-054, NT-055).  Package / interpreter state at claim time was almost
        never recorded; FRANKENSTEIN_XREF 'missing_here' is per-host.  Needed at
        the substrate: every run receipt emits interpreter version, pip freeze
        hash, and the NAMES (never values) of env vars read.

  RQ-5  FQ-12 replay.  Admissible replay exists for 5 producers (Pollux, Archaeon
        H3, sigma_kernel, prometheus_math ledgers, Techne canon) out of a 48-agent
        roster.  For daemons whose state/ was gitignored (FRANK-003) there are no
        bytes to replay.  Needed: (a) a lane-launch rule that a producer ships a
        replay entry point + fingerprinted fixture before its first tick;
        (b) for the dead, nothing -- the cell is EMPTY and stays so.

  RQ-6  FQ-13 / FQ-03 alternative judge.  For LLM-graded claims there is no
        admissible second instrument: NT-082 needs an absent package, NT-083 a
        fine-tuned verifier, NT-001 is untrusted.  Needed: EITHER Keeper controls
        for NT-082/NT-083 (planted-wrong / planted-right / constant-responder
        cases through tests/run_controls.py) OR a ruling that LLM-graded claims
        are NOT cross-examinable and their failures carry UNDECIDABLE_ON_RECORD.

  RQ-7  FQ-14 forking paths.  No instrument compares the set of runs that EXISTED
        with the set REPORTED; NT-051 / NT-050 / NT-015 are denominator fragments.
        Needed: a run-directory enumerator that pairs result files with the
        claims that cite them and lists the uncited remainder.

  RQ-8  FQ-15 temporal order.  Commit order bounds write order from below; claims
        edited in place have no ordering evidence.  Needed at the substrate: claim
        records carry the hash of the evidence they cite AT WRITE TIME
        (certificates must fingerprint inputs, feedback 2026-08-25).

  RQ-9  FQ-16 power.  p floors are covered (NT-025); power against a claimed
        effect size is not.  Needed: a power calculator that takes the claim's
        declared effect size (RQ-3 again: without the declared quantity there is
        no effect size to take).

## From the admissibility ladder (registry-wide)

  RQ-10 21 rows are blocked at CONTROLLED (author tests only): NT-058, 060-076,
        084, 085, 087.  Each has a runnable import and author tests but no Keeper
        control (a case that can fail).  These are the cheapest promotions in the
        registry and the Keeper will not write their controls: the author lane
        should nominate the defect shapes its tool must catch, and the Keeper
        will write the cases that plant them.  Techne's own rows in this set
        (NT-064 fossil isolation, NT-072, NT-075 Ergon packet invariants) first.

  RQ-11 10 rows blocked at IMPORTS (NT-017, 020, 077, 079, 082, 083, 086, 088,
        089, 090): absent packages or moved modules.  A requirements pin per row,
        or a ruling that the row is HISTORICAL_ONLY.

  RQ-12 6 rows have Keeper controls but hold NEEDS_VALIDATION (NT-009, 014, 022,
        035, 046, 057): each has at least one control FAIL/ERROR on record.  These
        are findings about the tools, not about the Keeper; the author lane
        should read tests/controls_result.json for its ids.

  RQ-13 NT-003 (prometheus_math KillVector builder) is admissible and answers
        none of the sixteen forensic questions: a validated instrument with no
        forensic question.  Recorded, not acted on.

## From case POLLUX (appended after adjudication -- case_pollux/ADJUDICATION.md section 5)

  RQ-14 Coroner step-chaining.  coroner_run.py execute() passes literal kwargs to each
        action and carries no data between steps, so the decisive observation of case
        POLLUX (Cleric C-C: load 9 pairs, deduplicate each subset by M at 1e-9, call
        NT-048 historical_statistic on each, report 9 x 2 (corr_norm, verdict)) cannot be
        written as a plan.  Needed: a driver form for plans -- a named step whose output
        is the next step's input, fingerprinted in RESULT.json -- under the same MAY
        clauses and <run_dir> confinement.  Contract v1.1 work; the Keeper owns the
        contract and will write it once the shape is agreed; recorded here so that Techne
        does not build a parallel one.  Also recorded: the dry check does not bind action
        kwargs to the function signature (CR-001 carried a `_note` kwarg that would have
        raised TypeError at step 0; fail-closed held).  BACKLOG RHAD-45.

  RQ-15 Planted-duplicate positive control (FQ-02 again, a second claim class).  The
        Cleric's finding is that ulp-distinct encodings of one value form near-zero-gap
        blocks that any gap / spacing statistic reads as signal.  Needed: a
        Keeper-controlled tool that plants a duplicate block of size k into a synthetic
        non-duplicated subset and reports whether a candidate statistic's verdict moves;
        without it the C-C plan has no positive control and dies like CR-001.

  RQ-16 (to the Stygian / Charon owner, not Techne) Static read of every
        charon/agents/stygian/loaders/composition_*lehmer*, *mahler* loader for gap,
        spacing or difference operations over the curated Mahler tier.  If any computes
        gaps over the raw literals, it carries the case-POLLUX defect live.  ADJUDICATION
        U5.

  RQ-17 (to the AUTOPSY_TAXONOMY owner) CONSUMER_ABSENT conflates three records: no
        reader; readers that consumed every row to no effect (inert -- this case); readers
        that inverted the rows (ergon gold=False on all 286).  The certificate field was
        not extended today (RHAD-15); the distinction is requested at the taxonomy, with a
        migration note, not by editing old certificates.

  RQ-18 (rule for plans, no build) "permutation null" is not a specification.  Two readers
        used the phrase for different operands (values before sorting -- invisible to a
        sorted-multiset statistic; gap series after normalisation -- changes corr_norm)
        and a third proposed a split-half null that would certify the artifact.  Any
        future plan naming a permutation or resampling null must state the operand, the
        population it represents, and the rate at which it PROMOTES on same-shape
        independent draws (case POLLUX: R2 gives ~0.22 mean corr_norm at every n).

  RQ-19 (to Pronoia, no status attached) "9 pairs, 9 constant outcomes, 286 rows, every
        row counted substantive by Erebos" is a measured instance of
        emission-without-information suitable as a calibration case for a liveness
        auditor; the Erebos _filter_substantive_recent seam (erebos/daemon.py:87-106) is
        where a per-(pair, instrument-version) novelty gate would have caught it.
