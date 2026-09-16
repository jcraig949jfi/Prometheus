"""Cut: reed-solomon-rockliff-1991 (ancestry-aware, Stage A DEEP-by-size; SOURCE_READ rs.c 1-200 (header, tables, generator, encoder,
decoder through Berlekamp init) and the decoder's own 20-line description; 312-406 main skimmed). 406 lines, one file, 1989/1991.
Organ names copy libfec-karn's rs.* names where the mechanism is the same, because Karn's decode_rs.h descends from this file:
a KNOWN-IDENTICAL pair for calibrating the recurrence ladder (an R5 that is also an ancestry edge)."""
from nyx.atlas.author import Cut

S = "vault:reed-solomon-rockliff-1991/upstream/rs.c"
c = Cut("reed-solomon-rockliff-1991", mode="ANCESTRY_AWARE", inspected=["rs.c 1-200 read; 200-311 (Chien/Forney) skimmed; main skimmed"], evidence=[("SOURCE_READ", S)],
        note="the atlas's calibration pair: this and libfec-karn::rs.* are the same five mechanisms by descent; a Stage E wind tunnel that cannot call them R5 is broken, and one that calls libfec's Viterbi equally close to them is fooled by the domain label")

gf = c.organ("rs.galois_field_log_antilog_tables_from_a_primitive_polynomial", human_name="generate_gf (GF(2^4) here; mm/nn/tt/kk compile-time)", status="ACCEPTED",
    mechanism="a shift register seeded from the polynomial coefficients pp[] builds alpha_to[] and index_of[] with -1 as the log of zero (Karn: A0 = nn); elements are carried in INDEX form (recd[] holds logs) so multiplication is an add mod nn",
    input="pp[mm+1]", output="alpha_to[], index_of[]", state="global tables", update="once", evidence_ref=S + ":44-77", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="generate_gf",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

gp = c.organ("rs.generator_polynomial_from_consecutive_roots", human_name="gen_poly", status="ACCEPTED",
    mechanism="gg = prod_{i=1..2tt} (x + alpha^i) built by repeated multiplication in index form (Karn: fcr and prim parameters generalise the root sequence; here fixed at 1, 1)", input="the tables", output="gg[nn-kk+1]", state="global", update="once",
    evidence_ref=S + ":78-95", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="gen_poly",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE"})

en = c.organ("rs.systematic_encoding_by_lfsr_division_by_the_generator", human_name="encode_rs", status="ACCEPTED",
    mechanism="for each data symbol from the top: feedback = log(data ^ bb[top]); shift bb up one, XOR in alpha^(gg[j] + feedback) at each tap; identical in shape to libfec's encode_rs.h (which adds the memmove and the UNNORMALIZED branch)", input="data[kk]", output="bb[nn-kk]", state="bb", update="per symbol",
    evidence_ref=S + ":96-123", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="encode_rs",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "CONSTANT", "update_topology": "SWEEP"})

sy = c.organ("rs.syndrome_evaluation_by_horner_at_consecutive_roots", human_name="decode_rs syndromes", status="ACCEPTED",
    mechanism="s[i] = sum_j recd[j] * alpha^(i*j) for i = 1..2tt by direct summation in index form (Karn: Horner's rule); a non-zero syndrome sets syn_error", input="recd[nn] (index form)", output="s[1..2tt]", state="none",
    evidence_ref=S + ":150-160", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the syndrome loop",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "output_topology": "DECISION"})

bm = c.organ("rs.iterative_locator_polynomial_from_syndromes", human_name="decode_rs Berlekamp iteration (Lin and Costello's table form)", status="ACCEPTED",
    mechanism="the textbook table: for each step u keep the elp, its degree l[u], the discrepancy d[u] and u - l[u]; when the discrepancy is non-zero find the earlier row q maximising u_lu and form the new elp from the old plus a shifted, scaled copy; NO erasure seeding (the header says erasures are 'not hard to adapt'); if deg(elp) > tt the block is declared uncorrectable and the information symbols are output as received",
    input="s[]", output="elp, its degree", state="the elp table (2tt+2 rows)", update="2tt steps", assumptions=["errors only; at most tt of them"],
    failure_landscape="by the header: beyond tt errors the data is passed through uncorrected with NO flag ('can be returned as error flags ... if desired') -- Karn returns count = -1", evidence_ref=S + ":161-230", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the Berlekamp block",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "SUPERLINEAR", "update_topology": "SWEEP", "failure_mode": "CORRUPTS"})

ch = c.organ("rs.exhaustive_root_search_over_the_field", human_name="decode_rs Chien search", status="ACCEPTED",
    mechanism="substitute alpha^i for i = 1..nn into the elp with a running register per coefficient; roots give inverse locations; a root count different from deg(elp) means more than tt errors -> pass through uncorrected", input="elp", output="root[], loc[], count", state="reg[]", update="nn steps",
    evidence_ref=S + ":231-270 (skimmed)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the root-search loop",
    coverage={"input_topology": "VECTOR", "output_topology": "SET", "state_amount": "CONSTANT", "update_topology": "SWEEP"})

fo = c.organ("rs.error_magnitudes_from_evaluator_over_locator_derivative", human_name="decode_rs error values (z polynomial)", status="ACCEPTED",
    mechanism="form z(x) from the syndromes and the elp, evaluate at each inverse root, divide by the product of (1 + root_i * root_j) terms (the derivative in product form, as in Lin and Costello; Karn uses omega and the odd-power derivative), and XOR the value into recd", input="s[], elp, roots", output="corrected recd[]", state="z[], err[]", update="per root",
    evidence_ref=S + ":271-311 (skimmed)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the error-value loop",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT"})

c.reject("main() (build a codeword, inject errors, decode, print)", reason="EFFECT_FROM_ENVIRONMENT", evidence=S + ":312-406 -- Techne's harness runs it; the error injection is the world")
c.reject("global variables / index-form bookkeeping (-1 for zero)", reason="GENERIC_LANGUAGE_MECHANICS", evidence="the header's own apology; Karn's rewrite localised them", note="the -1 sentinel vs Karn's A0 = nn is a representation difference with identical behaviour -- a Stage D identifier-permutation test can confirm")
c.reject("'Reed-Solomon codec' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="six functions with separate state; the same finding as libfec-karn")

c.edge(gf, gp, "feeds"); c.edge(gp, en, "feeds"); c.edge(gf, sy, "feeds"); c.edge(sy, bm, "feeds"); c.edge(sy, bm, "gates", note="syn_error"); c.edge(bm, ch, "feeds"); c.edge(bm, ch, "gates", note="deg > tt -> give up"); c.edge(ch, fo, "feeds"); c.edge(ch, fo, "gates", note="count != degree -> give up")

c.pressure("independent_symbol_corruption_with_a_fixed_redundancy_budget",
    condition="the same pressure recorded on libfec-karn: symbols are corrupted independently; 2tt parity symbols buy tt corrections; the receiver knows the code", resource_or_constraint="parity fraction; decoder arithmetic in a small field",
    failure_condition="more than tt errors -> uncorrected output passed through silently (this body) or flagged (Karn)", world_punishes="ignoring the algebraic structure", world_rewards="syndrome -> locator -> roots -> values",
    observable_consequence="corrected symbols vs injected errors (main's own demo)", vacuity_condition="a noiseless channel", trivial_shortcuts="repetition",
    cheat_control="a decoder given the error positions (erasures) must correct 2tt of them; this body cannot use them -- the erasure capability is exactly what Karn added", cost_class="CPU-scale", source_evidence="the header; main", purpose="PURPOSE: a teaching/reference codec (Rockliff 1989)")

c.ancestry("predecessor_of", "libfec-karn", note="Karn's decode_rs.h / encode_rs.h / init_rs.h keep Rockliff's variable names (alpha_to, index_of, genpoly, the Lin and Costello table) and add erasures, parametrisation and Horner syndromes; asserted from reading both bodies, not from Techne's record")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["the Chien and error-value blocks are skimmed, not read line by line", "the silent pass-through on decoding failure is a reading claim; a Stage C run with tt + 1 injected errors would show it directly"],
          note="every function of rs.c is assigned")
c.save(state="DEEP")
