"""Cut: ssw-smith-waterman (ancestry-aware, Stage A COARSE; SOURCE_READ src/ssw.c 163-387 (query profile, sw_sse2_byte in full), 860-960
(ssw_align: 8->16-bit fallback, reverse pass, banded traceback, grepped); sw_sse2_word 388-589 assumed the 16-bit twin; banded_sw
590-784 not read). Farrar's striped SIMD Smith-Waterman as packaged by Zhao et al. (SSW library)."""
from nyx.atlas.author import Cut

S = "vault:ssw-smith-waterman/upstream/tree/src/ssw.c"
c = Cut("ssw-smith-waterman", mode="ANCESTRY_AWARE", inspected=["src/ssw.c 163-387, 860-960"], evidence=[("SOURCE_READ", S)],
        note="a 1981 dynamic programme re-cut for 16-lane 8-bit SIMD: the anatomy is the striping, the lazy-F correction, the saturating-arithmetic bias trick and the overflow fallback; the DP recurrence itself is unchanged")

qp = c.organ("query_profile_striped_so_lane_k_holds_query_positions_k_segLen_apart", human_name="qP_byte / qP_word", status="ACCEPTED",
    mechanism="for each residue type nt and each segment i, pack 16 bytes: the substitution score of query position i + segNum * segLen against nt, plus a bias to keep it unsigned; positions past the query end get the bias alone; the profile is indexed by the reference residue so the inner loop does one aligned load per segment instead of a table lookup per cell",
    input="query (numeric), substitution matrix, bias", output="n * segLen SSE vectors", state="none (built once per query)", update="once per query", assumptions=["16 lanes of 8 bits (or 8 lanes of 16 bits)"],
    fitness_value_in_ancestor="the striped layout is what makes the vertical dependency (F) rare enough to fix lazily", evidence_ref=S + ":163-186", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="qP_byte (qP_word twin)",
    coverage={"input_topology": "SEQUENCE", "output_topology": "MATRIX", "state_amount": "LINEAR_IN_INPUT", "representation_sensitivity": "SENSITIVE"})

sw = c.organ("striped_dp_column_sweep_with_saturating_unsigned_arithmetic_and_bias", parent=None, human_name="sw_sse2_byte inner loop (H, E, F recurrences)", status="ACCEPTED",
    mechanism="per reference position: shift the last segment's H left one lane (the diagonal dependency across the stripe boundary), then for each segment: H = max(H_diag + profile - bias, E, F), store; E = max(E - gapE, H - gapO); F = max(F - gapE, H - gapO); all in saturating unsigned 8-bit so negatives clamp to 0 (the local-alignment floor comes free from the arithmetic) and the bias keeps mismatch scores representable; two H buffers alternate",
    input="one reference residue, previous column H/E, profile", output="a new column H/E and a running column max", state="pvHStore, pvHLoad, pvE (segLen vectors each)", update="per reference residue x per segment", assumptions=["gap open and extend are constant per column", "scores + bias fit in 8 bits (else the fallback organ)"],
    fitness_value_in_ancestor="the whole throughput gain (record: 'millions of alignments')", evidence_ref=S + ":230-280", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the inner j loop of sw_sse2_byte",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "update_topology": "PARALLEL_ROUNDS", "stochasticity": "DETERMINISTIC", "order_sensitivity": "SENSITIVE"})

lf = c.organ("lazy_f_correction_loop_that_stops_when_no_lane_can_still_improve", parent=sw, human_name="Lazy_F loop", status="ACCEPTED",
    mechanism="after the segment sweep, F (a gap in the reference direction) was computed ignoring the dependency that wraps across lanes; shift F by one lane and re-sweep the segments, taking max(H, F) and re-deriving F, up to 16 times; exit early as soon as F - (H - gapO) is zero in every lane (movemask == 0xffff), i.e. no cell could still change; the comment records a fix taken from SWPS3 (no E update here, so an insertion cannot directly follow a deletion)",
    input="vF, the stored column", output="a corrected column", state="none", update="0-16 extra sweeps per column", assumptions=["F rarely propagates far, so the loop usually exits after one pass (the striping's premise)"],
    evidence_ref=S + ":281-297", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the k loop and its goto end",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "update_topology": "SWEEP", "recovery": "SELF_RESETS"})

mx = c.organ("running_maximum_with_end_position_capture_and_second_best_outside_a_mask", parent=sw, human_name="vMaxScore / vMaxMark / maxColumn / bests[1]", status="ACCEPTED",
    mechanism="the column max is folded into vMaxScore; when it changes, the whole H column is copied to pvHmax and the reference position recorded; after the sweep the read end is the lowest striped index holding the max; per-column maxima (maxColumn[]) let a second-best alignment be found outside a window of maskLen around the best; a 'terminate' score stops the sweep early (used by the reverse pass)",
    input="column maxima", output="best score, ref end, read end; second best", state="vMaxScore, vMaxMark, pvHmax, maxColumn[refLen]", update="per column", evidence_ref=S + ":298-387", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the tail of sw_sse2_byte",
    coverage={"input_topology": "STREAM", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "memory": "SUMMARY_STATISTIC"})

fb = c.organ("overflow_detected_by_saturation_at_255_triggers_a_16_bit_recompute", human_name="ssw_align: byte then word", status="ACCEPTED",
    mechanism="run the 8-bit sweep; if bests[0].score == 255 (saturated) and a word profile exists, rerun with the 16-bit lanes (8 per vector); if no word profile, the result is flagged; the record names this as the guarded hazard",
    input="the 8-bit result", output="a trusted score", state="none", update="per alignment", assumptions=["a true score of exactly 255 is treated as overflow (a false-positive recompute, never a wrong answer)"],
    evidence_ref=S + ":875-895", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the fallback branch of ssw_align",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "NONE", "failure_mode": "DEGRADES", "recovery": "RETRIES"})

rv = c.organ("start_position_by_rerunning_the_sweep_on_reversed_sequences_terminating_at_the_known_score", human_name="seq_reverse + sw_sse2_*(ref_dir = 1, terminate = score1)", status="ACCEPTED",
    mechanism="the forward sweep yields only the END of the best local alignment; reverse the query up to that end and sweep the reference backwards from the end, stopping the column loop as soon as a column reaches the known best score; that column is the alignment start; a lower score on the way back is flagged",
    input="score1, ends", output="ref_begin1, read_begin1", state="none", update="per alignment", evidence_ref=S + ":813-830,900-915", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="seq_reverse + the reverse call in ssw_align",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "NONE", "update_topology": "SWEEP"})

bt = c.organ("banded_scalar_dp_over_the_located_window_to_recover_the_path", human_name="banded_sw -> CIGAR", status="CANDIDATE",
    mechanism="once both ends are known, a scalar DP with traceback runs inside a band around the diagonal of the window (widening the band if the score is not reproduced -- inferred from the flag handling, not read) and emits the CIGAR", input="the window, score1, band_width", output="a CIGAR path",
    evidence_ref=S + ":590-784 (unread), 930-960", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="banded_sw",
    coverage={"input_topology": "MATRIX", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "memory": "FULL_HISTORY"})

c.reject("the Smith-Waterman recurrence as a separate organ", reason="CANNOT_BE_ISOLATED", evidence="H/E/F max-plus recurrences are the inner loop's arithmetic (organ 2); there is no scalar reference in the body except banded_sw", note="the 1981 algorithm is the ancestry; the executable boundary here is the striped sweep")
c.reject("sse2neon.h, the C++ / Python / JNI wrappers, kseq.h, main.c", reason="GENERIC_LANGUAGE_MECHANICS", evidence="src/ file list: bindings, a FASTA reader, a driver")
c.reject("sw_sse2_word as separate anatomy", reason="OTHER", evidence="same structure with 8 x 16-bit lanes, no bias needed (signed) -- assumed from the signature and the byte version; not diffed", note="a lane-width parameter")

c.edge(qp, sw, "feeds"); c.edge(sw, lf, "feeds", note="F carried out of the segment loop"); c.edge(lf, sw, "restores", note="corrected column"); c.edge(sw, mx, "feeds"); c.edge(mx, fb, "gates", note="255 -> word rerun"); c.edge(mx, rv, "feeds", note="score1 + ends")
c.edge(rv, bt, "feeds", note="window"); c.edge(fb, sw, "retries", note="16-bit lanes"); c.edge(qp, rv, "feeds", note="reversed profile")

c.pressure("millions_of_quadratic_alignments_must_fit_a_throughput_budget_on_wide_but_narrow_lanes",
    condition="each alignment is O(m n) cells; the hardware offers 16 parallel 8-bit operations but a serial dependency runs along both axes of the table", resource_or_constraint="SIMD width x lane precision; the vertical dependency",
    failure_condition="the scalar cost; or a layout whose dependencies serialise the lanes", world_punishes="lane-by-lane dependencies; scores that need more bits than a lane has", world_rewards="a layout where the dependency across lanes is rare (striping) and a cheap correction when it is not (lazy F)",
    observable_consequence="cells per second vs the scalar oracle (EMBOSS water, record)", vacuity_condition="one alignment", trivial_shortcuts="heuristic seed-and-extend (not the same optimum; the world must score exactness)",
    cheat_control="an aligner given the optimum in advance must report it at zero cost; if the world scores it equal to SSW on identical outputs without charging time, throughput is not measured", cost_class="CPU-scale", source_evidence="record pressure; the striped loop", purpose="PURPOSE: read mapping in sequencing pipelines")
c.pressure("narrow_arithmetic_saturates_silently_and_the_wrong_answer_looks_like_a_right_one",
    condition="8-bit lanes clamp at 255; a high-scoring pair returns 255 with no error", resource_or_constraint="lane width",
    failure_condition="a silently wrong optimum (record)", world_punishes="trusting the narrow result", world_rewards="treating the saturation value as a detector and recomputing wider",
    observable_consequence="the record's entry point: a very high scoring pair", vacuity_condition="scores always below 255", trivial_shortcuts="always use 16-bit lanes (half the throughput)",
    cheat_control="a pair whose true score is exactly 255 must still be recomputed; a world that never presents scores near the lane limit does not test this", cost_class="CPU-scale", source_evidence=S + ":875-895", purpose="PURPOSE: same")

c.ancestry("algorithm_from", "Smith & Waterman 1981; Farrar 2007 (striped); SWPS3 (the lazy-F fix, named in the comment at 281)", note="from the code's comments")
c.residue("PARTIALLY_EXPLAINED", ["banded_sw (traceback) unread", "the 16-bit twin assumed", "nothing ran; Techne's EMBOSS agreement oracle is on M1"],
          note="the forward SIMD sweep is fully read")
c.save(state="COARSE")
