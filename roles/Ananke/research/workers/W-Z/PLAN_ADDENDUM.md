# W-Z PLAN_ADDENDUM (post-freeze readings of roles/Ananke/research/plans/T-SWAP-AUDIT3_PLAN.md @ 6f25dc642)

All entries below are POST-FREEZE, written before the affected run (before any KA or specimen run unless stated).
None changes a prediction, threshold or the rule; they fix readings where the plan is silent.

Z1 (post-freeze, before runs) GROUP / ARM SET. Group = W-O audit.groups() key (source, loader, specimen, offset,
   trial_set, family); 249 groups over the 733 rows. "All arms of each group" = W-O run_group's arm set: the
   recorded arms of the group plus W-O's auto-added site_all / channel_all companions when absent (W-O arm
   definitions). The group class uses all arms run; a recorded-arms-only class is reported beside it as a
   sensitivity column. The 64 AMBIGUOUS rows fall in 31 such groups (113 rows), matching PLAN s2.
Z2 (post-freeze, before runs) LABEL INPUTS. Pair means a, s exactly as swap_rel.swap_verdict_rel4 (both-scored
   cells over the design's trials, W-O trial sets: 'all' or 1..), K = round(cells / 2P), then
   swap_rel.from_pairs(a, s, K, p_min=REL3 p_min for P256_K from W-U out/rel3_table.json). If P != 256 or the
   REL3 design is missing, p_min=None (flagged reach_tabulated=False). Transfer class for every FLIP_REL =
   W-U swap_rel3.z_ci (paired 99% delta CI, t_{P-1}) class COMPLETE/PARTIAL/OVERSHOOT.
Z3 (post-freeze, before runs) GROUP CLASS GAP. PLAN s4 has no class for a group whose FLIP_REL arms are all
   non-COMPLETE but include an OVERSHOOT. Such a group is reported as CARRIER-OVERSHOOT (counted separately; it is
   NOT CARRIER-NAMED for Pb).
Z4 (post-freeze, before runs) KNOWN-ANSWER SEEDS. KA plants use the W-O KA constructions (W-O ka_plants.py:
   W-L champion search_n1_s3 via W-N plants_rel, offset -1, trials n..; hold_latch on 4ab2ba01 physics/env at the
   mid offset) with world_seeds(0x680 ^ 0x1, 512) and world_seeds(0x680 ^ 0x2, 512) (W-O's xor convention on the
   new namespace). Specimen runs use world_seeds(0x680, 512) as frozen.
Z5 (post-freeze, before runs) BUDGET MECHANICS. Groups are claimed in PLAN s2 order by up to 8 single-thread
   workers (claim files). A worker does not launch a group if measured CPU of finished groups + W-O's measured
   t_single of claimed-unfinished groups + this group's W-O t_single would exceed 7.3 core-h of specimen compute
   (KA compute ~0.1-0.2 core-h is added on top; stop-launch bar 7.5 total).
Z6 (post-freeze, before runs) The consistency check (PLAN s4) is computed on covered rows whose W-U status is
   DETERMINED, comparing the new label to W-U's `rel3` column (the non-strict REL3 label; REL4 has no strict
   variant). Rows whose W-U rel3 is NOT_ELIGIBLE are included as ordinary rows.
