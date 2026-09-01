# MINT-0001 — vacuous_truth — truth value of a quantified claim (universal / negative-universal / conditional / existential) over a domain the premises state is EMPTY, versus the same claim over a non-empty domain with or without a counterexample.
**STATUS:** `DORMANT` · **updated** 2026-09-01T08:07:11Z · missing-for-READY: none

## PRIORITY
- **score**: 0.812
- **dimensions**: - **cheap_search_exhaustion**: 1.0
- **distinct_models**: 2
- **distinct_failure_families**: 10
- **evidence_current_set_cannot_express**: 1.0
- **frequency_across_worlds**: 0.5
- **number_of_independent_origins**: 1.0
- **potential_cross_world_utility**: 0.5
- **quality_of_reproducer**: 1.0
- **quality_of_falsifier**: 1.0
- **minimality_of_required_extension**: 0.5
- **rationale**: RECLASSIFIED 2026-09-01: kernel is a Level-1 composition of frozen primitives (semantic-only closure test); the wall's substance is a REPRESENTATION adapter. Not a Master Smith target. Apprentice 'widen' mode may keep measuring adapter coverage.

## SOURCE_WORLD
Apollo typed-blackboard canary (apollo/data/clean_canary_v01.json, category vacuous_truth) and Charon's blind E9 battery (roles/Charon/apollo_e9/charon_battery_E9.json, 6 items).

## SOURCE_AGENT
Apollo (E9 abstained 40/42; vacuous_truth 0/6). Diagnosis by Aporia 155-S/156-S.

## FAILURE_FAMILY
vacuous_truth — truth value of a quantified claim (universal / negative-universal / conditional / existential) over a domain the premises state is EMPTY, versus the same claim over a non-empty domain with or without a counterexample.

## WHAT_FAILED
Apollo emits selected_answer=None on every vacuous_truth task: no registered transformer produces a truth value for a quantified claim; parse_comparison is gated on 'Is X larger than Y'.

## WHAT_SHOULD_HAVE_HAPPENED
state.comparison = True for a universal/negative-universal/conditional claim whose domain is stated empty (vacuous truth); False for an existential over an empty domain or a universal with a stated counterexample; None (abstain) when the premises give no information. The frozen tail score_by_comparison__g then selects.

## MINIMAL_REPRODUCER
PYTHONPATH=. python -m hephaestus.src.wall_vacuous_truth  (builds the 88-example dev set; prints the counterfeit battery). Candidate execution: python -m hephaestus.src.run_candidate vacuous_truth <candidate.py> <out.json>.

## POSITIVE_EXAMPLES
- **id**: vt-000; **kind**: VAC_UNIV_EMPTY; **prompt**: The number of red marbles in the jar is zero. Consider the claim: every red marble in the jar is chipped. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-001; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: The number of red marbles in the jar is zero. Consider the claim: no red marble in the jar is chipped. Is the claim true?; **correct**: yes
- **id**: vt-002; **kind**: VAC_COND_EMPTY; **prompt**: Nobody has ever found a red marble that is heavier than ten grams in the jar, and there are none now. Consider the claim: whenever a red marble in the jar is heavier than ten grams, it is chipped. Is the claim true?; **correct**: yes
- **id**: vt-004; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: every red marble in the jar is chipped. The number of red marbles in the jar is zero. Is the claim true?; **correct**: yes
- **id**: vt-006; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 5 red marbles in the jar, and all 5 of them are chipped. Consider the claim: any red marble in the jar is chipped. Is the claim true?; **correct**: yes, it is true
- **id**: vt-007; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 5 red marbles in the jar, and 3 of them are chipped. Consider the claim: there is a red marble in the jar that is chipped. Is the claim true?; **correct**: yes
- **id**: vt-011; **kind**: VAC_UNIV_EMPTY; **prompt**: Not a single book with more than 500 pages is in this shelf. Consider the claim: any book with more than 500 pages in this shelf is overdue. Is the claim true?; **correct**: yes
- **id**: vt-012; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: Not a single book with more than 500 pages is in this shelf. Consider the claim: none of the books with more than 500 pages in this shelf are overdue. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-013; **kind**: VAC_COND_EMPTY; **prompt**: No book with more than 500 pages in this shelf is signed. Consider the claim: whenever a book with more than 500 pages in this shelf is signed, it is overdue. Is the claim true?; **correct**: yes, it is true
- **id**: vt-015; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: any book with more than 500 pages in this shelf is overdue. Not a single book with more than 500 pages is in this shelf. Is the claim true?; **correct**: yes
- **id**: vt-017; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 7 books with more than 500 pages in this shelf, and all 7 of them are overdue. Consider the claim: each book with more than 500 pages in this shelf is overdue. Is the claim true?; **correct**: yes, it is true
- **id**: vt-018; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 7 books with more than 500 pages in this shelf, and 3 of them are overdue. Consider the claim: some book with more than 500 pages in this shelf is overdue. Is the claim true?; **correct**: yes, it is true
- **id**: vt-022; **kind**: VAC_UNIV_EMPTY; **prompt**: There are no employees who hold a pilot licence in the department. Consider the claim: every employee who holds a pilot licence in the department is on the weekend rota. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-023; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: There are no employees who hold a pilot licence in the department. Consider the claim: no employee who holds a pilot licence in the department is on the weekend rota. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-024; **kind**: VAC_COND_EMPTY; **prompt**: Nobody has ever found a employee who holds a pilot licence that is over forty in the department, and there are none now. Consider the claim: whenever a employee who holds a pilot licence in the department is over forty, it is on the weekend rota. Is the claim true?; **correct**: yes
- **id**: vt-026; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: each employee who holds a pilot licence in the department is on the weekend rota. There are no employees who hold a pilot licence in the department. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-028; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 4 employees who hold a pilot licence in the department, and all 4 of them are on the weekend rota. Consider the claim: all employees who hold a pilot licence in the department are on the weekend rota. Is the claim true?; **correct**: yes
- **id**: vt-029; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 4 employees who hold a pilot licence in the department, and 2 of them are on the weekend rota. Consider the claim: at least one employee who holds a pilot licence in the department is on the weekend rota. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-033; **kind**: VAC_UNIV_EMPTY; **prompt**: There are no items weighing more than two kilograms in the box. Consider the claim: all items weighing more than two kilograms in the box are fragile. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-034; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: There are no items weighing more than two kilograms in the box. Consider the claim: no item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: yes, it is true
- **id**: vt-035; **kind**: VAC_COND_EMPTY; **prompt**: No item weighing more than two kilograms in the box is insured. Consider the claim: if a item weighing more than two kilograms in the box is insured, then it is fragile. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-037; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: any item weighing more than two kilograms in the box is fragile. There are no items weighing more than two kilograms in the box. Is the claim true?; **correct**: yes, it is true
- **id**: vt-039; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 6 items weighing more than two kilograms in the box, and all 6 of them are fragile. Consider the claim: each item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: yes, it is true
- **id**: vt-040; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 6 items weighing more than two kilograms in the box, and 1 of them are fragile. Consider the claim: some item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: yes, it is true
- **id**: vt-044; **kind**: VAC_UNIV_EMPTY; **prompt**: The number of people taller than two metres in the room is zero. Consider the claim: all people taller than two metres in the room are asleep. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-045; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: The number of people taller than two metres in the room is zero. Consider the claim: no person taller than two metres in the room is asleep. Is the claim true?; **correct**: yes
- **id**: vt-046; **kind**: VAC_COND_EMPTY; **prompt**: Not a single person taller than two metres that is wearing a hat is in the room. Consider the claim: whenever a person taller than two metres in the room is wearing a hat, it is asleep. Is the claim true?; **correct**: yes, it is true
- **id**: vt-048; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: each person taller than two metres in the room is asleep. The number of people taller than two metres in the room is zero. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-050; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 5 people taller than two metres in the room, and all 5 of them are asleep. Consider the claim: each person taller than two metres in the room is asleep. Is the claim true?; **correct**: yes
- **id**: vt-051; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 5 people taller than two metres in the room, and 2 of them are asleep. Consider the claim: some person taller than two metres in the room is asleep. Is the claim true?; **correct**: yes, it is true
- **id**: vt-055; **kind**: VAC_UNIV_EMPTY; **prompt**: There are no electric cars in the garage. Consider the claim: each electric car in the garage is blue. Is the claim true?; **correct**: yes, it is true
- **id**: vt-056; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: There are no electric cars in the garage. Consider the claim: no electric car in the garage is blue. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-057; **kind**: VAC_COND_EMPTY; **prompt**: No electric car in the garage is registered abroad. Consider the claim: whenever a electric car in the garage is registered abroad, it is blue. Is the claim true?; **correct**: yes
- **id**: vt-059; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: each electric car in the garage is blue. There are no electric cars in the garage. Is the claim true?; **correct**: yes
- **id**: vt-061; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 5 electric cars in the garage, and all 5 of them are blue. Consider the claim: each electric car in the garage is blue. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-062; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 5 electric cars in the garage, and 2 of them are blue. Consider the claim: at least one electric car in the garage is blue. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-066; **kind**: VAC_UNIV_EMPTY; **prompt**: Nobody has ever found a tree older than a century in the orchard, and there are none now. Consider the claim: every tree older than a century in the orchard is diseased. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-067; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: Nobody has ever found a tree older than a century in the orchard, and there are none now. Consider the claim: no tree older than a century in the orchard is diseased. Is the claim true?; **correct**: yes
- **id**: vt-068; **kind**: VAC_COND_EMPTY; **prompt**: Not a single tree older than a century that is fenced is in the orchard. Consider the claim: if a tree older than a century in the orchard is fenced, then it is diseased. Is the claim true?; **correct**: yes
- **id**: vt-070; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: each tree older than a century in the orchard is diseased. Nobody has ever found a tree older than a century in the orchard, and there are none now. Is the claim true?; **correct**: yes
- **id**: vt-072; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 4 trees older than a century in the orchard, and all 4 of them are diseased. Consider the claim: all trees older than a century in the orchard are diseased. Is the claim true?; **correct**: yes
- **id**: vt-073; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 4 trees older than a century in the orchard, and 3 of them are diseased. Consider the claim: there is a tree older than a century in the orchard that is diseased. Is the claim true?; **correct**: yes
- **id**: vt-077; **kind**: VAC_UNIV_EMPTY; **prompt**: Not a single letter written in Latin is in the archive. Consider the claim: every letter written in Latin in the archive is damaged. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-078; **kind**: VAC_NEGUNIV_EMPTY; **prompt**: Not a single letter written in Latin is in the archive. Consider the claim: none of the letters written in Latin in the archive are damaged. Is the claim true?; **correct**: yes, it is true
- **id**: vt-079; **kind**: VAC_COND_EMPTY; **prompt**: No letter written in Latin in the archive is catalogued. Consider the claim: if a letter written in Latin in the archive is catalogued, then it is damaged. Is the claim true?; **correct**: yes, the claim holds
- **id**: vt-081; **kind**: VAC_UNIV_EMPTY_ORDER; **prompt**: Consider the claim: every letter written in Latin in the archive is damaged. Not a single letter written in Latin is in the archive. Is the claim true?; **correct**: yes, it is true
- **id**: vt-083; **kind**: NONEMPTY_UNIV_ALL; **prompt**: There are exactly 5 letters written in Latin in the archive, and all 5 of them are damaged. Consider the claim: all letters written in Latin in the archive are damaged. Is the claim true?; **correct**: yes, it is true
- **id**: vt-084; **kind**: NONEMPTY_EXIST_TRUE; **prompt**: There are exactly 5 letters written in Latin in the archive, and 4 of them are damaged. Consider the claim: there is a letter written in Latin in the archive that is damaged. Is the claim true?; **correct**: yes, the claim holds

## NEGATIVE_EXAMPLES
- **id**: vt-003; **kind**: EXIST_EMPTY; **prompt**: The number of red marbles in the jar is zero. Consider the claim: some red marble in the jar is chipped. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-005; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 5 red marbles in the jar, and exactly 3 of them are chipped. Consider the claim: any red marble in the jar is chipped. Is the claim true?; **correct**: no, it is false
- **id**: vt-009; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no heavier than ten grams red marbles in the jar, but there are exactly 5 red marbles in the jar and only 3 of them are chipped. Consider the claim: any red marble in the jar is chipped. Is the claim true?; **correct**: no
- **id**: vt-010; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on the jar. It holds exactly 5 red marbles, and 3 of them are chipped. Consider the claim: every red marble in the jar is chipped. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-014; **kind**: EXIST_EMPTY; **prompt**: Not a single book with more than 500 pages is in this shelf. Consider the claim: there is a book with more than 500 pages in this shelf that is overdue. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-016; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 7 books with more than 500 pages in this shelf, and exactly 3 of them are overdue. Consider the claim: every book with more than 500 pages in this shelf is overdue. Is the claim true?; **correct**: no, it is false
- **id**: vt-020; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no signed books with more than 500 pages in this shelf, but there are exactly 7 books with more than 500 pages in this shelf and only 3 of them are overdue. Consider the claim: every book with more than 500 pages in this shelf is overdue. Is the claim true?; **correct**: no
- **id**: vt-021; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on this shelf. It holds exactly 7 books with more than 500 pages, and 3 of them are overdue. Consider the claim: all books with more than 500 pages in this shelf are overdue. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-025; **kind**: EXIST_EMPTY; **prompt**: There are no employees who hold a pilot licence in the department. Consider the claim: at least one employee who holds a pilot licence in the department is on the weekend rota. Is the claim true?; **correct**: no, it is false
- **id**: vt-027; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 4 employees who hold a pilot licence in the department, and exactly 2 of them are on the weekend rota. Consider the claim: all employees who hold a pilot licence in the department are on the weekend rota. Is the claim true?; **correct**: no, it is false
- **id**: vt-031; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no over forty employees who hold a pilot licence in the department, but there are exactly 4 employees who hold a pilot licence in the department and only 2 of them are on the weekend rota. Consider the claim: each employee who holds a pilot licence in the department is on the weekend rota. Is the claim true?; **correct**: no
- **id**: vt-032; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on the department. It holds exactly 4 employees who hold a pilot licence, and 2 of them are on the weekend rota. Consider the claim: any employee who holds a pilot licence in the department is on the weekend rota. Is the claim true?; **correct**: no, it is false
- **id**: vt-036; **kind**: EXIST_EMPTY; **prompt**: There are no items weighing more than two kilograms in the box. Consider the claim: some item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-038; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 6 items weighing more than two kilograms in the box, and exactly 1 of them are fragile. Consider the claim: every item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: no
- **id**: vt-042; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no insured items weighing more than two kilograms in the box, but there are exactly 6 items weighing more than two kilograms in the box and only 1 of them are fragile. Consider the claim: any item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: no
- **id**: vt-043; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on the box. It holds exactly 6 items weighing more than two kilograms, and 1 of them are fragile. Consider the claim: any item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: no
- **id**: vt-047; **kind**: EXIST_EMPTY; **prompt**: The number of people taller than two metres in the room is zero. Consider the claim: there is a person taller than two metres in the room that is asleep. Is the claim true?; **correct**: no, it is false
- **id**: vt-049; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 5 people taller than two metres in the room, and exactly 2 of them are asleep. Consider the claim: every person taller than two metres in the room is asleep. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-053; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no wearing a hat people taller than two metres in the room, but there are exactly 5 people taller than two metres in the room and only 2 of them are asleep. Consider the claim: every person taller than two metres in the room is asleep. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-054; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on the room. It holds exactly 5 people taller than two metres, and 2 of them are asleep. Consider the claim: all people taller than two metres in the room are asleep. Is the claim true?; **correct**: no
- **id**: vt-058; **kind**: EXIST_EMPTY; **prompt**: There are no electric cars in the garage. Consider the claim: at least one electric car in the garage is blue. Is the claim true?; **correct**: no, it is false
- **id**: vt-060; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 5 electric cars in the garage, and exactly 2 of them are blue. Consider the claim: any electric car in the garage is blue. Is the claim true?; **correct**: no, it is false
- **id**: vt-064; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no registered abroad electric cars in the garage, but there are exactly 5 electric cars in the garage and only 2 of them are blue. Consider the claim: all electric cars in the garage are blue. Is the claim true?; **correct**: no, it is false
- **id**: vt-065; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on the garage. It holds exactly 5 electric cars, and 2 of them are blue. Consider the claim: all electric cars in the garage are blue. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-069; **kind**: EXIST_EMPTY; **prompt**: Nobody has ever found a tree older than a century in the orchard, and there are none now. Consider the claim: some tree older than a century in the orchard is diseased. Is the claim true?; **correct**: no, the claim fails
- **id**: vt-071; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 4 trees older than a century in the orchard, and exactly 3 of them are diseased. Consider the claim: every tree older than a century in the orchard is diseased. Is the claim true?; **correct**: no, it is false
- **id**: vt-075; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no fenced trees older than a century in the orchard, but there are exactly 4 trees older than a century in the orchard and only 3 of them are diseased. Consider the claim: any tree older than a century in the orchard is diseased. Is the claim true?; **correct**: no, it is false
- **id**: vt-076; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on the orchard. It holds exactly 4 trees older than a century, and 3 of them are diseased. Consider the claim: each tree older than a century in the orchard is diseased. Is the claim true?; **correct**: no
- **id**: vt-080; **kind**: EXIST_EMPTY; **prompt**: Not a single letter written in Latin is in the archive. Consider the claim: some letter written in Latin in the archive is damaged. Is the claim true?; **correct**: no, it is false
- **id**: vt-082; **kind**: NONEMPTY_UNIV_COUNTEREX; **prompt**: There are exactly 5 letters written in Latin in the archive, and exactly 4 of them are damaged. Consider the claim: each letter written in Latin in the archive is damaged. Is the claim true?; **correct**: no, it is false
- **id**: vt-086; **kind**: NEARMISS_NO_KEYWORD; **prompt**: There are no catalogued letters written in Latin in the archive, but there are exactly 5 letters written in Latin in the archive and only 4 of them are damaged. Consider the claim: each letter written in Latin in the archive is damaged. Is the claim true?; **correct**: no, it is false
- **id**: vt-087; **kind**: NEARMISS_VACUOUS_WORD; **prompt**: The label 'vacuous' is printed on the archive. It holds exactly 5 letters written in Latin, and 4 of them are damaged. Consider the claim: every letter written in Latin in the archive is damaged. Is the claim true?; **correct**: no, it is false

## BOUNDARY_EXAMPLES
- **id**: vt-008; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 5 red marbles in the jar. Consider the claim: each red marble in the jar is chipped. Is the claim true?; **correct**: abstain (cannot be determined)
- **id**: vt-019; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 7 books with more than 500 pages in this shelf. Consider the claim: all books with more than 500 pages in this shelf are overdue. Is the claim true?; **correct**: abstain (cannot be determined)
- **id**: vt-030; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 4 employees who hold a pilot licence in the department. Consider the claim: every employee who holds a pilot licence in the department is on the weekend rota. Is the claim true?; **correct**: abstain (cannot be determined)
- **id**: vt-041; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 6 items weighing more than two kilograms in the box. Consider the claim: any item weighing more than two kilograms in the box is fragile. Is the claim true?; **correct**: abstain (cannot be determined)
- **id**: vt-052; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 5 people taller than two metres in the room. Consider the claim: every person taller than two metres in the room is asleep. Is the claim true?; **correct**: abstain (cannot be determined)
- **id**: vt-063; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 5 electric cars in the garage. Consider the claim: every electric car in the garage is blue. Is the claim true?; **correct**: abstain (cannot be determined)
- **id**: vt-074; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 4 trees older than a century in the orchard. Consider the claim: all trees older than a century in the orchard are diseased. Is the claim true?; **correct**: abstain (cannot be determined)
- **id**: vt-085; **kind**: NONEMPTY_UNKNOWN; **prompt**: There are exactly 5 letters written in Latin in the archive. Consider the claim: every letter written in Latin in the archive is damaged. Is the claim true?; **correct**: abstain (cannot be determined)

## CURRENT_PRIMITIVES
- all_but_n
- bat_and_ball
- bayesian_update
- check_transitivity
- coin_flip_independence
- confidence_from_agreement
- counterfactual_intervention
- dag_traverse
- direction_composition
- entropy
- expected_value
- fencepost_count
- information_sufficiency
- modular_arithmetic
- modus_ponens
- negate
- parity_check
- pigeonhole_check
- sally_anne_test
- solve_constraints
- solve_linear_system
- solve_sat
- temporal_order
- topological_sort
- track_beliefs
- apollo REGISTRY: 27 ops (15 transformers, 10 scorers, 2 quarantine)

## PRIMITIVE_SET_HASH
- **forge_primitives.py**: 24bbe0486f0ad22b
- **apollo/src/blackboard_evolve.py**: 7ef2904b0cf3ccf2
- **IQ-PORT-1 frozen evaluator (aporia/iq)**: 10fa10db9989eb3a79c2039d18b748a83e93f751578ec6d0a0e12717eb0fa5ae

## WHY_COMPOSITION_APPEARS_INSUFFICIENT
No registered transformer writes `comparison` on any vacuous_truth prompt; the only producer of that slot (parse_comparison) is gated on 'Is X larger than Y'. The reachable set G(C) contains no path from problem_text to a truth value for a quantified claim over a possibly-empty domain. The only primitive touching predicates is solve_constraints(variables, domains, constraints), a finite-domain CSP over explicit variables: nothing parses a domain or a predicate from text, and a CSP with no variables does not encode 'every X is P' over an empty X-set as a truth value. No primitive computes a universally/existentially quantified truth value or models an empty domain; `negate` is surface-form only.

## CLOSURE_EVIDENCE
- **apollo_registry_transformers_run**: 15; **slots_written_by_registry_on_this_wall**: - **parse_numbers**: - numbers; **registry_ops_that_commit_comparison**: 0; **reading**: No registered transformer writes `comparison` on any vacuous_truth prompt; the only producer of that slot (parse_comparison) is gated on 'Is X larger than Y'. The reachable set G(C) contains no path from problem_text to a truth value for a quantified claim over a possibly-empty domain.; **forge_primitives**: - **all_but_n**: (total: int, n: int) -> int
- **bat_and_ball**: (total: float, difference: float) -> tuple[float, float]
- **bayesian_update**: (prior: float, likelihood: float, false_positive: float = 0.0) -> float
- **check_transitivity**: (relations: list[tuple[str, str]]) -> dict[str, set[str]]
- **coin_flip_independence**: (n_flips: int, target_heads: int) -> float
- **confidence_from_agreement**: (scores: list[float]) -> float
- **counterfactual_intervention**: (edges: list[tuple[str, str]], values: dict[str, float], intervene_node: str, intervene_value: float) -> dict[str, float]
- **dag_traverse**: (edges: list[tuple[str, str]], start: str) -> list[str]
- **direction_composition**: (directions: list[str]) -> str
- **entropy**: (probs: list[float]) -> float
- **expected_value**: (outcomes: list[tuple[float, float]]) -> float
- **fencepost_count**: (n_segments: int, include_both_ends: bool = True) -> int
- **information_sufficiency**: (n_unknowns: int, n_constraints: int) -> str
- **modular_arithmetic**: (a: int, b: int, mod: int) -> int
- **modus_ponens**: (premises: list[tuple[str, str]], facts: set[str]) -> set[str]
- **negate**: (statement: str) -> str
- **parity_check**: (numbers: list[int]) -> str
- **pigeonhole_check**: (items: int, containers: int) -> bool
- **sally_anne_test**: (who_moved: str, who_saw_move: set[str], original_location: str, new_location: str) -> dict[str, str]
- **solve_constraints**: (variables: list[str], domains: dict[str, list], constraints: list[tuple[list[str], callable]]) -> dict | None
- **solve_linear_system**: (A: list[list[float]], b: list[float]) -> list[float] | None
- **solve_sat**: (clauses: list[list[int]], n_vars: int) -> dict[int, bool] | None
- **temporal_order**: (events: list[tuple[str, str, str]]) -> list[str]
- **topological_sort**: (edges: list[tuple[str, str]]) -> list[str] | None
- **track_beliefs**: (agents: list[str], observations: list[tuple[str, str, bool]]) -> dict[str, set[str]]; **forge_primitives_accepting_callable_predicate**: - solve_constraints; **forge_primitives_reading**: The only primitive touching predicates is solve_constraints(variables, domains, constraints), a finite-domain CSP over explicit variables: nothing parses a domain or a predicate from text, and a CSP with no variables does not encode 'every X is P' over an empty X-set as a truth value. No primitive computes a universally/existentially quantified truth value or models an empty domain; `negate` is surface-form only.; **prior_evidence**: - aporia/iq/FINDINGS_SELECTOR_PREFLIGHT_2026-08-25.md: frozen pool = 25 forge primitives + 2 port ops; 18 expressible; zero candidates move dE for a capability-related reason; vacuous_truth untouched.
- aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:72-75: vacuous_truth = GENUINE capability gap, 'no vacuous-implication semantics'.
- apollo/cycles/campaign_20260825/E9_RESULT.json: Apollo scored 0/6 on Charon's blind vacuous_truth items (abstained).

## SEMANTIC_KERNEL_SPEC
- **inputs**: - **quantifier**: universal | negative_universal | existential
- **domain_size**: int >= 0 (0 = empty)
- **satisfier_count**: int, 0..domain_size, or unknown
- **output**: truth value; undetermined when a count is unknown
- **truth_table**: every/0/0 T; no/0/0 T; some/0/0 F; every/n/n T; every/n/<n F; no/n/0 T; no/n/>0 F; some/n/>0 T; some/n/0 F
- **semantic_only_closure_test**: - **script**: hephaestus/src/semantic_closure.py
- **result**: hephaestus/mint_queue/MINT-0001/semantic_closure_result.json
- **A0_frozen_no_routing**: impossible by arity: the three columns differ at (0,0)
- **A1_frozen_with_routing**: - **found**: - **existential**: - s
- 1
- **negative_universal**: - pigeonhole_check(1, s)
- 1
- **universal**: - coin_flip_independence(s, d)
- 1
- **evaluated**: 156
- **depth**: 1
- **B_generic_language**: - **found**: - **existential**: - s
- 1
- **universal**: - eq(d, s)
- 1
- **negative_universal**: - eq(s, 0)
- 1
- **evaluated**: 152
- **depth**: 1
- **C_v3_kernel**: - **rows**: 48
- **correct**: 48
- **kernel_lines**: 10
- **principled_depth2_form**: universal = pigeonhole_check(s, all_but_n(d, 1))  i.e. s >= d; negative_universal = pigeonhole_check(1, s); existential = s
- **caveat**: A1's depth-1 universal solution coin_flip_independence(s, d) is a truthiness coincidence (comb(s,d)=0 iff s<d); it is inside G(C) but is not a mechanism. The depth-2 form is the mechanism and is also inside G(C).
- **CLASSIFICATION**: LEVEL 1 — a composition of frozen primitives under per-quantifier routing. NOT a missing operator. What was missing: (a) routing on a quantifier slot, (b) a semantic state that carries domain_size / satisfier_count at all.
- **what_is_still_missing_if_perfect_semantic_state_were_injected**: almost nothing (three depth<=2 compositions + one guard per quantifier)

## REPRESENTATION_ADAPTER_SPEC
- **problem**: From natural-language premises + a quantified claim, produce (quantifier, domain noun phrase, predicate, domain_size, satisfier_count) where facts are accepted only if their noun phrase EQUALS the claim's domain.
- **measured_adapter**: deep_mint_sessions/20260901T073136Z/candidates/v3_quantified_truth.py (~110 of ~120 lines are this adapter)
- **coverage_on_dev_v2**: - **holdout_accuracy**: 0.9125
- **coverage**: 0.9125
- **conditional_correctness**: 1.0
- **boundary_false_commit**: 0.0
- **coverage_on_adversarial_20**: - **correct**: 4
- **n**: 20
- **false_commits**: 0
- **abstentions**: 16
- **idioms_not_covered**: - aren't any
- zero X are
- has no
- empty of
- lives in (verb)
- Is it true that ...?
- Claim: ... True or false?
- every one of the
- there exists
- semicolon counts
- none of them
- all of them (no count)
- number words
- singular '1 of them is'
- restrictive relative 'that is P is also Q'
- **D1_mapping_owed**: 'there are no <P> <X>' with non-empty <X> domain  ->  satisfier_count = 0 (an adapter mapping, not a kernel rule)
- **untested_component_now_tested**: predicate check in the cardinality reader: knockout P4 was 0.000 on dev v1; dev v2 adds NONEMPTY_OTHER_PREDICATE (gold abstain) so it is now load-bearing
- **ROUTING**: REPRESENTATION problem. Per Addendum 1 §10 this is not sent to the Master Smith as a Level-2 reasoning mint. Candidates: Apollo (parser ops on the blackboard), Ludus/Foundry (expose semantic-state worlds directly so the kernel can be tested without language), cheap-model parser widening (apprentice 'widen' mode, labelled representation work).

## SEARCH_ALREADY_ATTEMPTED
- Apollo O1 exhaustive enumeration over 1.74M type-correct pipelines: vacuous_truth 0/5 (ceiling 0.833; number later retracted by E9, but the abstention on this category is structural).
- Aporia SELECTOR pre-flight over the frozen 27-candidate pool: zero capability-related dE movers.
- Apollo E9 blind battery: 0/6, all abstained.
- Master Smith (Claude Code / Fable, operator-invoked, 5 cycles, 2026-09-01): kernel+parser candidate v3 passes dev; 4/20 on out-of-template phrasings with 0 false commits; see deep_mint_sessions/20260901T073136Z/
- semantic_closure.py (2026-09-01): frozen primitives + routing synthesise the kernel at depth 1 (156 evaluations) -> Level-1 composition; wall reclassified as representation.

## CHEAP_MODEL_ATTEMPTS
- **n**: 1; **ts**: 2026-09-01T07:08:12Z; **model**: nvidia:nvidia/nemotron-3-super-120b-a12b; **verdict**: NO_CODE; **holdout_acc**: _(missing)_; **boundary_false_commit**: _(missing)_; **failure_families**: _(none yet)_; **latency_s**: 39.9; **file**: _(missing)_; **harness_fault**: True; **note**: max_tokens=1800 truncated a reasoning model before its code fence; harness fixed (6000, code-first)
- **n**: 2; **ts**: 2026-09-01T07:08:52Z; **model**: ollama:phi3; **verdict**: RUNTIME_ERROR_ALL; **holdout_acc**: 0.0; **boundary_false_commit**: 0.0; **failure_families**: - runtime_error:NameError: name 're' is not defined; **latency_s**: 29.3; **file**: hephaestus\mint_queue\MINT-0001\attempts\0002_20260901T070852Z_ollama-phi3.py; **rescored**: 2026-09-01T07:15:09Z
- **n**: 4; **ts**: 2026-09-01T07:10:19Z; **model**: nvidia:nvidia/nemotron-3-super-120b-a12b; **verdict**: FAIL_DEV; **holdout_acc**: 0.3288; **boundary_false_commit**: 1.0; **failure_families**: - below_chance_or_abstaining
- commits_without_information
- keys_on_claim_form_not_domain_emptiness
- quantifier_blind
- candidate_order_dependent
- surface_form_of_emptiness
- weak_kinds:EXIST_EMPTY,NEARMISS_NO_KEYWORD,NEARMISS_VACUOUS_WORD,NONEMPTY_EXIST_TRUE,NONEMPTY_UNIV_COUNTEREX,NONEMPTY_UNKNOWN,VAC_COND_EMPTY; **latency_s**: 144.3; **file**: hephaestus\mint_queue\MINT-0001\attempts\0004_20260901T071019Z_nvidia-nvidia-nemotron-3-super-120b-a12b.py; **rescored**: 2026-09-01T07:15:09Z
- **n**: 6; **ts**: 2026-09-01T07:12:44Z; **model**: ollama:phi3; **verdict**: RUNTIME_ERROR_ALL; **holdout_acc**: 0.0; **boundary_false_commit**: 0.0; **failure_families**: - runtime_error:InterfaceViolation: op returned bool instead of BlackboardSt; **latency_s**: 59.7; **file**: hephaestus\mint_queue\MINT-0001\attempts\0006_20260901T071244Z_ollama-phi3.py; **rescored**: 2026-09-01T07:15:09Z
- **n**: 5; **ts**: 2026-09-01T07:15:21Z; **model**: nvidia:nvidia/nemotron-3-super-120b-a12b; **verdict**: NO_CODE; **holdout_acc**: _(missing)_; **boundary_false_commit**: _(missing)_; **failure_families**: - deliberates_without_emitting; **latency_s**: 294.6; **file**: _(missing)_; **note**: 6000-token budget, code-first instruction: 23 KB of deliberation, no code emitted. Model failure family: deliberates_without_emitting.
- **n**: 6; **ts**: 2026-09-01T07:20:16Z; **model**: ollama:phi3; **verdict**: FAIL_DEV; **holdout_acc**: 0.0; **boundary_false_commit**: 0.0; **failure_families**: - below_chance_or_abstaining
- quantifier_blind
- candidate_order_dependent
- surface_form_of_emptiness
- weak_kinds:EXIST_EMPTY,NEARMISS_NO_KEYWORD,NEARMISS_VACUOUS_WORD,NONEMPTY_EXIST_TRUE,NONEMPTY_UNIV_ALL,NONEMPTY_UNIV_COUNTEREX,VAC_COND_EMPTY,VAC_NEGUNIV_EMPTY,VAC_UNIV_EMPTY,VAC_UNIV_EMPTY_ORDER
- runtime_errors:76; **latency_s**: 27.1; **file**: hephaestus\mint_queue\MINT-0001\attempts\0006_20260901T072016Z_ollama-phi3.py

## CHEAP_MODEL_FAILURES
- **family**: runtime_error; **count**: 2
- **family**: below_chance_or_abstaining; **count**: 2
- **family**: quantifier_blind; **count**: 2
- **family**: candidate_order_dependent; **count**: 2
- **family**: surface_form_of_emptiness; **count**: 2
- **family**: weak_kinds; **count**: 2
- **family**: commits_without_information; **count**: 1
- **family**: keys_on_claim_form_not_domain_emptiness; **count**: 1
- **family**: deliberates_without_emitting; **count**: 1
- **family**: runtime_errors; **count**: 1

## BEST_FAILED_CANDIDATE
- **note**: superseded by a dev-passing candidate: deep_mint_sessions/20260901T073136Z/candidates/v3_quantified_truth.py
- **apprentice_best**: - **attempt**: 4
- **model**: nvidia:nvidia/nemotron-3-super-120b-a12b
- **holdout_acc**: 0.3288
- **boundary_false_commit**: 1.0
- **failure_families**: - below_chance_or_abstaining
- commits_without_information
- keys_on_claim_form_not_domain_emptiness
- quantifier_blind
- candidate_order_dependent
- surface_form_of_emptiness
- weak_kinds:EXIST_EMPTY,NEARMISS_NO_KEYWORD,NEARMISS_VACUOUS_WORD,NONEMPTY_EXIST_TRUE,NONEMPTY_UNIV_COUNTEREX,NONEMPTY_UNKNOWN,VAC_COND_EMPTY
- **file**: hephaestus\mint_queue\MINT-0001\attempts\0004_20260901T071019Z_nvidia-nvidia-nemotron-3-super-120b-a12b.py

## KNOCKOUT_RESULTS
- **note**: Baseline (no op) = Apollo's current behaviour: abstain on every item; accuracy_decidable 0.0. Any candidate's holdout accuracy is therefore its own knockout delta.; **n_executed_attempts**: 5; **n_pass_dev**: 0
- **session**: deep_mint_sessions/20260901T073136Z; **candidate**: v3_quantified_truth.py; **baseline_holdout**: 1.0; **component_deltas**: - **K1 kernel:=constant True**: -0.3973
- **K2 kernel: drop empty-domain rule**: -0.4932
- **K3 kernel: existential-blind on empty**: -0.589
- **K4 kernel: counterexample-blind**: -0.3151
- **P1 domain match: equality -> containment**: -0.0959
- **P2 no container strip**: -0.8904
- **P3 no cardinality reader**: -0.5068
- **P4 cardinality reader ignores predicate**: 0.0
- **P5 no stemming**: -0.6301; **decorative_on_dev**: - P4 cardinality reader ignores predicate
- **semantic_only_closure**: A1 SYNTHESISES THE TABLE: the kernel is a Level-1 COMPOSITION of frozen primitives (pigeonhole_check / all_but_n / constants) under per-quantifier routing. MINT-0001 was a routing/search/representation problem, NOT a missing operator. Reclassify.

## COUNTERFEIT_TESTS
- **shortcut**: constant_yes; **accuracy_decidable**: 0.6; **boundary_false_commit_rate**: 1.0
- **shortcut**: constant_no; **accuracy_decidable**: 0.4; **boundary_false_commit_rate**: 1.0
- **shortcut**: kw_no_to_yes; **accuracy_decidable**: 0.6; **boundary_false_commit_rate**: 1.0
- **shortcut**: kw_every_to_yes; **accuracy_decidable**: 0.4; **boundary_false_commit_rate**: 1.0
- **shortcut**: kw_no_and_every_to_yes; **accuracy_decidable**: 0.6; **boundary_false_commit_rate**: 1.0
- **shortcut**: kw_vacuous_to_yes; **accuracy_decidable**: 0.0; **boundary_false_commit_rate**: 0.0
- **shortcut**: kw_some_to_no; **accuracy_decidable**: 0.6; **boundary_false_commit_rate**: 1.0

## KNOWN_SHORTCUTS
- **name**: constant_yes; **why_it_works_on_the_canary**: Apollo's canary has 5/5 'Yes'; scores 5/5 there. On the dev set: see COUNTERFEIT_TESTS.
- **name**: kw_no_and_every_to_yes; **why**: the obvious regex; fails NEARMISS_NO_KEYWORD and NONEMPTY_UNIV_ALL kinds.
- **name**: kw_vacuous_to_yes; **why**: the forge_v4 pathology: 98/375 files answer by matching the word 'vacuous' (counterfeit museum #001).

## FORBIDDEN_SHORTCUTS
- Any read of state.candidates to decide the truth value (the answer must come from problem_text).
- Matching the word 'vacuous' or the category name.
- Committing a truth value when the premises carry no information about the predicate (boundary kind must abstain).
- Hard-coding the three sentences of Apollo's canary generator.

## REPRESENTATION_PERTURBATIONS
- emptiness stated as: 'there are no X', 'contains no X', 'not a single X', 'number of X is zero', 'exactly zero X'
- claim forms: every/all/each/any X is P; no X is P; if an X is Q then P; whenever; some/there is/at least one X is P
- claim stated before vs after the emptiness fact
- distractor 'no' on a different noun phrase than the claim's domain (NEARMISS_NO_KEYWORD)
- candidate order shuffled; candidate wording varied (yes / yes, it is true / yes, the claim holds)
- OWED (from cycle 4): aren't any / zero X are / has no / empty of / lives in / 'Is it true that' / 'Claim: ... True or false?' / every one of the / there exists / semicolon counts / none of them / all of them / number words / singular '1 of them is'

## DESIRED_TYPED_INTERFACE
- **signature**: op_vacuous_truth(state: BlackboardState) -> BlackboardState
- **reads**: - problem_text
- **writes**: - comparison
- **semantics**: comparison=True claim true; False claim false; None abstain. Do not touch candidates.
- **tail**: apollo/src/blackboard_ops_compare.py score_by_comparison__g (frozen; selects candidate starting 'yes'/'no')
- **allowed_imports**: - re
- math
- itertools
- collections
- functools
- string
- forge_primitives
- blackboard
- **delta_class**: dE_synth (no implementation exists anywhere accessible; a retrieval would be dE_port and is not available)

## RESOURCE_CONSTRAINTS
Pure Python, CPU, deterministic, < 1 s per task, no network, no model calls at inference time.

## INDEPENDENT_EVALUATOR
- **status**: MISSING — this is the gate on any deep mint being READ, not on it being ATTEMPTED.
- **required**: Aporia's frozen G-heldout generator for vacuous_truth (TRANSFER-1 prerequisite per roles/Aporia/resume_aporia.md PART 2.5) and a post-E9 Apollo evaluator of record.
- **available_now_but_reserved**: Charon's E9 battery (6 items) — independent, blind, NOT to be used for development; results on it are reported only by Charon/Aporia.
- **independence_chain**: supplier (Hephaestus) != prereg author (Aporia/Charon) != prompt author != grader (frozen evaluator) != adjudicator (Charon).

## SUCCESS_CRITERION
Candidate passes dev (holdout accuracy_decidable >= 0.95, boundary_false_commit_rate == 0, all four input-mutant falsifiers pass), AND, under an independently authored prereg, moves the ceiling on the held-out generator with the op load-bearing under knockout and absent from the v1 catalog, forge library and every prior Apollo registry (mechanically checked).

## KILL_CRITERION
Three consecutive deep mints that pass dev but do not move the independent held-out => coupling dead; route to compression under Lexis/Ergon. OR a reclassification by the Master Smith (existing primitive overlooked / composition / representation / evaluator defect).

## PROVENANCE
- **ts**: 2026-09-01T07:08:02Z; **by**: hephaestus.src.triage; **note**: packet created from executed wall module; dev examples Hephaestus-authored; no Charon E9 item read by any code in hephaestus/
- **ref**: aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md:49-53
- **ref**: aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:72-75
- **ref**: apollo/scripts/gen_clean_canary_v01.py:191-208 (degenerate generator)
- **ref**: aporia/iq/probe_synth1_target_degeneracy.py
- **ref**: apollo/cycles/campaign_20260825/E9_FINDINGS.md
- **ts**: 2026-09-01T07:40:16Z; **by**: Master Smith session 20260901T073136Z; **note**: candidate produced; author of dev set == author of candidate; Charon E9 untouched
- **ts**: 2026-09-01T08:07:10Z; **by**: hephaestus.src.semantic_closure + operator Addendum 1; **note**: reclassified Level 2 -> Level 1 composition; routed as representation problem
