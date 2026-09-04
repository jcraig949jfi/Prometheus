"""Append HC-R01 corrections to registries Q and R.

Sources: the neutral-network lane's final report, and two sibling-seat commits
this seat failed to read before dispatching lanes (elenchus/kashtan-alon-mvg
at 397dc307f, and the Ergon correction at c98598f47).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

Q_ADD = [
 {"specimen_id": "spec-parter-2008-facilitated-variation",
  "field": "systems biology / facilitated variation",
  "year": 2008,
  "source": "Parter, Kashtan and Alon, 'Facilitated variation: how evolution learns from past environments to generalize to new environments', PLoS Comput Biol; the load-bearing content is in Text S1 section 7, 'Complete characterization of the phenotypic neighborhood'",
  "substrate": "Boolean NAND logic circuits, 104-bit genome; plus an RNA secondary-structure model",
  "present_state_matching_available": None,
  "machinery_class_matched": True,
  "machinery_note": "goal schedules only; the mutation operator is held fixed across all arms",
  "identical_variation_operator": True,
  "history_differs": True,
  "future_distribution_measured": True,
  "future_distribution_how": "A-LOCAL AND EXHAUSTIVE. 'Neutrality was defined as the fraction of 1-mutant circuits that compute the same Boolean function as the wild-type.' The genome is 104 bits, so the one-mutant neighbourhood is ENUMERATED with no sampling error. Multiple statistics, not one: maximal next-goal fitness in the phenotypic neighbourhood, averaged modularity of neighbouring circuits, and counts of modular and non-modular goals in it.",
  "measured_in_all_arms": True,
  "arms": ["fixed goal", "modularly varying goal", "non-block varying goal, a control absent from the main text"],
  "uncertainty_reported": "Mean and standard error per scenario over 30 simulations. Better statistical practice than Toussaint 2003 or Kouvaris 2017.",
  "subsequent_acquisition_measured": True,
  "causal_intervention": False,
  "causal_note": "C-mechanism absent: the arms are goal schedules, causally remote from the variation operator",
  "conditioned_on_cheap_state": False,
  "surviving_artifacts": "article PDF, XML and the 3,024,384-byte Text S1, held at ergon/kouvaris2017/original/parter2008*. Two seats retrieved Text S1 independently and the sha256 matches byte for byte.",
  "reconstruction_feasibility": "not assessed",
  "confounds": ["the detector is CONTENT-ADDRESSED, keyed to a named goal set, which is a difference in kind from HC-T01's breadth statistics, not merely a difference in substrate"],
  "evidence_tier": "ELENCHUS_VERIFIED_BY_GREP_AGAINST_RETRIEVED_BYTES, independently re-fetched and hash-matched by ERGON",
  "H_level": "H2 at minimum, in all arms, with error bars",
  "H_level_note": "UNRESOLVED DISAGREEMENT BETWEEN TWO SIBLING SEATS, recorded rather than adjudicated. Elenchus reads the measurement as longitudinal and scores D4-weak. Ergon reads 'genomes from the end of the last G1-epoch population were analyzed' as endpoint-per-arm. Herakles has not read the file and takes no side.",
  "relation_to_HC_T01": "THE LOCAL-LONGITUDINAL ACCESSIBILITY CELL HAS NOT BEEN EMPTY SINCE 2008. This seat's packet section 6 asserted the MVG line never measured a distribution; that assertion is withdrawn. Missed because the lane brief listed Kashtan and Alon 2005, 2007 and 2009 and did not list Parter 2008, and because this seat never read elenchus/kashtan-alon-mvg/ despite the directive saying to coordinate with that seat."},
]

R_ADD = [
 {"specimen_id": "background-manrubia-cuesta-2015-vanishes-under-conditioning",
  "source": "Manrubia and Cuesta 2015, on neutral-network dynamics; reported by the HC-L01 lane",
  "accessibility_effect": "PRESENT AS AN APPARENT EFFECT. Escape probability from a neutral network appears to decline with elapsed time, which reads as history-conditioned accessibility.",
  "acquisition_link": "THE EFFECT IS PROVEN ANALYTICALLY TO VANISH UNDER CONDITIONING. The decline is entirely a compositional artifact of populations drifting toward high-degree hubs. Conditioned on current degree, elapsed time carries ZERO further information.",
  "why_it_is_a_background": "This is the sharpest negative in the entire programme and it is analytic rather than empirical. In the exact substrate the directive nominated as the cleanest natural control, an apparent same-elapsed-time-different-future effect is shown to be pure collider bias. It is the textbook demonstration of the hazard the H2-to-H3 gate exists to catch.",
  "kill_condition": "generalises K2 and the history-versus-location distinction of directive section 8",
  "evidence_tier": "HCL01_LANE",
  "standing_consequence": "Any RNA or neutral-network H3 attempt must condition on degree and robustness at least as carefully as Manrubia and Cuesta did, or it will reproduce their artifact rather than refute it. Network position is NOT automatically independent of current state: degree is itself a strong summary of position, and a population's position is non-randomly selected by its own history."},

 {"specimen_id": "background-mvg-effect-is-authored-curriculum",
  "source": "Elenchus seat, elenchus/kashtan-alon-mvg/, nineteen deliverables, commit 397dc307f, every load-bearing quote verified by grep against retrieved bytes",
  "accessibility_effect": "PRESENT and exhaustively measured, in all arms, since 2008",
  "acquisition_link": "PRESENT BUT CONFINED TO AN AUTHORED REGION. The authors' own difficulty-matched null: 'MVG's outperformance occurred only toward goals within the modularity language. MVG adaptation toward non-modular goals was not significantly different from FG's.' The advantage lives on about 1e-4 of the phenotype space, and it is the part the experimenter wrote.",
  "why_it_is_a_background": "Two dissociations break the standard causal story. Randomly varying goals produce NO modularity yet give 45x to 160x speedups. Alternation with no selection at all gives 190x against MVG's 265x. Modularity is a correlate of the speed effect, not its cause; the operative condition is genotype-space proximity between successive goals.",
  "independent_replication": "REVERSED THE SIGN. Clune, Beckmann, McKinley and Ofria 2010, retina arm, with a direct-encoding control at Kashtan's own switching rate, out to 30,000 generations. The NAND-circuit arm, which carries every accessibility result in the line, has never been independently replicated or refuted by anyone.",
  "kill_condition": "n/a, this is a background on the phenomenon rather than on a detector",
  "evidence_tier": "ELENCHUS_VERIFIED",
  "standing_consequence": "House calibration particle cal-08 must be marked CONTESTED and held out of the detector-scoring set. And any Prometheus claim that varying environments buy general evolvability must carry the difficulty-matched null."},

 {"specimen_id": "diagnosis-breadth-detectors-cannot-beat-fitness",
  "source": "Elenchus seat, from Parter 2008 Text S1, addressed explicitly to HC-T01",
  "accessibility_effect": "n/a, this is a diagnosis of why our own detector failed",
  "acquisition_link": "THE EXPLANATION FOR K7. Verbatim from the Elenchus commit: 'the MVG detector is content-addressed, not a breadth statistic. Text S1 reports that organisms under unstructured variation vary MORE broadly and score LOWER. A breadth detector has no reason to beat fitness at predicting acquisition. Measuring WHICH phenotypes are reachable relative to a named target set is an inheritable repair.'",
  "why_it_is_a_background": "HC-T01's modular degree, mutual information and neutral degree are ALL breadth or structure statistics. None asks whether the reachable set contains anything the population is trying to reach. On this reading K7 was not bad luck, and not a property of accessibility detectors in general. It was a consequence of choosing a target-blind statistic.",
  "kill_condition": "K7, explained",
  "evidence_tier": "ELENCHUS_VERIFIED",
  "standing_consequence": "OVERTURNS the primary detector recommendation in EVCA_HCA1_HCA2_DESIGN_NOTE.md section 6. A behavioural-distance cloud is a breadth statistic and would reproduce K7. The primary EvCA detector must be CONTENT-ADDRESSED: how much of the neighbourhood lands in a named target set, not how widely it spreads."},
]

if __name__ == "__main__":
    for name, rows in (("HISTORY_CONDITIONED_ACCESSIBILITY_REGISTRY.jsonl", Q_ADD),
                       ("ACCESSIBILITY_WITHOUT_ACQUISITION_NEGATIVES.jsonl", R_ADD)):
        p = os.path.join(HERE, name)
        with open(p, "a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("%-52s +%d -> %d rows"
              % (name, len(rows), sum(1 for _ in open(p, encoding="utf-8"))))
