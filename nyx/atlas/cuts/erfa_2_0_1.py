"""Cut: erfa-2.0.1 (ancestry-aware, Stage A COARSE; SOURCE_READ atciq.c in full, nut00a.c 159-180 and 1880-1920 (series loop), dat.c
(grepped structure), t_erfa_c.c 25-125 (validators); the 247-routine list read by name; plan94 / epv00 / moon98 by size only).
Essential Routines for Fundamental Astronomy (the SOFA fork), 257 C files."""
from nyx.atlas.author import Cut

S = "vault:erfa-2.0.1/upstream/tree/erfa-2.0.1/src/"
c = Cut("erfa-2.0.1", mode="ANCESTRY_AWARE", inspected=["atciq.c", "nut00a.c (series loop)", "dat.c", "t_erfa_c.c (vvd/viv)", "routine list (247 names)"],
        evidence=[("SOURCE_READ", S + "atciq.c"), ("SOURCE_READ", S + "nut00a.c"), ("SOURCE_READ", S + "dat.c"), ("SOURCE_READ", S + "t_erfa_c.c")],
        note="247 routines, but a handful of mechanism SHAPES: trigonometric series over fundamental-argument polynomials, rotation-matrix algebra, fixed correction pipelines, table lookups with validity windows, and a two-part date representation; the library keeps every superseded model side by side")

ps = c.organ("trigonometric_series_over_integer_combinations_of_fundamental_arguments_summed_smallest_first", human_name="nutation / planetary / lunar series (nut00a: 678 + 687 terms; plan94, epv00, moon98 same shape)", status="ACCEPTED",
    mechanism="each term is (integer multipliers of 5 fundamental arguments -> arg = fmod(sum n_k * F_k, 2pi)) and coefficients (sin, t*sin, cos for longitude; cos, t*cos, sin for obliquity); the loop runs from the LAST (smallest) term to the first so rounding error accumulates on the small terms; two tables (luni-solar, planetary) are summed separately then combined; the result is scaled from 0.1 microarcseconds to radians",
    input="t (Julian centuries since J2000)", output="dpsi, deps (radians)", state="none (the tables are constants)", update="none", assumptions=["the MHB2000 tables are truth; the argument polynomials are those of IERS 2003"],
    fitness_value_in_ancestor="the accuracy of every frame transform rests on these series", evidence_ref=S + "nut00a.c:159-180,998,1852,1880-1990", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the series loops of nut00a/nut00b/nut06a/plan94/epv00/moon98 (only nut00a read)",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "order_sensitivity": "SENSITIVE", "representation_sensitivity": "SENSITIVE"})

fa = c.organ("fundamental_arguments_as_polynomials_in_t_reduced_modulo_a_turn", human_name="fal03 falp03 faf03 fad03 faom03 (and the inline polynomials in nut00a 1870-1885)", status="ACCEPTED",
    mechanism="each argument (mean anomalies, elongation, node) is a quartic in t with arcsecond coefficients, reduced mod 1296000 arcseconds then converted to radians; nested Horner form", input="t", output="an angle", state="none", update="none",
    evidence_ref=S + "nut00a.c:1870-1885; fa*03.c by name", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the fa*03 routines",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE"})

jd = c.organ("two_part_julian_date_carried_through_every_interface", human_name="(date1, date2) convention", status="ACCEPTED",
    mechanism="every epoch argument is a pair of doubles whose sum is the Julian Date; the caller chooses the split (JD and 0, MJD form, date and fraction) so the fractional day keeps its full precision instead of being lost after 2.4 million; time-scale conversions return the same shape",
    input="two doubles", output="two doubles", state="none", update="none", assumptions=["IEEE double; a 53-bit mantissa cannot hold a JD to microseconds in one number"],
    fitness_value_in_ancestor="the precision pressure made concrete in a representation", evidence_ref=S + "atciq.c (astrom carries it), utctai.c, taitt.c, dat.c:70-87 (djm + fd)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the argument convention of the whole library",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE", "uncertainty": "POINT"})

rm = c.organ("rotation_matrix_algebra_for_frame_changes", human_name="rx ry rz rxr rxp trxp c2s s2c ir tr cr pxp pdp ... and the bias-precession-nutation matrices (pnm06a, bp06, c2i*)", status="ACCEPTED",
    mechanism="frames are related by 3x3 rotation matrices built from Euler angles (rx/ry/rz apply an elementary rotation in place), composed (rxr), applied to vectors (rxp) or transposed (trxp); spherical <-> Cartesian conversions (c2s, s2c) bracket the vector algebra; a frame transform routine is a product of these",
    input="angles, vectors", output="matrices, vectors", state="none", update="none", evidence_ref=S + "atciq.c:10 (eraRxp astrom->bpn); rx.c, rxr.c, c2s.c by name", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the vector/matrix routine family (~40 files)",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE"})

ch = c.organ("fixed_pipeline_of_astrometric_corrections_over_a_precomputed_context", human_name="eraAtciq (ICRS -> CIRS): pmpx -> ldsun -> ab -> rxp(bpn) -> c2s; eraApci13 builds the context", status="ACCEPTED",
    mechanism="apply proper motion and parallax (eraPmpx), light deflection by the Sun (eraLdsun), stellar aberration (eraAb), then rotate by the bias-precession-nutation matrix and convert to spherical; every step reads a precomputed eraASTROM context (observer position/velocity, matrix, Sun direction) built once per epoch by eraApci13 so many stars can be transformed cheaply",
    input="ICRS coordinates + proper motion + parallax + radial velocity; eraASTROM", output="CIRS right ascension / declination", state="eraASTROM (per epoch)", update="context per epoch; transform per star",
    fitness_value_in_ancestor="the catalogue-to-sky pipeline the record's failure condition speaks of", evidence_ref=S + "atciq.c:1-16; apci13.c (name and size)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="atciq + the at*/ap* family",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "update_topology": "SWEEP", "memory": "SUMMARY_STATISTIC"})

ls = c.organ("leap_second_table_with_a_pre_1972_drift_formula_and_a_validity_horizon", human_name="eraDat", status="ACCEPTED",
    mechanism="a compiled-in table of (year, month, delta-AT) changes since 1960 (extendable at run time via eraDatini / erfadatextra); find the latest entry not after the date; for the 1960-1972 entries add a linear drift term (djm - epoch) * rate; return a status: warning if the date is more than 5 years past the table's last year (IYV + 5), error before 1960 or for a bad date",
    input="calendar date + fraction", output="TAI - UTC in seconds, status", state="the table (static + optional extension)", update="none (the table is data)", assumptions=["someone updates the table when the IERS announces a leap second"],
    fitness_value_in_ancestor="the one place the library's truth expires on a calendar", failure_landscape="UNKNOWN by run; by reading: dates after the table's horizon silently use the last value with only a status warning",
    evidence_ref=S + "dat.c:6-87", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="dat.c + erfadatextra.c",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "temporal_horizon": "UNBOUNDED", "failure_mode": "DEGRADES", "hidden_state": "ASSUMES"})

ts = c.organ("time_scale_graph_of_pairwise_conversions_by_constant_table_or_series_offsets", human_name="taitt tttai taiutc utctai tttdb tdbtt tcgtt ttut1 ... (24 routines)", status="ACCEPTED",
    mechanism="each edge of the scale graph (TAI, TT, UTC, UT1, TDB, TCB, TCG) is a routine adding a constant (TT - TAI = 32.184 s), a table value (UTC via eraDat, with the leap-second day-length rule in utctai), a caller-supplied value (UT1 - UTC) or a series (TDB - TT via eraDtdb, a ~1000-term series of the same shape as organ 1); each preserves the two-part date",
    input="(date1, date2) in one scale", output="(date1, date2) in another", state="none", update="none", evidence_ref=S + "taitt.c, utctai.c, dtdb.c by name; utctai.c 191 lines", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the 24 two-letter-scale routines",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE"})

c.reject("t_erfa_c.c / vvd / viv (the validation program)", reason="OTHER", evidence=S + "t_erfa_c.c:25-98 and 247 t_* functions comparing to compiled-in reference values within absolute or fractional tolerances", note="an INSTRUMENT (the record's ORACLE); the atlas records that this fossil ships its own oracle -- rare in the sample")
c.reject("247 routines as 247 organs", reason="OTHER", evidence="the routine list groups by shape: series (nut*, plan94, epv00, moon98, dtdb, s00/s06, xy06), fundamental arguments (fa*03), matrix/vector algebra (~40), astrometry pipelines (at*, ap*), time scales (24), calendar/angle formatting (a2af, d2dtf, cal2jd...)", note="formatting routines (a2af, a2tf, d2tf, dtf2d, cal2jd, jd2cal) not given an organ: representation conversions with no state")
c.reject("'the IAU model' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the library keeps nut80 / nut00a / nut00b / nut06a and prec76 / pmat00 / pmat06 side by side; the human name changes with the standard, the machinery shape does not")
c.reject("autotools / meson build", reason="GENERIC_LANGUAGE_MECHANICS", evidence="configure, Makefile.am, meson.build")

c.edge(fa, ps, "feeds"); c.edge(jd, fa, "feeds", note="t from the two-part date"); c.edge(ps, rm, "feeds", note="nutation angles -> matrices"); c.edge(rm, ch, "feeds", note="bpn matrix in the context"); c.edge(ls, ts, "feeds"); c.edge(ts, ch, "feeds", note="epoch in TT/TDB for the context"); c.edge(ps, ts, "feeds", note="TDB - TT series"); c.edge(jd, ts, "transforms")

c.pressure("positions_must_be_right_to_a_part_in_1e9_over_centuries_using_64_bit_arithmetic",
    condition="a milliarcsecond error misplaces catalogue stars; the quantities span 2.4 million days and 1e-10 radians in the same computation", resource_or_constraint="IEEE double; the ordering of floating-point sums",
    failure_condition="a term off by 1e-9 (record)", world_punishes="single-number dates; summing large terms first; truncated series", world_rewards="split representations, smallest-first summation, long series with a published reference",
    observable_consequence="make check: 247 routines within tolerance of reference values", vacuity_condition="arcsecond-level needs", trivial_shortcuts="extended precision arithmetic (slower; the world may allow it)",
    cheat_control="a routine with the reference values compiled in must pass; if it passes with a perturbed constant (the record's entry point), the tolerance is too loose -- the fossil's own validation is the cheat control's mirror", cost_class="CPU-scale", source_evidence="record pressure / failure; nut00a loop order; the date convention", purpose="PURPOSE: fundamental astronomy for catalogues and observatories")
c.pressure("the_definition_of_truth_is_revised_by_a_standards_body_while_old_results_must_stay_reproducible",
    condition="the IAU replaces precession/nutation models every decade; results computed under an old model must remain reproducible and comparable", resource_or_constraint="one library serving all generations",
    failure_condition="silent drift when a model is swapped", world_punishes="a single 'current' model", world_rewards="coexisting versioned routines with the model in the name (nut80 / nut00a / nut06a)",
    observable_consequence="the routine list; the same transform under two models differs by a known amount", vacuity_condition="a frozen standard", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="the routine names", purpose="PURPOSE: same")
c.pressure("a_fact_about_the_world_that_is_announced_a_few_months_ahead_must_be_carried_as_data_with_an_expiry",
    condition="leap seconds are decided by the IERS; code compiled before the decision cannot know it; a result past the table's horizon is quietly wrong", resource_or_constraint="compile time vs the calendar",
    failure_condition="wrong TAI - UTC after the horizon", world_punishes="a table with no horizon", world_rewards="a table with a run-time extension hook and a dated validity warning",
    observable_consequence="eraDat's status code past IYV + 5", vacuity_condition="a world with no leap seconds", trivial_shortcuts="refuse dates past the horizon (the world may reward or punish this)",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="dat.c:77-78; erfadatextra", purpose="PURPOSE: same")

c.ancestry("forked_from", "IAU SOFA (the code's own headers)", note="not re-read from the record")
c.residue("PARTIALLY_EXPLAINED", ["plan94 / epv00 / moon98 / dtdb assumed to be organ-1-shaped from size and name only", "the matrix family and the astrometry family read from one routine each", "the calendar / angle formatting routines are unassigned", "nothing ran here; Techne's make check (t_erfa_c) is the executed evidence on M1"],
          note="seven shapes cover the 247 names; the claim that each name belongs to a shape is by name for ~230 of them")
c.save(state="COARSE")
