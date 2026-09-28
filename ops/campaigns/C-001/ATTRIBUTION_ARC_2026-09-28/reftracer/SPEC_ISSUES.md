# SPEC_ISSUES -- reference BEE tracer vs ANCESTRY_PREREG_v4 (s1, s2.1-2.2, s4.1)

Written by the isolated reference worker from the v4 text plus the frozen `vm.py` / `world.py` (git 16fc6c2a; sha256
prefixes 2536b1ac / 5b985241 match the s3 pins). World: r025144 (VM_COPY, L=64, SHARED, budget 256, entry 0).
For each item: what the text says, why it is not enough, and what `ref_tracer_bee.py` does. "CHOICE n" tags in the code
point here. Items marked **[agreement risk]** are the ones where I expect another conforming tracer to legitimately differ
from mine, which would count against the 99.5% agreement threshold of s4.3.

---

## A. Scope of the dependence sets

**CHOICE 1 -- "whole-execution" ctrl_deps: up to the store, or up to the end?** **[agreement risk]**
s1.3 says ctrl_deps is "the whole-execution PC label" and "the base labels of the condition inputs of every conditional
EVALUATED". Two readings:
(a) the Denning PC label *at the time of the store*, never popped (i.e. "whole-execution" is contrasted only with the
    post-dominator pop); or
(b) the union over every conditional evaluated anywhere in the interaction, including after the last store to the locus.
(a) misses implicit flows through *non*-execution after the store: a later branch on X that skips an overwrite makes the
final byte depend on X. (b) is sound for that, but makes ctrl_deps identical for every locus of the interaction.
I implement (b) as `ctrl_deps` and export (a) as `ctrl_deps_at_store` so either can be compared. Unwritten loci also get
(b) (whether they were written at all depended on the path).

**CHOICE 2 -- exec_deps scope.** Same question: every fetched byte of the whole interaction (primary, `exec_deps`) vs.
those fetched before the store (`exec_deps_at_store`). Same choice as CHOICE 1. With (b), exec_deps is per-interaction, so
Q6 ("entity composition of exec_deps in window-writing interactions") is well defined, but per-locus exec_deps carries
no per-locus information. **[agreement risk]**

**Secondary post-dominator scope not implemented.** s1.3 names "post-dominator-scoped ctrl_deps" as secondary but gives no
construction. In BEE the code is self-modifying (any byte can be opcode or operand depending on the PC, bytes can be
rewritten during the run, LDIR/COPYALL overwrite running code), so a static CFG / post-dominator tree does not exist for
the program *as executed*. Options: (i) static CFG of the pre-state tape with linear decode from the entry, (ii) a
dynamic post-dominator on the executed trace, (iii) per-instruction CFG rebuilt at each fetch. The text does not say
which; Q8r "in both ctrl scopes" is therefore not reproducible as written. I export only the store-time label as a
diagnostic, not a post-dominator scope.

**CHOICE 3 -- are CONSTANT labels members of dependence sets?** **[agreement risk]**
s1.2 calls CONSTANT/CONTEXT "FOREIGN-STRUCTURAL (never de-identifying; reported)", and s1.3 says the budget "is recorded
by a flag, not by a label", while COMPUTED drops CONSTANT bases. So it is unclear whether e.g. a RESET pointer S puts
(CONSTANT, reset) into addr_deps, or a RESET C puts it into ctrl_deps. I drop CONSTANT from all three sets (consistent
with COMPUTED flattening and the budget rule) and report the CONSTANT kinds met in conditions/fetches/pointers per
interaction in `structural_seen`. Identification is unaffected either way; agreement on "the three dependence sets"
(s4.3) is affected.

**CHOICE 5 -- what is a "pointer label", and do addr_deps propagate transitively?**
s1.3: "addr_deps: the union of the pointer labels of the store AND of every load that contributed to the value".
Unstated:
- whether the pointer label is the pointer register's *data label bases* only, or also the pointer's own addr_deps
  (pointer loaded from memory through another pointer). I use both (full dependence of the pointer value).
- whether "every load that contributed" is transitive through memory (value loaded via S1, stored via T1, reloaded via
  S2, stored via T2 -> {S1,T1,S2,T2}) and through computation (ADD A,B where B was loaded via S). I make it transitive:
  every value carries an addr set; computations union them; stores add the store pointer; loads add the load pointer.
- the ctrl_deps of a condition and the exec_deps of a fetched byte: "base labels of the condition inputs / fetched byte".
  I include the input's addr set too (a byte placed by an input-dependent pointer and then executed does depend on the
  input). A strictly "data-label bases only" tracer will differ. **[agreement risk]**

**Implicit increments of pointers.** COPYALL writes to T+i reading S+i (i = 0..L-1) without changing S/T. The address
T+i is computed from T and a constant; I take the pointer label as T's (S's) full dependence (CHOICE 11). LDIR/LDI's
internal S++, T++, C-- are treated like INC_S/INC_T/DEC_C (COMPUTED_FROM, see CHOICE 4).

## B. Label algebra gaps

**CHOICE 4 -- COMPUTED / COMPUTED_FROM corner cases.** **[agreement risk]**
- INC/DEC of a CONSTANT (RESET register, e.g. LDIR's C or S counting from RESET 0; INC A from RESET): the text says
  COMPUTED_FROM(label), but K32 expects "pointer/count labels CONSTANT". I return (CONSTANT, "computed"), so a count
  from RESET stays structural. Keeping the original kind (e.g. "reset") or producing COMPUTED_FROM(CONSTANT reset) are
  both defensible; the kind string affects nothing but agreement.
- A computation whose inputs are all CONSTANT (e.g. ADD A,B on two RESET registers; immediate operands never qualify,
  they are ENTITY): "COMPUTED(flattened base labels, CONSTANT bases dropped)" literally gives COMPUTED(empty set).
  I return (CONSTANT, "computed"). Both are "new material" under s2.2 and neither is ENTITY, so only agreement differs.
- INC/DEC of a COMPUTED or COMPUTED_FROM value: COMPUTED_FROM(COMPUTED(s)) vs COMPUTED(s), and COMPUTED_FROM of
  COMPUTED_FROM(x): I flatten (keep the input label unchanged). The text does not say.
- DJNZ decrements B: treated as DEC B (COMPUTED_FROM). INC_C/DEC_C set Z: Z's label is COMPUTED(bases of C).
- Flags: the text never says flags carry labels, only "zero RESET registers and flags" are CONSTANT. I give Z and CF a
  label + addr set: Z/CF after ADD/SUB/XOR/AND/OR/INC/DEC/SHL/SHR/CP = COMPUTED(bases of the inputs). CP A,n uses the
  operand byte's label. Instructions that don't touch a flag leave its label alone (e.g. XOR does not change CF).
- SHL/SHR are register-only and no-operand but NOT bijective -> COMPUTED (the text's bijective list is INC, DEC).
- SWAP A,B and LD r,r' are moves (labels travel with values).
- Immediate operands used as a jump target (JP n, JR d, taken or not) are not "values"; they enter exec_deps only. A
  data-dependent jump target (e.g. from self-modified code) thus never enters ctrl_deps -- only exec_deps. I think this is
  intended (exec_deps covers it) but the text does not say.

**CHOICE 7 -- result-independent idioms in BEE.** BEE has no XOR A,A / SUB A,A instruction; the only candidates are
XOR A,B / SUB A,B / CP A,B when A and B hold the same byte. Deciding "same byte" by value would be value alignment
(forbidden, s1.4). I use label identity: if A and B carry the identical ENTITY/INPUT MOVE label they necessarily hold the
same byte (each pre-state byte has a unique label; moves preserve the value), so the result is 0 (and Z=1, CF=0) regardless
of that byte -> (CONSTANT, "idiom") with an empty addr set. For COMPUTED/COMPUTED_FROM labels identical labels do NOT
imply equal values, so no idiom. AND A,B / OR A,B with identical labels return A unchanged; the text says "everything
else that computes -> COMPUTED", so I keep COMPUTED (a MOVE would be more precise). A tracer that never applies the idiom
in BEE would label such bytes COMPUTED({x}). **[agreement risk]**

**CHOICE 9 -- the input region beyond len(inputs).** world.py writes only `inputs[:16]` (COND_MULTI/ECHO/... give 1-2
inputs) into 0xE0..; the remaining input-region bytes are zero, and IN (ip < 16) reads *memory*, not the input list. So
IN #3..#16 read zero bytes that are not "input byte k" and not "IN beyond 16 reads". I label them (CONSTANT, "scratch")
(fresh zero scratch). A tracer that labels every IN_BASE+k as (INPUT, k) would put INPUT labels on them.
Also: the input region is writable (a program can overwrite it before IN); IN then returns whatever label the byte has
now, not (INPUT, k). The text's "input byte k -> (INPUT, k)" is read as a pre-state label.

**IN / OUT hidden counters.** "Their labels are the ctrl_deps at each IN/OUT." I use the store-time PC label (reading (a)
of CHOICE 1 -- the end-of-execution label is not known yet at the IN/OUT). The IN counter is used as the load pointer
(its label enters the value's addr set); the OUT counter as the store pointer for mem[OUT_BASE + n]. The IN `ip < 16`
guard and the OUT `< 16` guard have the counter as their condition input, whose label *is* the PC label, so adding it to
ctrl_deps is a no-op. Note: OUT is not a `W()` write in the VM (not in Trace.writes), but s1.2 requires its store to update
labels; I do.

**IN beyond 16.** Value 0 -> (CONSTANT, "in_exhausted"), empty addr set (no load happens).

**Region-exit halt / budget.** In SHARED the region is the whole space: the region test never fails; its condition input
is the PC itself (label = PC label) -> no-op. The budget test (main loop and inside LDIR) is (CONSTANT, "budget") ->
flag `budget_end` only (and "budget" is not in structural_seen). COPYALL adds L//8 steps without a budget check inside,
so steps can exceed the budget; mirrored.

**"LDIR/COPYALL C==0 exit".** The frozen COPYALL has NO C==0 exit (it always copies exactly L bytes and ignores C). Only
LDIR evaluates C==0 (after each decrement, every iteration). The text's listing of COPYALL here is wrong for BEE; I add
nothing to ctrl_deps for COPYALL. Also, in the frozen VM, COPYALL with allow_copyall False is a NOP (not applicable to
r025144).

## C. Initial labels / persistence

- **orig_id.** "(ENTITY w, i, orig_id)" -- orig_id is never defined. I read it as "the origin id from the persisted
  per-organism label vector" (inherited labels "count to their carrier entity", s2.2). Within one interaction the tracer
  takes it as a parameter (`w_orig`, `o_orig`, or per-address `pre_labels`); identification only uses the entity role.
  If persisted labels (e.g. an inherited MUTATION or COMPUTED label) were meant to *replace* the ENTITY label at the next
  interaction, then "Inherited labels count to their carrier entity" contradicts s2.1 (a locus whose pre-state label is
  inherited COMPUTED could never be rule-identified). I use fresh ENTITY labels for every pre-state locus, keeping orig_id
  as a tag only. **[agreement risk]**
- **EMPTY partner.** Window bytes -> (CONSTANT, "empty"). Other scratch (2L..0xDF, 0xF0..0xFF) -> (CONSTANT, "scratch").
  Registers and flags -> (CONSTANT, "reset").
- **MUTATION** labels never arise inside one vm.execute (mutation is applied between ticks) and are not modelled.

## D. Performer / identification

- **performer** = "the material label of the STORE instruction's opcode byte". "Material label" = the data label of that
  byte at fetch time (I use exactly that). If the opcode byte itself is COMPUTED/INPUT/CONSTANT (code written during the
  interaction), the performer is not an entity; I then add no performer entity to the allowed set in s2.1. The class
  "INPUT-or-scratch-performed" (s2.2) does not say what happens with a COMPUTED(entity) opcode byte or an opcode byte
  copied from the occupant into the writer's tape (label (o, k) sitting at a w address: performer = o by material,
  w by location -- I use material, per s1.4 "code location" is forbidden).
- **Multiple stores to one locus.** The performer, addr_deps and at-store snapshots are those of the LAST store (the one
  that determined the final byte). Earlier stores do not count. The text does not say; a union over all stores would
  over-taint but is arguably what "the store" means for Q1.
- **OUT as performer** -- OUT stores never reach the window (0xF0..0xFF), but the bytes they create can be copied into it
  by a later COPYALL/LDIR; performer is then the copy instruction, not OUT.
- **Identification of unwritten loci.** s2.1 identification is defined for loci; per-birth identifiability counts
  "written loci". I compute `rule_identified` for every locus, but an unwritten occupant locus (o, j) has no performer,
  so the executing organism's own exec_deps/ctrl_deps (always w) make it NOT rule-identified (selftest T4, loci 8..63).
  Literal, but meaningless; callers should restrict to written loci. The text should say identification is only over
  written loci.
- **Performer exemption and ENTITY other than w/o.** In BEE SHARED only w and o exist, so the "no ENTITY other than
  {data-label entity, performer entity}" clause only bites when data label is o and performer w (or vice versa) and the
  third entity... cannot exist. Therefore for BEE SHARED the ENTITY clause reduces to: if data label is w and performer is
  w (self-performed), any o in ctrl/addr/exec de-identifies; if data is o and performer is w, or data w and performer o,
  nothing entity-based can de-identify. That is a big asymmetry between classes, worth noting for the per-class
  thresholds.
- **Birth-existence deps** (s1.3) -- I compute the union of the PC label, the store-pointer sets of window stores, the
  dependence of every final child byte, and every occupant locus (child != occupant compares the whole tape). Not a
  requested deliverable; included for completeness. "n_written" is the number of *distinct* window addresses in
  Trace.writes (OUT excluded, W-writes with an unchanged value included).

## E. s4.1 flip test

**FLIP-1 -- the path criterion omits LOAD addresses (the test fails correctly-labelled loci).** **[important]**
The path is "(pc, opcode) fetch trace and the store-address sequence". Data-load addresses are not in it. Counter-example
(selftest T1): the COPYALL replicator `LD S,0; LD T,64; COPYALL; HALT`. Window locus 1 is correctly labelled (w, 1) (it
is the S operand byte, moved). Flipping bit b of (w,1) changes S (a load pointer) but neither the fetch trace nor the
store addresses; the child byte at locus 1 becomes w[1+2^b], not 0^2^b -> FAILED. The same happens for any locus whose
source byte is also used as a load pointer, a loop count that does not change the store sequence, etc. With the literal
text this is counted as a tracer failure (and feeds the FAILED <= 1% threshold) although the label is correct and the
dependence is fully disclosed in addr_deps. I implement the literal test (default) and a `strict_path=True` variant that
also requires the data-load address sequence to be unchanged (then T1 locus 1 is INAPPLICABLE). Recommendation: add load
addresses to the path, or declare a bit INAPPLICABLE when the flipped byte's label appears in the locus's addr_deps.

**FLIP-2 -- "(X, j)" addresses.** The flipped pre-state byte for (ENTITY w, j) is address j and for (ENTITY o, j) address
L+j. For an EMPTY window there is no o. The text does not state the mapping (obvious, but a SEPARATED/NPE port differs).

**FLIP-3 -- what "unchanged path" is compared to.** The (pc, opcode) trace and store addresses are not exposed by the
frozen vm.execute; they come from the shadow executor, whose final memory, outputs, steps, halted flag and write map are
asserted equal to the frozen VM on every flipped re-run. A harness that instruments differently (e.g. counts the LDIR
per-byte steps as fetches, or excludes OUT stores from the store sequence) can classify bits differently. I include OUT
stores and every per-byte LDIR/COPYALL store in the store sequence, and count LDIR/COPYALL as ONE fetch.

**FLIP-4 -- predicted value.** "The predicted moved value" is taken as pre[(X,j)] XOR bit. That is well defined only
because every pre-state byte has a unique label, so a MOVE label (X,j) always holds exactly pre[(X,j)]; if persisted
labels were ever reused across addresses (see section C, orig_id) the prediction would be ambiguous.

**FLIP-5 -- which loci.** "every rule-identified locus with an ENTITY MOVE label". "MOVE label" is not defined; I take
it as data label type ENTITY (not COMPUTED_FROM of an entity). Written-only by default (identification is over written
loci); an unwritten occupant locus (o, j) passes trivially.

**FLIP-6 -- birth / write suppression under the flip.** If a flip keeps the path, writes and births are unchanged by
construction, so there is no suppression case here (unlike Q8c). A flipped bit that changes the birth test only via
`child != occupant` cannot change the path either. Fine, but the text does not say whether a flip that makes the child
equal to the occupant (no birth) counts.

**FLIP-7 -- per-class thresholds depend on the class of the flipped run?** No: the class is the baseline's. Assumed.

**FLIP-8 -- the flip test cannot detect over-tainting nor missing ctrl labels**, as s7 says; but it also cannot certify
the ctrl-only case K31 (selftest T15: a byte recreated by branching on w40 has label (w, 13) = the operand of the chosen
LD A,n; flipping w40 changes the path, INAPPLICABLE; flipping w13 CONFIRMS). A tracer that labels such a byte (w, 40)
("MOVE-labelling") would get INAPPLICABLE on every bit (path changes) -> not FAILED. So K31 is only rejected by the
fixture expectation, not by s4.1.

## F. Other textual problems

- s1.3 "per child locus" dependence sets vs. a PC label that is interaction-wide: see CHOICE 1/2.
- s1.2 "every store updates labels (OUT, per-byte sequential LDIR/COPYALL, and harness stores included)" -- in BEE SHARED
  the harness stores are the pre-state construction (tapes, inputs[:16]); there are no in-interaction harness stores.
- s1.2 "OUT's 16-output guard is a conditional": its condition input is the OUT counter, whose label is the PC label, so
  it never adds anything. The mutation-testing item "ctrl omits the ... OUT guard" therefore cannot be detected in BEE
  SHARED (it is a semantic no-op), same for the region-exit halt. Both are only meaningful if the counter/PC labels are
  distinct objects, which the text rules out.
- s1.1 "register labels reset at the second entry" (SEPARATED) -- not applicable (r025144 is SHARED).
- s2.1 "Per class: flip coverage >= 50%": with the literal FLIP-1 test, copy programs whose code bytes lie in the copied
  region give INAPPLICABLE for code-byte loci (any bit flip of an opcode changes the fetch trace) -- expected and fine,
  but coverage also depends on how many loci are code; a replicator of mostly-code tapes may fall below 50%.
- s2.2 "new material ... CREATED IN THIS INTERACTION": with CHOICE 4 the only labels created are COMPUTED/COMPUTED_FROM/
  CONSTANT(computed|idiom|in_exhausted); CONSTANT(reset|scratch|empty) are pre-existing structural labels -- are they
  "created in this interaction"? Presumably yes (they are not inherited) but the text does not say.
- Pinning: s3 gives "vm 2536b1ac" etc. These are sha256 prefixes of the file contents, not git blob ids (the git blob of
  vm.py is 91d8516c). Worth stating, since `git show <id>` on them fails.

## G. VM facts a tracer must mirror (not spec defects, but easy to get wrong)
- LDIR tests C==0 AFTER the decrement, so C = 0 on entry copies up to 256 bytes (budget permitting); each byte costs a
  step and the budget is re-checked inside the loop. COPYALL copies exactly L bytes sequentially (reads see earlier writes:
  the overlap chain, selftest T14), leaves S/T/C unchanged, and costs 1 + L//8 steps with no inner budget check.
- XOR/AND/OR/ADD/INC/DEC do not touch CF; SUB/SHL/SHR/CP set CF. INC_S/INC_T set no flags; INC_C/DEC_C set Z.
- OUT writes memory directly (not via W, so not in Trace.writes / n_written) and only while fewer than 16 outputs exist.
- IN reads mem[IN_BASE + ip] (the current memory, possibly overwritten), for ip < 16, else 0.

## H. What was verified
- `trace_interaction` asserts, on every call (including every flip re-run), that final memory, outputs, steps, halted and
  the W-write map equal those of the frozen `vm.execute` (loaded from `frozen_vm_16fc6c2a.py`, sha256 prefix 2536b1ac
  checked at import). Passed on 3000 + 300 random programs (random bytes / random defined opcodes, occupant or EMPTY,
  1-2 inputs) and on all hand programs.
- `selftest.py`: 15 hand programs (replicators via COPYALL / LDIR / register loop, K32 overlap, K34 IN/OUT past 16, K35,
  XOR idiom, occupant-performed, input-guarded, input-derived code and pointer, EMPTY partner, overlap chain, K31-style
  control-flow recreation): 0 expectation failures; flip test on 114 fuzz loci: 0 FAILED. The one FAILED in the
  selftest is deliberate (FLIP-1, T1 locus 1).
- Not verified: agreement with any other tracer (by design I have not seen one); the preserved births file has no tapes,
  so no production pre-state was traced.
