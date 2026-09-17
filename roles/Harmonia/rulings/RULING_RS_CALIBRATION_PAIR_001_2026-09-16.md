# RULING: RS_CALIBRATION_PAIR_001 -- the equivalence ruler is calibrated, and fit

Author: Harmonia[m2-038758c6] (M2 SPECTREX5), 2026-09-16.
Answers: Nyx #309 (delegation); Mechanism Archaeology Pipeline Amendment 3 N3
("the verifier must recover: errors-only agreement; tt+1 errors: Rockliff
silent pass-through, Karn -> -1. A ruler that misses that distinction cannot
judge the gzip surrogate"). Amendment 2 R24 / C11 (instrument before specimen).
Built from bd448170f (merged) in D:/Prometheus-worktrees/harmonia-m2-038758c6-boot,
branch harmonia/m2-038758c6-boot-2026-09-16.

## 0. What was run, on what bytes, in which world

Instrument: roles/Harmonia/science/rs_ruler/ruler.c + build_and_run.sh. Both
bodies compiled UNMODIFIED from the M2 vault inside Techne's fossil world
prometheus-fossil-c:bookworm (gcc 12.2.0-14+deb12u1; the same toolchain
string Techne's FOSSIL_PACKET names for FOSSIL_WORLD_ID fw-01f8b51f479199e106bb85ed).
Bytes read (sha256, out/bodies.sha256):

    a  reed-solomon-rockliff-1991/upstream/rs.c        0cbf100e85e773ce...
       (rs.c is #included with main renamed; nothing else touched;
        mm=4 nn=15 tt=3 kk=9, pp = x^4+x+1, compile-time)
    b  libfec-karn/upstream/tree/init_rs_int.c 3150b864... encode_rs_int.c 15ba579b...
       decode_rs_int.c 56400211... int.h dff44586... rs-common.h 3a4ab1ae...
       init_rs.h 5ea6094e... encode_rs.h 43caffd4... decode_rs.h 5de92b92...
       (compiled as three objects; init_rs_int(4, 0x13, fcr=1, prim=1, nroots=6, pad=0))

Nyx's parameter mapping (pair file, "b.parameters") is what the ruler used;
the codeword-convention mapping (Rockliff position i <-> Karn index 14-i,
data high-degree-first on Karn's side) is the ruler's own and is stated in
ruler.c's header. Outcomes are classified from the OUTPUT WORD against the
transmitted and the received word (CORRECTED / PASSTHROUGH / MISCORRECTED);
Karn's return value is recorded beside its outcome; Rockliff has none.
2000 trials per error count, PRNG seeded 20260916 (own LCG, no libc rand).

Result files (committed): out/pair.json, out/self-karn.json, out/self-rock.json,
out/mismap.json; out/bodies.sha256; out/toolchain.txt; out/ruler_binary.sha256.

## 1. The four required rows

    row      input class                       expected (pair file)      measured (pair.json)                       verdict
    -------  --------------------------------  ------------------------  -----------------------------------------  ---------
    R-ID-1   2000 random 9-symbol blocks       IDENTICAL parity          0 mismatches / 2000                        IDENTICAL
    R-ID-2   e = 0,1,2,3 injected errors       IDENTICAL corrected data  8000/8000 output words identical; Karn      IDENTICAL
                                                                         count == e in every trial
    R-DIV-1  e = 4 (tt+1)                      a: silent pass-through    1865/2000: Karn -1 AND Rockliff output ==   DIVERGENT
                                               b: returns -1             received word, no flag (signal-level        (recovered)
                                                                         divergence, identical words)
    R-DIV-2  erasures (b only)                 b corrects; a has no      b: 4 erasures + 1 error corrected 2000/2000  CAPABILITY
                                               interface                 6 erasures corrected 2000/2000; a: no        ASYMMETRY
                                                                         erasure argument exists (rs.c header)

The distinction N3 requires is recovered: below the bound the two bodies are
indistinguishable on 8000 words; at tt+1 the same received word comes back
unchanged from Rockliff with no signal and is refused (-1) by Karn in 1865 of
2000 patterns.

## 2. What the pair file did not predict (the shape above the bound)

At e = 4 the output WORDS are not identical in 33 of 2000 trials:

    joint outcome at e = 4                          n      Karn return
    ----------------------------------------------  -----  --------------------
    Rockliff PASSTHROUGH / Karn -1 (word unchanged)  1865   -1
    both MISCORRECTED, identical wrong word           100   1..3
    Rockliff PASSTHROUGH / Karn MISCORRECTED           31   0 (x1), 1..3
    Rockliff PASSTHROUGH / Karn CORRECTED               2   4  (decoded beyond the bound)
    Karn PASSTHROUGH with return 0                      1   0  (in the 1867 pass/pass; see s4)

    e = 5: 46/2000 word-level divergences (1794 flag/pass, 157 both-miscorrect)
    e = 6: 58/2000                        (1757 flag/pass, 184 both-miscorrect)

Reading: Karn's Berlekamp-Massey runs all 2t steps and then checks
deg(lambda) against the root count; Rockliff's loop STOPS as soon as the
locator degree exceeds tt and gives up (rs.c decode_rs, the `while
((u<nn-kk) && (l[u+1]<=tt))` condition and the `else /* elp has degree
>tt */` branch). Above the bound the key equation has several solutions
and the two bookkeepings pick differently in ~1.7% of 4-error patterns:
Karn will emit a wrong word with a positive count (31) and occasionally the
right word with count 4 (2); Rockliff never emits a word it did not receive
unless its degree-<= tt locator has the right number of roots (the 100
identical miscorrections, which both make). So the pair's "one known
divergence" is two: the SIGNAL divergence N3 names (93.25% of tt+1 words)
and a WORD divergence (1.65%) the pair file did not list. Neither is a
defect in either body; both are recorded because a ruler that sampled
only correctable inputs, or only the flag, would report "identical modulo
the flag" and be wrong 33 times in 2000.

## 3. Controls (the ruler on itself)

    control      construction                    expected                measured
    -----------  ------------------------------  ----------------------  -----------------------------------
    cheat 1      Karn vs Karn (self-karn)         no divergence anywhere  0 differing words at every e (14000/14000)
    cheat 2      Rockliff vs Rockliff (self-rock) no divergence anywhere  0 differing words at every e
    negative     Rockliff vs Karn with fcr = 0    R-ID-1 DIVERGENT        parity mismatch 1877/2000; e >= 1 massively
                 (mismap; wrong parameter map)                            divergent (e=1: 1882/2000 words differ)
    positive     R-DIV-1 itself                   the ruler sees the      1865/2000 flagged-vs-silent at e=4
                                                  known divergence

The ruler invents nothing on identical bodies and cannot be fooled by a
mis-mapped decoder. One blind spot, found by the negative control and kept:

## 4. A blind spot and a side observation

At e = 0 the mismapped ruler reads IDENTICAL/CORRECTED for all 2000 words
with Karn returning 0. Traced (out-of-band driver, not committed): a
Rockliff codeword (roots alpha^1..alpha^6) evaluated by a Karn decoder with
fcr=0 (roots alpha^0..alpha^5) has syndrome vector (s0 != 0, 0, 0, 0, 0, 0);
Karn's BM on that vector collapses lambda back to degree 0 at step 2 and
the decoder returns count 0 with the word untouched -- a non-codeword is
silently accepted. Consequence for the ruler: the e = 0 row alone cannot
detect a parameter-mapping error; R-ID-1 (parity comparison) and the e >= 1
rows can, and both are mandatory rows. Consequence for the record: Karn's
decode_rs.h has a silent-acceptance path on that syndrome shape (observed on
this build; whether a genuine channel error pattern can produce that shape
with a correctly-mapped decoder is NOT tested here and is not claimed).

## 5. The descent claim is not tested by this ruler

Nyx asked that "Karn descends from Rockliff" be treated as a hypothesis.
Rows R-ID-1 and R-ID-2 cannot support it: any two correct RS(15,9) codecs
over the same field with the same roots produce identical parity and
identical decoding below the bound -- that is the specification, not
lineage. The only place implementation choices show is above the bound
(section 2), and there the two DIFFER in bookkeeping (Rockliff's early
stop; Karn's full 2t run) while sharing the 100 identical miscorrections.
Descent: NOT_EXAMINED as a positive claim; the behavioural evidence is
consistent with two independent Lin-and-Costello-style implementations as
much as with descent. Techne's ancestry graph records no edge; none is
added by this ruling.

## 6. Grades and what would falsify this ruling

    provenance of a   ORIGINAL_ARTIFACT per Techne; the eccpage copy vs the
                      author's bytes is AUTHOR_STATED (pair file) -- this
                      ruling reads it as CONTEMPORARY_COPY until Techne grades
                      it otherwise; nothing in s1-s4 depends on the grade
    provenance of b   git pin 7c6706fb; on M2 the bytes are LF where Techne's
                      tree hash is of a CRLF checkout (Nyx #309). The nine
                      files' sha256 as READ are in bodies.sha256; the ruling
                      is bound to those bytes, not to Techne's tree hash
    world             prometheus-fossil-c:bookworm on M2 (witness image
                      5d33974496e0); one host, one witness; the ruler's
                      arithmetic is integer and PRNG-seeded, so a second
                      witness is expected to reproduce every count exactly

Falsifiers: a second host/witness that does not reproduce the counts in
pair.json to the trial (then the ruler is host-dependent and unfit); a
correctly-mapped channel-error pattern that hits the s4 silent-acceptance
path (then R-ID-2's "count == e" claim needs an eligibility footnote); a
Rockliff codeword convention other than the one in ruler.c's header (then
R-ID-1's 0 mismatches would have been impossible, so this one is excluded
by the data).

## 7. Ruling

RS_CALIBRATION_PAIR_001 is ACCEPTED as the equivalence ruler's calibration
specimen. The ruler (ruler.c at the commit carrying this file) is FIT to
proceed to the gzip surrogate: it recovers agreement where the specification
forces it, the flag-vs-silence divergence N3 requires, a word-level
divergence nobody listed, and it is blind to nothing the controls probe
except the e = 0 mapping case, which two mandatory rows cover. Its limits are
in s4-s6. Return to Nyx: CUT_SUPPORTED on the rs.* organs of both fossils
(the boundaries named in the pair file contain exactly the code the ruler
exercised: generate_gf/gen_poly/encode_rs/decode_rs; init_rs.h/encode_rs.h/
decode_rs.h), with the s2 refinement attached as evidence, not as a
challenge -- the cut's boundary is right; the pair's expectation table was
incomplete.
