# F - LINEAGE RECOVERY REPORT

## What was recovered

The **complete line of descent of the case-study population through the origin
of EQU**, extracted from supplementary section IV and parsed to
`artifacts/lineage_of_descent.jsonl`.

    records                112
    phylogenetic depth     0 - 111
    fields per record      pd, born (update), functions (9 bits), fit
                           (relative to immediate parent), genome, len
    ancestor (pd 0)        rucavccccccccccccccccccccccccccccccccccccutycasvab
                           50 instructions, 0 of 9 functions
    T_EQU                  pd 111, birth update 27450
    genome length          50 min, 61 max
    functions at pd 111    6 of 9

Every genotype on the successful lineage is therefore available as an exact
string over the verified 26-letter alphabet. For the purposes of a *static*
accessibility analysis this is a complete specimen.

## What was NOT recovered, and it is the binding constraint

**No contemporary genotypes.** The supplementary publishes the line of descent
only. It contains no organism that was alive at the same update and did not
lead to EQU.

The directive's first scientific target (section 5) is a *matched* comparison of
`g_succ(t)` against 3-5 `NON_EQU_DESCENDANT_CONTROL` genotypes at the same
generation with matched fitness, genome length and task count. **None of those
controls exists in any artifact recovered in this pass.**

Three routes to controls, in order of fidelity:

1. **Recover the myxo repository from the Wayback Machine.** The supplementary
   states that the full line of descent and "functional-genomic arrays for all
   345 genotypes" live there. If population dumps or `detail-*.spop` files were
   also posted, contemporaries come with them. Snapshot confirmed to exist
   (timestamp 20211122232656, status 200); retrieval blocked this session by
   rate limiting. **Cheapest and highest fidelity.**
2. **Recover 2003-era source and configuration via SourceForge CVS**, then
   re-run to generate contemporaries. This yields controls but they are
   RECONSTRUCTED, not historical, and every UNSPECIFIED parameter in E becomes
   an assumption.
3. **Use the lineage against itself** - compare `g_succ(t)` to `g_succ(t')` for
   t' far from EQU. This needs no new artifact but it is **not** a matched
   control and would answer a different, weaker question.

## An unexplained discrepancy, recorded rather than resolved

The supplementary says the distributed line of descent contains **345
genotypes**; the table printed in the same document contains **112**, ending at
EQU. The likely reading is that the printed table is truncated at the origin of
EQU (its own title says "through the origin of the EQU function at step 111")
while the distributed file continues past it. That is a plausible reading, not
a verified one, and it is flagged as a live archaeology question rather than
assumed.

## Fidelity caveat on the parse

`lineage_of_descent.jsonl` is a DERIVED artifact: its hash is of our text
extraction, not of a historical file. The regex requires a well-formed row
(depth, update, nine bits, fitness, genome) and silently skips malformed lines,
so a systematic extraction failure would present as missing rows rather than as
an error. 112 consecutive depths 0-111 with no gaps is evidence against that,
but the parse has not been validated against an independent rendering of the
PDF.
