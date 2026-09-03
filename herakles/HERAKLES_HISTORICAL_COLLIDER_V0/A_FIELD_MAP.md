# A. FIELD MAP — research traditions, systems, dates, investigators, artifact status, lens

**Evidence source for every row EXCEPT fam-124, fam-051 and fam-063: `MODEL_RECALL_UNVERIFIED`.** Those three were promoted to `PRIMARY_SOURCE_READ` on 2026-09-03; see `RESEARCH_PASS_2026-09-03.md` for what verified, what was corrected, and what is still open. Dates are approximate, names may be incomplete, and "artifact status" is a belief to be checked, coded as: `SRC?` source believed available, `SRC-` believed unavailable, `SPEC` fully specified in print (reimplementable), `DATA?` data believed available, `?` unknown. Nothing here is a finding. Enumerate → stratify → verify → promote (METHOD §1a). Row ids are stable; edit rows in place and log promotions.

Lens codes (directive §1 signals): DUP duplication/divergence · PROT protected innovation · NEUT neutral/deleterious precursor · MOD spontaneous modularity/reuse · ROB robustness/evolvability · ENV environment modification / niche construction · ECO ecological interaction altering evolvability · STATE persistent internal state · META better-at-becoming-better · CONT historical contingency · REP representation change · REACH reachable-region change · DET the system itself is a historical detector · NEG candidate negative control · XR cross-substrate recurrence

---

## A.0 Pre-history anchors (before the 40-year window; included as calibration of what "looking for mountains" cost)
| id | system / experiment | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-000 | Numerical symbioorganisms on the IAS machine | 1953–1963 | Barricelli | printed lattices; SPEC partial; modern reimplementations `?` | DUP ECO CONT NEG (stagnation reported) |
| fam-001 | Random program mutation "learning machine" (Herman) | 1958 | Friedberg (IBM) | SPEC partial, SRC- | NEG (random search matched it) |
| fam-002 | Evolution of finite-state machines for prediction | 1966 | Fogel, Owens, Walsh | SPEC | STATE |
| fam-003 | Artificial ecosystem evolution experiments | 1970 | Conrad, Pattee | SPEC partial, SRC- | ECO ENV |
| fam-004 | AM / EURISKO heuristics modifying heuristics | 1976–1983 | Lenat | AM thesis SPEC; EURISKO source reportedly located in archives (verify) | META REP |
| fam-005 | Evolution strategies with self-adapting step sizes | 1970s– | Rechenberg, Schwefel | SPEC, SRC? | META (adaptive mutation) — calibration |
| fam-006 | Genetic algorithms, schema theory, bucket brigade | 1975– | Holland | SPEC | REP PROT |
| fam-007 | Classifier systems CS-1, default hierarchies | 1978– | Holland, Reitman, Goldberg | SPEC | STATE REP |

## A.1 Digital organisms / self-replicating programs
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-010 | Coreworld / VENUS | 1989–1990 | Rasmussen, Knudsen, Feldberg, Hindsholm | SPEC, SRC? | ECO REACH |
| fam-011 | Tierra | 1990– | T. Ray | SRC? (distributed versions), few original run dumps `?` | ECO PROT NEUT CONT (parasites, hyper-parasites, unrolled loops, cheaters) |
| fam-012 | Network Tierra | 1996–2000 | Ray | SRC? | ECO ENV |
| fam-013 | Avida (all eras) | 1993– | Adami, Brown, Ofria, Lenski, Pennock et al. | SRC (devosoft/avida) DATA? | DUP NEUT CONT META ECO STATE MOD |
| fam-013a | Avida: evolution of complex features (EQU) with deleterious stepping stones | 2003 | Lenski, Ofria, Pennock, Adami | SPEC, lineage data `?` | NEUT CONT — CALIBRATION |
| fam-013b | Avida: deleterious mutations as stepping stones | 2013 | Covert, Lenski, Wilke, Ofria | SPEC DATA? | NEUT — CALIBRATION |
| fam-013c | Avida: early evolution of memory usage | 2010 | Grabowski, Bryson, Dyer, Ofria, Pennock | SPEC DATA? | STATE |
| fam-013d | Avida: coevolution with parasites promotes evolvability | 2014 | Zaman, Meyer, Devangam, Bryson, Lenski, Ofria | SPEC DATA? | ECO META |
| fam-013e | Avida: gradual complexity / sudden features; instruction-set potential | 2008, 2013 | Ofria, Huang, Torng; Bryson, Ofria | SPEC | REACH substrate dependence |
| fam-013f | Avida: survival of the flattest; mutation-rate selection fails long-term | 2001, 2008 | Wilke et al.; Clune et al. | SPEC | ROB META |
| fam-013g | Avida: division of labour / somatic cells / task switching | 2012–2014 | Goldsby, Dornhaus, Kerr, Ofria | SPEC | MOD ECO |
| fam-014 | Amoeba (spontaneous replicators from random soup) | 1996–2001 | Pargellis | SPEC partial, SRC? | REACH (de novo emergence, rare-event) |
| fam-015 | Spontaneous emergence of self-replicating programs (sea of programs) | 1994 | Koza | SPEC | REACH |
| fam-016 | Nanopond | 2006 | Ierymenko | SRC | REACH tiny physics |
| fam-017 | Evita, Bugs, evolutionary activity statistics | 1989–1998 | Packard; Bedau, Packard, Snyder | SPEC SRC? | DET (activity vs neutral shadow) NEG |
| fam-018 | Cosmos | 1996–1999 | T. Taylor | thesis, SRC? | NEG (analysed failure of open-endedness) |
| fam-019 | Geb | 1998–2006 | Channon | SRC? | DET-passing claim (activity class 4) — test as specimen or NEG |
| fam-020 | Aevol (genome structure, noncoding DNA, complexity ratchet) | 2006– | Knibbe, Beslon, Parsons, Liard, Rouzaud-Cornabas | SRC DATA? | ROB CONT NEUT META |
| fam-021 | Stringmol automata chemistry | 2010– | Hickinbotham, Clark, Stepney, Clarke, Nellis, Pay, Young | SRC | ECO REACH |
| fam-022 | BFF / computational life (Brainfuck soups) | 2024 | Agüera y Arcas, Alakuijala, Mordvintsev et al. | SRC | REACH XR (modern replication of fam-014/015/016) |
| fam-023 | Push autoconstructive evolution (Pushpop, AutoPush) | 2001– | Spector, Robinson, Harrington | SRC? | META (evolving reproduction), COLLAPSE anomalies |
| fam-024 | Division Blocks | 2007 | Spector, Klein, Feinstein | SRC? | ENV MOD |
| fam-025 | Framsticks | 1996– | Komosinski, Ulatowski | binary + SDK | MOD REP |
| fam-026 | Polyworld (incl. driven-vs-passive complexity controls) | 1994–2011 | Yaeger; Yaeger, Sporns, Griffith | SRC | ECO DET (passive control) NEG (plateau) |
| fam-027 | Echo / Hidden Order | 1990s | Holland | SRC? (SFI) | ECO ENV |
| fam-028 | Sugarscape | 1996 | Epstein, Axtell | SPEC, reimpl. | ENV ECO NEG |
| fam-029 | Chromaria / open-ended conditions | 2014 | Soros, Stanley | SRC | META ECO |
| fam-030 | Long-term evolution experiment (biological; frozen fossil record; citrate replay; second-order selection) | 1988– | Lenski, Blount, Woods, Wiser et al. | DATA (public strains/seqs) | CONT META — CALIBRATION analogue for fork-by-reference |
| fam-031 | Phage λ OmpF innovation stepping stones (biological) | 2012 | Meyer, Lenski et al. | DATA | CONT NEUT — calibration analogue |

## A.2 Evolutionary computation core (GA / ES / EP / EDA)
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-040 | Royal Road functions, hitchhiking, RMHC beats GA | 1992–1994 | Mitchell, Forrest, Holland | SPEC | NEUT NEG DET (anomaly explained) |
| fam-041 | Hinton–Nowlan Baldwin effect; persistent question marks as drift | 1987; 1993 | Hinton, Nowlan; Harvey | SPEC | META NEG (anomaly = drift) — CALIBRATION |
| fam-042 | Messy GA, linkage learning, LLGA, cGA, BOA | 1989–2000s | Goldberg, Deb, Harik, Pelikan | SPEC SRC? | REP MOD |
| fam-043 | NK landscapes; ruggedness | 1987– | Kauffman, Levin | SPEC | NEG calibration |
| fam-044 | Adaptive operator probabilities; self-adaptive mutation in GAs | 1989–1990s | Davis; Bäck; Spears | SPEC | META |
| fam-045 | Hyper-heuristics; automated algorithm configuration | 2000s– | Burke et al.; Hutter, Hoos, Leyton-Brown | SRC | META search control |
| fam-046 | Coevolutionary pathologies: numbers game, mediocre stable states, loss of gradient | 1997–2001 | Watson, Pollack; Ficici, Pollack | SPEC SRC? | NEG cycling |
| fam-047 | Coevolving sorting networks with parasites | 1990 | Hillis | SPEC, SRC- (CM-2) | ECO META |
| fam-048 | HIFF, compositional evolution, symbiogenesis (SEAM) | 1998–2006 | Watson, Pollack, Hornby | SPEC SRC? | MOD DUP composition |
| fam-049 | CIAO plots; measuring coevolutionary progress | 1995 | Cliff, Miller | SPEC | DET |
| fam-050 | Local optima networks; landscape neutrality analyses | 2008– | Ochoa, Tomassini, Verel | SRC | DET REACH |

## A.3 Genetic programming / program evolution
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-060 | GP, ADFs, architecture-altering operations (gene duplication in GP) | 1992–1999 | Koza | SPEC (Lisp in books) | DUP MOD STATE (ADStorage) |
| fam-061 | Evolutionary module acquisition (GLiB compress/expand) | 1993 | Angeline, Pollack | SPEC | PROT MOD |
| fam-062 | Adaptive representation through learning (ARL) | 1994–1996 | Rosca, Ballard | SPEC | MOD REP |
| fam-063 | Constructional selection; evolution of evolvability in GP | 1994–1995 | Altenberg | SPEC | META DUP — foundational |
| fam-064 | Introns, effective fitness, explicitly defined introns, bloat as protection | 1995–1998 | Nordin, Banzhaf, Francone; Soule, Foster; Langdon, Poli | SPEC | ROB PROT NEUT DET (effective fitness) |
| fam-065 | Genotype–phenotype mapping in GP; neutral networks in GP | 1994–2006 | Banzhaf; Keller; Ebner, Shackleton, Shipman; Banzhaf, Leier | SPEC | NEUT REACH |
| fam-066 | Cartesian GP; neutrality helps / harms dispute | 2000–2006 | Miller, Thomson; Yu, Miller; Vassilev; Collins | SRC | NEUT (disputed effect — replication target) |
| fam-067 | Self-modifying CGP | 2007– | Harding, Miller, Banzhaf | SRC? | REP META (self-modification) |
| fam-068 | Indexed memory / PADO / mental models in GP | 1994 | Teller | SPEC | STATE |
| fam-069 | Grammatical evolution; code degeneracy | 1998– | O'Neill, Ryan | SRC | NEUT REP |
| fam-070 | Lexicase selection; hyperselection; specialists | 2012– | Spector, Helmuth, McPhee, La Cava | SRC | PROT search control; anomaly (hyperselection) |
| fam-071 | Ancestry collapse in GP populations | 1999 | McPhee, Hopper | SPEC | CONT DET |
| fam-072 | GP tree-shape lattice / structural reachability limits | 2001–2005 | Daida et al. | SPEC | REACH DET |
| fam-073 | Robustness, evolvability, accessibility in linear GP (phenotype networks) | 2011–2012 | Hu, Banzhaf, Ochoa, Payne, Moore | SRC | REACH NEUT DET |
| fam-074 | Genealogy visualisation / hash-based lineage in GP | 2015– | Burlacu, Kronberger, Affenzeller | SRC | DET |
| fam-075 | Ecological + phylogenetic metrics for GP; MODES toolbox | 2018–2022 | Dolson, Banzhaf, Ofria; Hernandez, Lalejini | SRC | DET |
| fam-076 | SignalGP / tag-based regulation / plasticity stabilises evolution | 2018–2021 | Lalejini, Ofria, Ferguson, Grant | SRC DATA (OSF) | STATE META ROB |
| fam-077 | Semantic GP; geometric semantic operators | 2009– | Krawiec, Moraglio, Vanneschi | SRC | REP |
| fam-078 | Tag-based modularity in GP | 2011 | Spector, Martin, Harrington, Helmuth | SRC? | MOD |
| fam-079 | Program synthesis by evolution benchmarks; algorithm evolution (AutoML-Zero) | 2015–2020 | Helmuth; Real, Liang, So, Le | SRC | REP META (modern end) |

## A.4 Neuroevolution / evolving topology / evolving learning
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-090 | Early GA+NN; grammar encoding | 1989–1990 | Miller, Todd, Hegde; Montana, Davis; Kitano | SPEC | REP |
| fam-091 | Evolving learning rules (genetic connectionism; synaptic rule learning) | 1990–1992 | Chalmers; Bengio, Bengio, Cloutier | SPEC | META — learning-to-learn precursor |
| fam-092 | Evolutionary reinforcement learning (ERL); Baldwin + shielding | 1991 | Ackley, Littman | SPEC SRC- | META STATE ECO |
| fam-093 | Learning and evolution in changing environments | 1994–1996 | Nolfi, Elman, Parisi; Todd, Miller | SPEC | META |
| fam-094 | Cellular encoding (developmental, modular ANN) | 1994 | Gruau | SPEC SRC? | MOD REP |
| fam-095 | GNARL topology evolution | 1994 | Angeline, Saunders, Pollack | SPEC | REP |
| fam-096 | SANE / ESP / CoSyNE (cooperative coevolution of neurons) | 1996–2008 | Moriarty, Gomez, Miikkulainen | SRC | MOD ECO |
| fam-097 | NEAT (complexification, speciation protection, historical markings; ablations) | 2002 | Stanley, Miikkulainen | SRC | PROT REP DUP — CALIBRATION (ablation table) |
| fam-098 | CPPN / HyperNEAT / ES-HyperNEAT / adaptive HyperNEAT | 2007–2012 | Stanley, D'Ambrosio, Gauci, Risi | SRC | REP MOD META |
| fam-099 | Evolving reusable neural modules | 2004 | Reisinger, Stanley, Miikkulainen | SPEC | MOD |
| fam-100 | GasNets; landscape neutrality of GasNets | 1998–2002 | Husbands, Smith, Philippides, O'Shea | SPEC | REP ROB META (evolvability measured) |
| fam-101 | CTRNN learning without synaptic plasticity; associative learning dynamics | 1994–2007 | Yamauchi, Beer; Phattanasri, Chiel, Beer; Izquierdo | SPEC SRC? | STATE |
| fam-102 | Plastic neurocontrollers evolve faster; neuromodulated plasticity | 2000–2008 | Floreano, Urzelai; Soltoggio, Bullinaria, Mattiussi, Dürr | SPEC SRC? | META |
| fam-103 | Evolved RL-like signals in bee models | 2002 | Niv, Joel, Meilijson, Ruppin | SPEC | META |
| fam-104 | Connection-cost modularity; modularity helps learn without forgetting | 2013–2015 | Clune, Mouret, Lipson; Ellefsen | SRC (Sferes2) | MOD META — CALIBRATION |
| fam-105 | Novelty search; abandoning objectives | 2008–2011 | Lehman, Stanley | SRC | META search control |
| fam-106 | MAP-Elites; quality diversity; behavioural repertoires | 2015– | Mouret, Clune; Cully; Pugh, Soros, Stanley | SRC | REACH MOD |
| fam-107 | Minimal criterion coevolution | 2017 | Brant, Stanley | SRC | ECO REACH |
| fam-108 | POET / Enhanced POET (environment–agent coevolution; stepping stones measured) | 2019–2020 | Wang, Lehman, Clune, Stanley | SRC | ECO REACH CONT — measured "unreachable by direct optimisation" |
| fam-109 | Evolvability search; evolvability is inevitable; reconciling explanations | 2013–2016 | Lehman, Stanley; Wilder; Mengistu, Clune | SRC | META |
| fam-110 | Extinction events accelerate evolution | 2015 | Lehman, Miikkulainen | SRC? | META perturbation |
| fam-111 | Surprising creativity of digital evolution (community anecdote collection) | 2018 | Lehman, Clune, Misevic + 50 authors | SPEC | anomaly source for D |
| fam-112 | Meta-learning precursors (self-referential learning; LSTM meta-learning) | 1987–2001 | Schmidhuber; Hochreiter, Younger, Conwell | SPEC SRC? | META |

## A.5 Cellular automata / self-reproduction / computational mechanics
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-120 | Self-reproducing loops (Langton, Byl, Reggia) | 1984–1993 | Langton; Byl; Reggia, Armentrout, Chou, Peng | SPEC | STATE REACH |
| fam-121 | Emergence of replicators from random CA states; GA discovery of replicators | 1997 | Chou, Reggia; Lohn, Reggia | SPEC | REACH rare-event |
| fam-122 | Evoloop / SDSR loop; complex genetic evolution of CA replicators | 1998–2004 | Sayama; Salzberg, Sayama | SRC? | ECO CONT DUP |
| fam-123 | Edge of chaos: λ; adaptation toward the edge; failed replication | 1988–1993 | Langton; Packard; Mitchell, Hraber, Crutchfield | SPEC | NEG DET (failed replication) |
| fam-124 | EvCA: GA-evolved CA for density classification & synchronisation; epochs; particle-based strategies | 1993–1999 | Mitchell, Crutchfield, Das, Hraber, Hanson, Hordijk | SPEC (rule tables published) SRC? | CONT REACH REP DET (computational mechanics) — FIRST-EXPERIMENT CANDIDATE |
| fam-125 | Coevolved / GP-evolved density rules; impossibility bound | 1995–2008 | Juillé, Pollack; Andre, Bennett, Koza; Land, Belew; Wolz, de Oliveira | SPEC | XR (same motif, three search physics) CALIBRATION (bound) |
| fam-126 | Computational mechanics; ε-machines; particle catalogues | 1989– | Crutchfield, Young, Hanson, Shalizi | SRC (CMPy) | DET |
| fam-127 | Basins of attraction; DDLab; Z-parameter | 1992– | Wuensche, Lesser | SRC | DET REACH |
| fam-128 | Schema redescription / canalisation in automata networks | 2011–2013 | Marques-Pita, Rocha | SRC? | ROB REP |
| fam-129 | Cellular programming; non-uniform CA | 1996–1997 | Sipper | SPEC | ECO |
| fam-130 | Evolved glider-supporting rules | 2003– | Sapin, Bailleux, Chabrier | SPEC | REACH |
| fam-131 | Lenia / Flow Lenia; neural CA | 2019– | Chan; Plantec et al.; Mordvintsev et al. | SRC | NEG? (novelty vs accumulation) ROB (regeneration) |

## A.6 Artificial chemistry / origin-of-organisation models
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-140 | AlChemy (λ-calculus chemistry; levels 0/1/2; "tape played twice") | 1991–1994 (revisited 2020s) | Fontana; Fontana, Buss | SRC? (re-released, verify) | MOD CONT DET (organisation levels) |
| fam-141 | Matrix / binary-string chemistries | 1993–2001 | Banzhaf; Dittrich, Banzhaf | SPEC | REACH |
| fam-142 | Chemical organisation theory | 2007 | Dittrich, Speroni di Fenizio | SRC | DET |
| fam-143 | Autocatalytic sets; RAF detection | 1986– | Kauffman; Farmer, Bagley; Hordijk, Steel | SRC | DET REACH |
| fam-144 | Squirm3 evolvable replicators | 2002 | Hutton | SRC? | REACH ECO |
| fam-145 | Machines-and-tapes active mutation; Typogenetics | 1979–1995 | Hofstadter; Ikegami, Hashimoto | SPEC | META |
| fam-146 | Combinatory chemistry | 2020 | Kruszewski, Mikolov | SRC | REACH XR |
| fam-147 | RNA neutral networks; smoothness within ruggedness; relay series; shape-space continuity | 1994–1998 | Schuster, Fontana, Stadler, Hofacker; Huynen | SRC (ViennaRNA; parameter-set caveat) | NEUT CONT REACH — RUNNER-UP FIRST EXPERIMENT |
| fam-148 | Robustness ↔ evolvability (RNA, proteins, GRNs) | 2005–2008 | A. Wagner; Draghi | SRC? | ROB META |
| fam-149 | Arrival of the frequent; simplicity bias in GP maps | 2008–2018 | Cowperthwaite et al.; Schaper, Louis; Dingle, Camargo, Louis | SRC | REACH REP |

## A.7 Evolvability, modularity, development, GRNs
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-160 | Complex adaptations and the evolution of evolvability | 1996 | G. Wagner, Altenberg | SPEC | META framing |
| fam-161 | Modularly varying goals → modularity, motifs; varying environments speed evolution; facilitated variation | 2005–2008 | Kashtan, Alon; Kashtan, Noor; Parter | SRC? | MOD META — CALIBRATION |
| fam-162 | Origin of modular variation | 2002 | Lipson, Pollack, Suh | SPEC | MOD |
| fam-163 | Evolution of evolvability in GRNs (mutational priming) | 2008 | Crombach, Hogeweg | SRC? | META NEUT |
| fam-164 | Evolvability as selectable trait | 2004 | Earl, Deem | SPEC | META |
| fam-165 | Evolution of genetic representations; σ-evolution (neutral traits change exploration distribution) | 2003 | Toussaint | SPEC | NEUT REP META — direct §14 shape |
| fam-166 | Fluctuation–response; noise, robustness and evolvability in GRN dynamics | 2003–2007 | Sato, Ito, Yomo, Kaneko; Kaneko | SPEC SRC? | ROB META (Vg–Vip) |
| fam-167 | Isologous diversification; coupled-map differentiation | 1990s | Kaneko, Yomo; Furusawa | SPEC | STATE MOD (differentiation without genetic change) |
| fam-168 | Evolution as learning: developmental memory; how evolution learns to generalise | 2014–2017 | Watson, Szathmáry; Kouvaris, Clune, Kounios, Brede, Watson | SRC? | META REP |
| fam-169 | Global adaptation in networks of selfish components; self-modelling CAS | 2011 | Watson, Mills, Buckley | SPEC | STATE META (associative memory from local adaptation) |
| fam-170 | Developmental encodings, regeneration, French flag; artificial ontogeny | 1990s–2000s | Dellaert, Beer; Eggenberger; Bongard, Pfeifer; Miller; Federici, Downing | SPEC SRC? | ROB REP |
| fam-171 | Measuring modularity, regularity, hierarchy in generative representations (GENRE) | 2003–2005 | Hornby | SPEC | MOD DET |
| fam-172 | Major evolutionary transitions models | 1995– | Maynard Smith, Szathmáry; Michod; Ratcliff (yeast, biological) | SPEC | MOD ECO |
| fam-173 | Iterated learning; transmission bottleneck → compositionality | 2001– | Kirby; Smith; Brighton | SPEC SRC? | REP (bottleneck-driven representation change) |
| fam-174 | Language games; shared external symbols | 1995–2005 | Steels; Batali; Cangelosi, Parisi | SRC? | ENV STATE |
| fam-175 | Evolution, learning and culture (cumulative culture models) | 1990– | Belew; Boyd, Richerson | SPEC | META ENV |
| fam-176 | Value of information / bet hedging in varying environments (information-theoretic) | 2005–2011 | Kussell, Leibler; Rivoire, Leibler | SPEC | META ROB |

## A.8 Evolvable hardware / evolutionary robotics / physical substrates
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-190 | Intrinsic evolution on XC6216 (tone discriminator; disconnected-yet-necessary cells) | 1996–1998 | A. Thompson | thesis DATA? bitstreams? hardware obsolete | UNEXPLAINED anomaly; physics irreproducible (detector-archaeology case) |
| fam-191 | The evolved radio (circuit exapts environmental RF) | 2002 | Bird, Layzell | SPEC | ENV exaptation anomaly |
| fam-192 | Evolvable motherboard; unconventional substrates (liquid crystal) | 1998–2005 | Layzell; Harding, Miller | SPEC | REACH substrate dependence |
| fam-193 | Evolved virtual creatures; coevolved competition; physics exploits | 1994 | Sims | SRC- (reimpl.) | ECO NEG (cycling) anomaly (exploits) |
| fam-194 | GOLEM; self-modelling robots | 2000–2006 | Lipson, Pollack; Bongard, Zykov | SRC? | REP STATE |
| fam-195 | Predator–prey coevolution cycling; Hall of Fame | 1997–2000 | Nolfi, Floreano; Rosin, Belew | SPEC | NEG cycling |
| fam-196 | Minimal simulations; SAGA | 1992–1998 | Jakobi; Harvey | SPEC | ROB |
| fam-197 | Morphological change facilitates learning | 2011 | Bongard | SRC? | META |
| fam-198 | Soft robots via CPPN; morphological innovation protection | 2013–2018 | Cheney, Clune, Lipson; Cheney, Bongard | SRC | PROT REACH |

## A.9 Adaptive learning systems / self-modifying computation (non-evolutionary but in scope)
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-210 | Schema mechanism (synthetic items invented on prediction failure) | 1991 | Drescher | SPEC, reimpl. (Chaput; Guerin) | REP STATE — failure-driven new hidden variables |
| fam-211 | Anticipatory classifier systems (ACS, ACS2) | 1998–2002 | Stolzmann; Butz | SRC | STATE REP |
| fam-212 | XCS / ZCS accuracy-based classifiers | 1994–1995 | Wilson | SRC | REP |
| fam-213 | Knowledge growth in an artificial animal (animat problem) | 1985 | Wilson | SPEC | STATE |
| fam-214 | Fast-weight memories; learning to control them | 1992 | Schmidhuber | SPEC | STATE META |
| fam-215 | Gödel machine / OOPS / Levin search (self-referential) | 1990s–2004 | Schmidhuber | SPEC SRC? | META (conceptual) |
| fam-216 | Stigmergy; ant colony optimisation | 1991– | Dorigo; Bonabeau, Theraulaz | SRC | ENV (pheromone as persistent environment) NEG? |
| fam-217 | Swarm chemistry with human-in-the-loop novelty | 2009–2011 | Sayama | SRC | NEG (novelty w/o accumulation) |
| fam-218 | Reservoir-like evolved dynamics; evolving ESN topology | 2000s | Jaeger (ESN); various | SRC | STATE REP |

---

## Coverage accounting (this version)
- Families listed: ~120 across 10 traditions. Directive target 100–200: reached in count, NOT in verification.
- Thin or missing strata (to enumerate next, not sample): evolutionary game dynamics beyond IPD (Lindgren 1991 belongs under A.2/ECO and is a first-experiment runner-up: `fam-051` to be added), swarm systems, multi-agent simulation beyond Sugarscape/Echo, hyper-heuristics depth, unconventional computation beyond LC, cumulative-culture models depth, Japanese ALife lineage (Ikegami, Kaneko, Suzuki) depth, Latin-American CA lineage (de Oliveira), Eastern-European ES lineage.
- Known bias of this seed: it over-represents anglophone, well-cited work, i.e. exactly the fame bias §18 forbids in ranking. Correct it during stratified enumeration by decade × substrate × venue (workshop/tech-report/thesis strata first).

### Addendum rows (added same day, before commit)
| id | system | years | investigators | artifacts | lens |
|---|---|---|---|---|---|
| fam-051 | Iterated Prisoner's Dilemma with variable-length memory genomes (gene-duplication operator; punctuated stasis; extinctions) | 1991–1994 | Lindgren; Lindgren, Nordahl | SPEC (fully specified), SRC- | DUP NEUT STATE CONT — RUNNER-UP FIRST EXPERIMENT |
| fam-052 | Axelrod's GA tournament of IPD strategies | 1987 | Axelrod | SPEC | ECO |
| fam-053 | Spatial games, homeochaos, artificial food webs | 1992–1994 | Nowak, May; Ikegami, Kaneko; Lindgren, Nordahl | SPEC | ECO STATE |
| fam-054 | Bedau–Packard–Snyder long-term dynamics classes (1–4); "no artificial system reaches class 4" | 1998 | Bedau, Snyder, Packard | SPEC | DET NEG — CALIBRATION |
