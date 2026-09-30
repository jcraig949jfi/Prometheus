# Adversary 2: an alternative ontology for NPE (sites, contents, contexts, and the pair-rewrite map)

Independent critic, fresh context, 2026-09-30. I read the seven reader dossiers A-G in full and the world code
(`campaigns/z80atlas-verify-2026-09-22/world.py` `_pair_epoch`/`_pair_interact`/`_mutate`, `z8.py`, `p11.py`). I did not read
anything else under `inference_harvest_2026-09-30/`. I wrote nothing to the repository except this file. I made no git writes
and ran no world campaign.

**What I computed.** Section 6 reports small read-only probes. They call `p11.interact` or `z8.run` on a private tape, for
a handful of genomes, against random partners. I also ran one toy mean-field process built only from those calls. That
process is *not* `world.Runner`: it uses 256 sites and 300 epochs, and runs 3 seeds for each of 2 genomes.
- Total CPU was about 95 s.
- I ran with `PYTHONDONTWRITEBYTECODE=1`, so no `__pycache__` was written in the repo.
- The scripts are in the session scratchpad and not in the repo: `pairmap.py`, `probe2.py`-`probe6.py`, `toy.py`.
- Numbers from these probes are tagged **[P]**. Numbers quoted from dossiers are tagged with the dossier letter.

---

## 0. The one code fact that forces a new ontology

On `PAIR_TAPE`, no organism is ever created or destroyed by reproduction. Five code facts show this:

1. **Genomes go back to the slots they came from.** `_pair_interact` concatenates two slot contents on a 128-byte tape and
   runs side 0 and then side 1. Each runs from its own half-start, with its *own carried register file*
   (`world.py:801-812`). Each half is then written back to the slot it came from (`world.py:825-833`).
2. **A "birth" is a relabelling.** A birth only reassigns the label: `org.pid, org.anc, org.oid = src.oid, src.anc,
   next_oid` (`world.py:877`). The slot, and the register file (`org.regs`), stay with the victim.
3. **Nothing dies in these cells** (E §1.1). The population is a fixed set of sites.
4. **Only 7 bits of any pointer matter.** Addresses are masked to the 128-byte tape (`z8.py:180, 207`). The effective
   "register context" of a copier is therefore small: the low 7 bits of L and E, the copy count modulo 128, and the
   direction. H and D are irrelevant.
5. **Copy length is set by the slice budget.** `BC = 0` means 65,536 (`z8.py:403-412`), and the copy is truncated to the
   remaining slice budget. So copy length is a function of the slice budget and of how many instructions ran first.

**What the system is.** It is a fixed field of **sites**. Each site holds a **content** (L bytes) and a **context** (a
register file). A random matching rule applies a stochastic **pair-rewrite map** to the field each epoch. Everything the
heredity ontology calls an individual, a birth, a lineage or descent is a *derived and thresholded* reading of that map.
The world adds two post-processing rules on top: `_mutate` (with the splice on the RECOMBINATION axis), and, in later
work, the ATOMIC keep-rule.

---

## 1. Diagnosis: which concepts are mis-carved, and where they broke

### 1.1 "Organism" fuses three things with different dynamics

An `Org` on the pair tape fuses three things:
- a **site**: the slot, which persists for the whole run;
- a **context**: the register file, which stays with the site across content replacement;
- a **label**: `oid`/`anc`, which moves with *promoted* content transfers.

Each has its own dynamics, and every major correction in the record is one of these three coming apart:

- **C9-D14** (C §1.6). In both H3 cells, 128/128 organisms were never the child of any edge, yet their median identity to
  their own birth genome was 0.000. The *site/label* persisted while the *content* was completely rewritten by
  sub-threshold writes.
- **FF-11** (F §1.8). A "birth" is an in-place renaming of the victim body. The new "individual" is the old site, running
  the donor's content in the victim's register context.
- **Id ≠ material / "founder-descended" = slot lineage.**
  - X-CONTENT: anc0 share 0.98-1.0 alongside a median founder-byte share of 13-25% (A §28, B X-CONTENT).
  - X-MAT: D0 bytes are 3-33% of the state-free L genomes (F §5.1).
  - Early and late "in-lineage" genomes share about 5/64 aligned bytes (D U9).
  - The label is carried by the predecessor criterion, "causal or not" (B §0.2).
- **Register-state findings are site-context findings.** The newborn content runs in the *victim's* registers. This covers
  self-poisoning, zero-specialization and state-freedom. A genome's "competence" is therefore always competence *in someone
  else's context*, which is why it reads as an environment-supplied scaffold (D §1.12; E §1.4).

### 1.2 "Birth / replication event" is a threshold imposed on a continuous rewrite

**[P]** One interaction between random contents in 7ae3's cell (BASE write-back, random contexts, 400 halves):
- 78.5% of halves change;
- the mean change is 3.06 bytes (median 2);
- 14% change by 7 or more bytes;
- **0 of 400** are promoted by the predecessor criterion.

X-STALL-F0 found the same thing inside lineages: 57% of member interactions change the genome, by about 5.55 bytes
(A §25).

So the content field is rewritten *all the time*. The birth criterion (fid_other >= 0.9, fid_self < 0.9, donor
writes >= n/4) selects a thin, arbitrary slice of that flow and gives it the name "reproduction". Everything outside the
slice is invisible to lineage, depth and anc. That includes sub-threshold transfer, residue, and partial overwrites that
carry up to 6 foreign bytes into every accepted "child".

### 1.3 "Donor / copier" is an execution context, not a material agent

The world credits authorship to the *executing context* (FF-31). The material that executed can belong to someone else:
- the Artemis side-1 hijack (F §1.1);
- AN8, where the victim stays donor-like with the donor's writes blocked in 11/34 births (F §4).

**[P, new]** I tested this on 7ae3 placed at side 0:
- In **39/64** random partners, the partner's half ends up copied over 7ae3's half. The world records this as "7ae3 was
  overwritten by a non-anc0 donor", and the label goes to the partner's anc.
- The copy disappears in **34/39** when 7ae3's half is replaced by random bytes before the partner runs.
- It disappears in **30/39** when only 7ae3's four bytes SELF+LDIR (positions 23, 24, 52, 53) are zeroed.
- 7ae3's own context writes only 2-3 bytes outside its half, almost always a 0x00 at the partner's position 0.
- The partner's pc runs into 7ae3's code. There SELF returns the *partner's* base, so LDIR copies the partner.

The "victim-magnet" anomaly (B A6; U1 100/240 founder overwrites) is therefore 7ae3's own copy machine executed by the
partner. The record credits agency, authorship and the lineage label to the wrong party.

### 1.4 "Replicator / competent" is construction at one context point

P-11 certifies construction: painters pass, and 3/57 donors self-copy (C §1.8; F §1.1-1.3). The COMPETENT ruler scores
that construction at *one* point of context space: all-zero registers and a blank partner (D §0).

**[P]** Contexts show why one point is not enough:
- **c2a8** converts random partners at 0.81 from *random* contexts but at 0.00 from the zero context. This is exactly the
  "anti-zero donor" type (D U4, anomaly 3). It is also the only C-ATOMIC C2 specimen that ran away (B U6: fresh-state rate
  0.005, depth 39).
- **The 3-byte `1E 40 E5` minimal copier** converts 0.60 of partners from random contexts when padded with NOPs, but
  **0.00** when its passengers are random bytes.
  - The zero-padded "state-freedom" is a fidelity artefact: a rotated copy of a zero sled still matches 0.9 of a zero sled.
  - This is the same failure as E anomaly 8, where the D32 rescue over-fires on 60/64-zero genomes.

### 1.5 The painter/copier boundary is drawn on the wrong axis

The program classified by composition (dominant-byte share) or by whether a block-copy op is present. Both fail:
- Z6h is a real copier at 91.7% 0x00, while Z2 is a painter at 48% dominance (F §1.1).
- 4931, a 0x36 near-homopolymer that Odysseus labels PROV, "converts" random partners at 0.81 from side 1 in the zero
  context **[P]**.

In map terms the boundary is simple. A painter's *image* does not depend on its own content. A copier's image moves with
its content. The operational test is the transmission Jacobian (§2, Q5), which is what CVT-R approximates.

### 1.6 "State-free" is a measure over a small, enumerable phase space

The two state-free rulers disagree (E anomaly 1). The transplant ruler finds 182/332 state-free, while C-A3 finds 93/94 D0
sets not free under STATE_FREE. They sample different fixed register vectors from a space that, on this tape, is
effectively only the pointer phases. The cycling single-k ruler failed for the same reason (E §3.2): carried pointer phase
is periodic.

**[P]** Self-poisoning is arithmetic, not biology. For the copier `k NOP-bytes; LD E,0x40; LDIR` with random passengers,
under carried state (side 0, 16 successive interactions):

| k | copy count | count mod 128 | conversions (16 interactions, carried state) |
|---|---|---|---|
| 0-2 | 298-296 | 42-40 | first interaction only |
| 38-41 | 260-257 | 4-1 | first only |
| **42** | **256** | **0** | **16/16** |
| 43-47 | 255-251 | 127-123 | first only (one stray at k = 44) |

A copier whose copy length is congruent to 0 mod 128 returns L to its own start after every execution. It is "state-robust"
with no register initialization at all. With a count of 298, L advances by 42 per run, and the conversion orbit has period
128/gcd(42, 128) = 64. Which donors are "poisoned" is a function of the slice budget, the pre-copy instruction count and the
tape length. It is not a property of the genome alone.

### 1.7 "Establishment / runaway" measured by depth conflates three quantities

`max_causal_replication_depth` is:
- world-level (W7, X-SWAP-ORIGIN);
- a maximum over a branching tree (A §6.4);
- broken by P-11 certification failures at 5-36% per edge (A §6.4);
- produced only by *promoted* rewrites.

Once one content family occupies every site, a family-to-family overwrite usually fails fid_self < 0.9, so it produces no
birth at all. Depth after takeover therefore measures **within-family turnover** (how fast relatives drift more than 10%
apart and overwrite each other). It does not measure establishment.

Evidence from C-ATOMIC per-run files `c9x/c_atomic/results/*.json` **[P, tabulated]**:
- **cb7f under ATOMIC:** 8/8 runs make 163-1,053 P-11 events, and depth is 4-6 in every run.
- **7ae3 under ATOMIC:** runs split into events <= 1,538 with depth <= 16, and events >= 64,159 with depth >= 37.

These are two regimes: takeover without turnover, and takeover with turnover. The depth ruler reads the first as "never
establishes".

### 1.8 "Erosion" is not a partner attack

Members rewrite themselves about as often as partners do: self 3,507, partner 3,241, both 8,024 (A §6.6). ATOMIC also
keeps non-causal promoted overwrites and deletes self-writes (B A2).

In map terms, much of "erosion" is the copier's own **wrong-side action**. A tape-anchored copier copies "half 0 to half 1"
in *tape* coordinates:
- at side 0 it copies itself;
- at side 1 it copies its partner over itself **[P: `1E 40 ED B0` at side 1 keeps its own half in 2% of random partners]**;
- 7ae3 is hijacked at side 0 (§1.3).

### 1.9 "Internalization" is scored on a label and a single checkpoint

The C-A3 EVENT reads "the last checkpoint with any state-free genome" (E §6.1), and 4/8 events are transient. "In L" is the
label, and founder bytes are a minority (F §5.1). The claim is well supported *as a label-compartment regularity*. But its
units (a lineage that internalizes) are the units that §1.1 dissolves.

---

## 2. The alternative decomposition

### 2.1 Primitive objects

**P1. Site σ.** A fixed slot (N = 256 at tier M). A site persists for the run.

**P2. Content c_σ ∈ {0..255}^L.** The bytes in the slot. This is the only thing the tape moves between sites.

**P3. Context r_σ.** The register file and flags that stay with the site. On the pair tape the pc is *not* carried: each
interaction starts at the half-start. Because addresses are masked to 7 bits, the relevant context is the **pointer phase**
π_σ = (L mod 128, E mod 128, BC mod 128, and the direction-relevant flags). In general, the context is the projection of
r_σ onto the address bits the tape can see.

**P4. Interaction ι = (σ_a, σ_b).** An ordered pair drawn by the matching rule. Side 0 executes first.

**P5. The pair map Φ.** Φ : (c_a, r_a, c_b, r_b) → (c_a', r_a', c_b', r_b'). It is deterministic except for copy errors,
and it is exactly `p11.interact` with the world's slice, ops mask and copy-mutation rate.

**P6. The write-back rule W.** W is applied after Φ:
- BASE: write back, then `_mutate`, including the splice on the RECOMBINATION axis;
- ATOMIC: restore the pre-interaction content unless the half was promoted, then `_mutate`.
W is a *world* rule and is kept strictly separate from Φ.

**P7. The byte-event graph.** For every output byte of an interaction there are three relations:
- **EXEC(context → code bytes)**: which context executed which tape positions, and whose content those positions held;
- **WRITE(context → position)**: `prov` / `prov_lit` already record this;
- **READ(position → value)**: the source position of a copied value (LDIR or LD r,(HL) chains), which z8taint partly
  tracks.

Copying, painting, hijack and residue are different *motifs* in this graph:
- **Copying:** the output value at p was READ from content x, by a context EXECUTING x's code.
- **Painting:** the value comes from an immediate operand in the executed code, not from a read.
- **Hijack:** EXEC context ≠ owner of the executed code.
- **Residue:** position p was not written at all.

### 2.2 Relations

1. **Conversion x ⇒ y**: under Φ, content x turns partner content y into x-like content (defined per side and context).
2. **Import x ⇐ y**: x's half becomes y-like. This covers wrong-side self-copying and hijack.
3. **Family F**: the smallest set of contents closed under the images of Φ that start from x (up to W's mutation). This is
   a content-defined *autocatalytic set*, not a label.
4. **Occupancy**: the set of sites whose content is in F.

### 2.3 Measurable quantities

Each quantity is implementable today with `p11.interact`, `z8taint` and the corpus. Π is a declared partner ensemble:
uniform random, the realized population at epoch t, or the family itself. R is a declared context ensemble: phase 0,
uniform phase, or the realized carried contexts.

- **Q1. Conversion kernel** κ_x(s, Π, R) = P[fid(partner_out, x) >= θ].
  - Report it with θ applied to *transmitted positions only* (Q5), not the whole genome, to remove low-complexity inflation.
- **Q2. Retention and import.**
  - ρ_x(s, Π, R) = P[own half stays x-like under W].
  - η_x = P[own half becomes partner-like].
  - Split η by EXEC motif (self wrong-side copy, hijack, partner copy).
- **Q3. Offspring law.** Per interaction, the number of x-like halves after W is 0, 1 or 2 (p0, p1, p2). This gives:
  - mean m_W(x) = p1 + 2·p2;
  - Galton-Watson establishment probability, 1 − p0/p2 when that is positive.
  This is a **computed** lottery ticket, not an empirically discovered one.
- **Q4. Closure and self-pair fixed point.**
  - Is Φ(x, x) = (x, x)?
  - What share of x's products are themselves converters (image ⊆ converter set)?
  - What is the family turnover rate τ_F, the rate of promoted rewrites among members of F at saturation?
- **Q5. Transmission Jacobian.** For each position i, perturb x_i and record two things:
  - T_x(i) = P[the variant appears at position i of the product | conversion];
  - E_x(i) = P[the variant abolishes conversion].
  From these:
  - **specification size** = |{i : E_x(i) high}|;
  - **heredity capacity** = Σ_i T_x(i) over non-essential positions, in bytes or bits;
  - **painter index**: T ≈ 0 means the image is independent of x.
- **Q6. Image dimension.** The number of distinct products over a partner sample, with copy errors off. It is 1 for a
  constant map, whether that map is a copier or a painter, and approaches the number of partners for a non-converter. It
  is a contraction measure, and Q5 is what separates copier from painter.
- **Q7. Context set** 𝒞_x = {π : κ_x(π) >= ½}.
  - The phase space is about 128 × 128 per side for L and E. It is **exhaustively enumerable** in seconds per genome, so
    no fixed random vectors are needed.
  - Report the measure μ(𝒞_x) and whether the origin belongs to it.
- **Q8. Context dynamics.** G_x : π → π' after x executes; for a BC = 0 copier, the phase advance Δ_x = copy count mod 128.
  - The **closure index** is the share of 𝒞_x mapped into 𝒞_x by G_x.
  - "Internalized" means closed: the content re-establishes its own working phase, via SELF, an immediate LD, or
    Δ ≡ 0 (mod 128).
- **Q9. Occupancy trajectory** O_F(t) = |{σ : c_σ ∈ F}| / N. The takeover time t_F is the first t with O_F >= ½.
- **Q10. Material flow.** Through z8taint, the shares of bytes in F-occupied sites that were copied from F, computed by F,
  residue, or mutation. This is X-MAT, but keyed on content membership, not on the label.

**The population-level objects are attractors** of the Markov chain on the site field:
- **S (soup):** no family with m > 1 is present;
- **A_F:** F occupies the field.

Transitions S → A_F occur at a rate set by carrier exposure × P_est(F).

---

## 3. Re-description of the main findings

**False positives (1,031 → 57 → 3).**
- In map terms, all 1,031 flags were produced by **W, not Φ**. The splice on the RECOMBINATION axis made 910 (C §1.5,
  Z80A-D05), and population convergence made the rest.
- A kernel κ measured on Φ alone, against random partners, would never have counted them.
- `births_similar_no_write` marked the artefact perfectly (906/910 against 0/121; C §5.4), because it is a Φ-free
  similarity counter.
- **Hidden by the old terms:** the 1,031 were a property of the world's post-processing, and the scheduler amplified them
  (C §5.1).

**Dense encoding.** A 1-byte alias raises the density of converter contents in content space.
- A random genome contains an alias with probability 0.39, against 0.0019 for the 2-byte pair (D U2).
- "Carrier exposure" is simply the frequency of κ-positive contents in the field.
- **Revealed:** the specification size of a converter is 3-4 bytes (**[P]** essential set {0, 1, 2} for `1E 40 E5`). So
  the discovery barrier is the density of a 3-4-byte motif in the field, not "encoding length" as a trait of organisms.

**Splice.** The splice belongs to W, and it acts on products.
- **Old reading:** it "prevents runaway".
- **New reading:** it lowers m on the family's products (20% per half per epoch). A near-critical process that has started
  is then pushed below criticality.
- **Prediction:** the splice cuts only the tail. Observed: depth >= 1 was 81 vs 77, while runaways were 0/222 vs 22/630
  (A §6.8, §4).

**Establishment lottery.** The lottery is Q3.
- 7ae3 against random partners **[P]** (500 interactions per context):

  | context | write-back | p0 | p1 | p2 | m | GW survival |
  |---|---|---|---|---|---|---|
  | ZERO | BASE | 0.316 | 0.258 | 0.426 | 1.11 | 0.26 |
  | ZERO | ATOMIC | 0.206 | 0.368 | 0.426 | 1.22 | **0.52** |
  | RAND | BASE | 0.376 | 0.272 | 0.352 | **0.98** | 0 |
  | RAND | ATOMIC | 0.178 | 0.470 | 0.352 | 1.17 | 0.49 |

- The observed single-founder ATOMIC runaway rate, pooled over C-ATOMIC C1 (46/80), X-ATOMIC (36/64) and C-CORE (27/64),
  is **109/208 = 0.52**.
- Under BASE, copies placed into sites with carried, non-zero contexts are *subcritical* (m 0.98). That predicts
  "cessation, not extinction": sites persist and conversion stops (A §21). It also predicts that the 3.5% of BASE runaways
  need an m-raising variant.
- **Revealed:** the lottery ticket is computable from single interactions in under a second. It is a property of Φ and W,
  not of lineage history.

**Erosion and ATOMIC.** ATOMIC is a **quantizer**. It turns a continuously rewritten field into a birth-death process by
discarding every unpromoted rewrite.
- It works mostly by cancelling the copier's own wrong-side import (§1.8, §1.3). Under ZERO context, it lowers 7ae3's p0
  from 0.32 to 0.21.
- **Hidden by the old terms:** "tape-write erosion is the brake" silently includes the copier erasing itself. ATOMIC also
  *manufactures* the individuality that the heredity ontology presupposes (B §0.4). Under ATOMIC the ontology is valid
  partly *by construction*.

**Runaway bistability** (no single-founder run between depth 22 and 161, out of 630; A §6.1).
- A supercritical branching process either dies within a few generations or saturates the field within about
  log(256)/log(m) generations, which is tens of epochs.
- After saturation, depth accrues from within-family turnover for the remaining ~1,900 epochs. The gap is the distance
  between "died early" and "saturated early, then accrued".
- Intermediate depths need an intermediate absorbing state, and none exists.
- **Revealed:** the gap is not a mystery threshold. It is the difference between the extinction regime and depth-after-
  saturation. Predictions:
  1. runaway depth should scale with (T_end − t_F) × τ_F;
  2. the gap should close when turnover is suppressed (the cb7f regime), or when several families slow saturation. Many
     founders (k >= 2) partly fill it (A §6.1).

**Core conservation** (C-CORE 23/24/52/53).
- **[P]** The static Jacobian of the 7ae3 founder, with zero context and random partners, gives essential positions
  {2, 22, 23, 24, 34, 43, 45, 46, 52, 53}.
- Mean final founder retention in the 27 C-CORE runaways is **0.42** at essential positions against **0.10** elsewhere.
  Spearman(E, retention) is 0.29 over 64 positions.
- The four core positions are both essential *and* opcode-immune to OPERAND mutation, and they are the top four retained.
- Positions 2, 22, 34, 43 and 46 are essential against random partners but *not* retained (0.04-0.14). The extended core
  (48, 42, 33) is retained but not essential in this context.
- **Revealed:** purifying selection acts on essentiality *in the realized partner and context distribution*, and after
  takeover that distribution is the family itself (SELF re-supplies the phase). The ontology predicts that E_x measured
  against family partners and family-carried contexts will fit retention far better than the zero-context E_x does (§5).

**Zero-specialization and self-poisoning.**
- The context set 𝒞_x contains the origin π = 0, because HL = 0 is the half-start at offset 0.
- A BC = 0 copier advances its own phase by Δ = count mod 128.
- It is "poisoned" unless Δ ≡ 0 or it re-sets its phase. The 16000006 forensic's period-2-3 cycles (E §1.3) and "copies
  after k = 0, 2, 5" are phase orbits.
- **Revealed** (**[P]** table in §1.6): state-robustness can be pure arithmetic. The slice budget (tier S 220, M 300,
  L 360) is a hidden heritable-geometry parameter.
- "ZERO-specific rescue" (C-ZERO-SPECIFIC 26/48 vs CONST 2/48) is phase-origin rescue. CONST 0x5A puts L at phase 90 for
  every site.

**The minimal 3-byte copier `1E 40 E5`.**
- In the old terms it is a trivial "environment-scaffolded replicator".
- In the new terms **[P]** it is a tape operator "copy half 0 → half 1" with:
  - specification 3 bytes;
  - heredity capacity **61 bytes** (T = 1.0 at positions 3-63);
  - image dimension 1.
- At side 1 it imports its partner. Its BASE offspring mean against random partners is about 0.5·2 + 0.5·0.1 ≈ 1.05, which
  is barely critical. Its ATOMIC mean is about 1.4.
- **Revealed:**
  - "Replicator" is a property of the triple (content, side, phase), not of the content.
  - A trivial specification can carry a high-capacity channel, so "trivial replicator" and "rich heredity" are orthogonal.
  - Every tape-anchored copier is equally a replicator of *whatever sits at the other side*.

**Internalization (C-A3).** In the new terms, a family evolves toward a **closed context set** (Q8). The 16000006 triplet
`LD DE,3200` (0x3200 ≡ 0 mod 128) is literally a phase reset of the destination.
- In 8/8 events, state-freedom follows takeover (L >= 0.5 first; E §6.1). The ontology says why: selection on closure only
  has traction once the family's own carried contexts dominate the context distribution its content meets. Before
  takeover, contexts are set by soup contents and closure pays little.
- **Revealed:** the conditional rate (8 of 11 runaways) is the natural unit, and the rarity lives in P_est.

**Compartment segregation** (state-free genomes never appear both inside and outside L; E §6.1).
- Under occupancy, one family holds the field at any time. Variants appear in whichever family occupies it, because that
  family supplies nearly all of the content, contexts and trials.
- **Revealed:** segregation is a corollary of the attractor structure (a single dominant family), not a lineage-level
  regularity that needs an explanation.

**Material turnover** (founder bytes 3-33%).
- A promoted "child" is the donor's *transmitted window*, plus up to 10% residue from the victim's previous content, plus
  mutation.
- **[P]** Three examples:
  - cb7f's products differ from cb7f at positions 61-63 in 38/38 products, because those positions are never copied and
    stay residue;
  - 7ae3's position 0 is never transmitted;
  - only 17/38 of 7ae3's products are exact.
- **[P, toy]** In 7ae3 seed 3, label occupancy reaches 256/256 while the number of sites that are >= 0.9 founder-like falls
  from 51 at epoch 25 to 0 by epoch 100.
- **Revealed:** label/content divergence is a generic, immediate consequence of Φ plus a 0.9 threshold plus mutation. It is
  not a special finding about NPE lineages.

**Transient events** (4/8 C-A3 events hold no free genome at 2000).
- Closure variants have no guaranteed m advantage inside a family whose contexts are already family-set, for example when
  members that run SELF re-supply the phase. Where the advantage is small, closure drifts.
- **Revealed:** persistence is predicted by m(free) − m(non-free) *measured inside the realized family field*. Nobody has
  computed this.

---

## 4. Which rulers and endpoints are malformed, and what replaces them

| current ruler | defect under this ontology | replacement |
|---|---|---|
| `max_causal_replication_depth` (L3/L4, "runaway") | Mixes establishment, within-family turnover, and P-11 chain breaks. It is world-level, and after takeover it rises only through turnover (cb7f 8/8 at 163-1,053 events, depth 4-6) | O_F(t) and t_F (Q9) for establishment; τ_F for turnover; certification reported separately as a per-edge rate |
| `anc0` share / "founder-descended" | A label moved by a threshold rule; content-blind (13-25% founder bytes) | O_F keyed on content membership; material flow Q10, with F8's planted positive and non-parental-founder null |
| Predecessor "birth" | A threshold slice of a continuous rewrite; 0/400 random-random rewrites are promoted, yet 78.5% of halves change | the byte-event graph (P7): per-interaction transfer counts by motif (copy, paint, hijack, residue); promotion kept only as a label |
| P-11 | Construction at the *recorded* context; painters pass; authorship goes to the EXEC context | κ over enumerated contexts (Q1, Q7), plus the Jacobian T and E (Q5), plus closure (Q4); EXEC ≠ owner reported as hijack |
| COMPETENT (fresh-state, zero registers, blank partner) | One point in phase space; misses anti-zero converters (c2a8 0.00 vs 0.81); inflated by zero padding | μ(𝒞_x) over the full 128×128 phase grid, with random-passenger controls |
| STATE_FREE (two fixed vectors), single-k self-state | Samples a periodic orbit at arbitrary phases; the two rulers disagree | closure index under G_x (Q8); Δ and orbit period |
| Whole-genome fidelity >= 0.9 | Inflated by low-complexity content (NOP-padded copier "state-free" 0.60 vs 0.00) | identity on the transmitted, information-bearing positions; information-weighted fidelity |
| S1-S5 stage chain | Stages are not nested (D U5) because they mix label, certificate and screen | occupancy stages: first conversion; O_F > k/N; t_F; closure onset |
| "Erosion" readouts; the ATOMIC contrast | Composite: self wrong-side import, hijack, partner writes | η split by EXEC motif; ATOMIC relabelled as a *quantizing* W |
| X-RUNAWAY `causal_descendant_share` | Already mislabelled (A W7) | O_F |

---

## 5. New measurements the ontology demands

**Static, from existing data or cheap VM calls (seconds to minutes):**

1. **A map atlas of the 51k-genome corpus** (`p2/delegates/corpus/corpus.json`). For a sample, compute κ, ρ, η, m under
   BASE and ATOMIC, P_est, Δ, μ(𝒞_x), closure, and the Jacobian (specification size and capacity). Then:
   - test whether P_est predicts per-donor establishment in the implanted panels, where donor identity dominates the outcome
     (D U4: all CONST/RANDOM successes come from 4 of 16 donors);
   - test whether μ(𝒞_x) and closure predict SELF_POISON and STATE_FREE labels (X-DD-SELFSTATE 18/18 and 11/23;
     SELFLOCATION 3/179 vs 74/143).
2. **Δ arithmetic on real donors.** Predict poisoned or robust from the copy count mod 128 and SELF or immediate phase
   resets. Validate on `q3_reset.json` `carried_states` and on bridge `founder_ages` (D, unmined series), where phase orbits
   should appear as copy ages clustered at orbit returns.
3. **EXEC-motif audit of recorded births.** Use the X-CERT-BREAK W1/W3 births, the 34 Archaeon replay births and
   AN3/AN8/TH-003. Classify each birth as copy, paint, hijack or residue from `prov`/`prov_lit` plus an EXEC trace.
   Prediction: the "victim-magnet" events (B U1: 100/240) are mostly hijacks of the founder's own code.
4. **Jacobian against realized partners.** For the 27 C-CORE runaways, re-derive E_x with the partner ensemble drawn from
   end-state family genomes and with family-carried contexts, then refit retention. Genomes are needed; X-CORE-TIME has
   only frequencies, so this needs a replay snapshot, which is cheap.
5. **The painter index T for the 57 P-11 survivors, the ancestry-replay children and the 8 C-A3 event genomes.** This is
   CVT-R's question asked on Φ, with EXEC separated.

**Needing (small) new runs:**

6. **Replays with occupancy logging** (O_F, τ_F, t_F per epoch):
   - cb7f under ATOMIC: this is the decisive test of "takeover without depth";
   - 7ae3 BASE vs ATOMIC;
   - C-A3 events vs non-events.
7. **A slice-budget dose** (220 / 256+k / 300 / 360) with fixed genomes. The ontology predicts a *non-monotone*,
   arithmetic pattern of self-poisoning and establishment (robust when count ≡ 0 mod 128). The heredity ontology predicts
   nothing specific.
8. **A tape-length dose** (2n = 128 vs 192 with n fixed, or offset halves). This changes the phase modulus, so that
   Δ-robust genomes become poisoned and vice versa. It is also the clean version of WP-7 tape rotation.
9. **Planted-motif invasion.** Plant `1E 40 ED B0` with random passengers at k founders and estimate P_est under BASE and
   ATOMIC against the Q3 prediction. This is a calibration of the whole ontology on a specimen whose map is known exactly.
10. **A ZERO-world (always-scaffolded) arm for C-A3.** This was already requested (F §5.2). In map terms it is the arm where
    closure has no payoff, so closure variants should arise at the mutational base rate and not sweep.

---

## 6. Where the two ontologies predict differently, and what I checked

All checks are **[P]**. They are read-only, on the cells' own slice and ops mask, and total about 95 s of CPU.

**D1. The establishment probability is computable from Φ.** CHECKED, AGREES.
- The heredity ontology treats establishment as an empirical lottery p, found over roughly 10 experiments.
- The map ontology predicts it from single interactions: 7ae3 ATOMIC GW survival **0.49-0.52**, against **0.52** observed
  (109/208 pooled).
- It also predicts BASE descendants to be near-critical (m 0.98), consistent with the observed cessation and a 3.5%
  runaway rate.
- **Caveats:**
  - GW assumes random partners and ignores mutation;
  - "survival" is not identical to depth >= 20;
  - a single genome and a single cell were tested.

**D2. Founder loss at the first pairing.** CHECKED, SAME ORDER.
- Predicted P(founder overwritten at epoch 1) = ½ · P(overwritten | side 0) = **0.18-0.21**. The side-0 sample gave 0.41 in
  zero context, and an earlier 64-partner sample gave 0.61, which would give 0.30.
- Observed in X-TICKET: 36/128 = **0.28** (A §6.2), which "no experiment named".
- The map ontology names it: side-0 hijack. The prediction is roughly right, somewhat low in the larger sample.

**D3. The "victim-magnet" is the founder's own machine.** CHECKED, CONFIRMED.
- **Old ontology:** the founder is overwritten by a *non-anc0 donor*. On this reading, knocking out the founder's copy
  bytes should not stop it being overwritten.
- **New ontology:** it predicts the opposite.
- **Result:** 39/64 side-0 overwrites; **34/39** vanish when the founder's half is randomized, and **30/39** vanish when
  only SELF+LDIR (23, 24, 52, 53) are zeroed.
- **Implications:**
  - Authorship, the lineage label and "donor" are assigned to the wrong party in these events.
  - The "descendant" that takes the site is not itself a copier: 0/20 convert at side 0, and 2/20 at side 1.

**D4. Self-poisoning and state-robustness are phase arithmetic.** CHECKED on synthetic donors, CONFIRMED.
- Copy count 256 gives 16/16 carried conversions. Counts of 251-260 (other than 256) and 296-298 give 1/16, except for one
  stray.
- The heredity ontology attributes robustness to internalized register initialization. This result shows robustness can
  come with no initialization at all.
- **Not yet checked:** real corpus donors (item 2 in §5).

**D5. cb7f: "never establishes / capped near 6" vs "establishes nearly always, depth blind".** PARTLY CHECKED.
- Map statistics: cb7f converts at 0.84-0.95 from side 1 in *both* zero and random contexts. Its products convert again at
  gen 2 (mean 0.83). Under ATOMIC it is never overwritten at side 0, so the predicted P_est is close to 1.
- World data: 8/8 ATOMIC runs have 163-1,053 P-11 events, a copy in *every* run, yet depth is 4-6.
- Toy process (256 sites, 300 epochs, 3 seeds): cb7f takes over in **3/3** (label occupancy 243-252/256), with *predecessor*
  depth 24-50. 7ae3 takes over in 1/3.
- **Reading:** the world's ceiling at 6 is plausibly a certification and turnover artefact of the depth ruler, not a failure
  to establish.
- **Decisive test:** one ATOMIC replay of cb7f with occupancy logging. It needs a world run, which I did not do.

**D6. Label/content divergence follows from Φ alone.** CHECKED IN TOY, CONSISTENT.
- In the toy's 7ae3 takeover, label occupancy is 256/256 while sites >= 0.9 founder-like fall to 0 by epoch 100.
- The toy has no splice, no niches and no z8taint. X-CONTENT's 13-25% is therefore the expected outcome of a map with a 0.9
  threshold and residue, not a discovery about lineages.

**D7. Essentiality predicts conservation.** CHECKED, PARTIAL.
- Essential positions retain 0.42 against 0.10 elsewhere. The C-CORE four are the top four retained. Spearman is 0.29.
- The zero-context Jacobian misses the extended core (48, 42, 33) and over-calls 2, 22, 34, 43 and 46.
- This is the ontology's own refinement: essentiality must be measured against the *realized family field* (§5 item 4).
  It is an open prediction.

**D8. Low-complexity inflation of competence and state-freedom.** CHECKED, CONFIRMED.
- The NOP-padded minimal copier converts 0.60 from random contexts; with random passengers it converts 0.00.
- **Implications:**
  - Every competence or state-free reading on low-DOM genomes needs a random-passenger control.
  - Near-homopolymers (4931, 0x36; the 0x36 "family" of 27/29 replay children) read as converters for the same reason.

**D9. The panel's "never copy" donors are field scramblers.** OBSERVED, NOT PREDICTED BY EITHER ONTOLOGY.
- 9 panel donors keep their own half at 0.56-0.94 in zero context but at <= 0.03 in random contexts. They are e160, 08b4,
  9cba, 1935, 0365, aaa8, 2c45, ffa6 and dd30.
- A block op fired with random pointers rewrites up to 300 bytes of a 128-byte tape.
- In a CARRIED world these contents are operators that *randomize the field*, including themselves. Their prevalence is a
  field-level mutation rate that the heredity ontology counts only as "erosion".
- **Next step:** measure it per epoch from replay (§5 item 6).

**Where the new ontology might lose.**
- It says nothing yet about *which* family wins when several coexist (k >= 2 fills the depth gap, A §6.1).
- Q3 ignores the frequency dependence of Φ, so it will fail when partners are relatives before t_F.
- My toy establishes 7ae3 in 1/3 runs, which is noisy.
- The strongest counter-evidence would be a replay in which O_F stays below ½ but depth exceeds 20. A founder-less
  runaway (A §6.11) could be one; it needs an occupancy replay.

---

## Summary (10 lines)

```
1. On PAIR_TAPE nothing is born or dies: 256 fixed SITES carry CONTENT (bytes) and CONTEXT (registers); a stochastic pair MAP rewrites contents.
2. "Organism/birth/anc" fuse site, context and a label moved by a 0.9 threshold; C9-D14, FF-11, X-CONTENT, X-MAT are all this seam splitting.
3. New primitives: site, content, pointer-phase context (only 7 address bits matter), map Phi, write-back rule W, byte EXEC/WRITE/READ graph.
4. New quantities: conversion kernel, retention/import, offspring law m and P_est, closure, transmission Jacobian (spec vs capacity), phase set and advance.
5. [P] Phi alone predicts 7ae3 ATOMIC establishment 0.49-0.52 vs 0.52 observed (109/208); BASE descendants m 0.98 (subcritical -> cessation).
6. [P] "Victim-magnet" events are hijacks: 39/64 side-0 overwrites; 34/39 vanish without 7ae3's half, 30/39 without its SELF+LDIR bytes.
7. [P] Self-poisoning is arithmetic: copy count = 0 mod 128 gives 16/16 carried conversions, neighbours 1/16; slice budget is hidden geometry.
8. [P] Depth conflates takeover with turnover: cb7f copies in 8/8 ATOMIC runs (163-1,053 events) at depth 4-6; toy takes over 3/3.
9. Malformed: depth, anc0, predecessor birth, P-11, COMPETENT, STATE_FREE, whole-genome fid; replace with occupancy, kappa over the phase grid, Jacobian, closure.
10. Cheapest decisive next steps: corpus map atlas vs per-donor outcomes; one cb7f ATOMIC occupancy replay; a slice-budget dose.
```

Output: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/adversaries/ADVERSARY_2_ONTOLOGY.md`
