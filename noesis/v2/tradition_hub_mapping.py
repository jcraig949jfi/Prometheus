"""
Tradition Dimension — Map ethnomathematics systems to impossibility hubs.
Creates cross_domain_edges linking each ethnomathematical system to the hub(s) it confronts.

Logic: each tradition's structural operations implicitly confront specific impossibilities.
A calendar system confronts incommensurability. A tuning system confronts the Pythagorean comma.
A number system confronts representational limits. A geometric system confronts tiling obstructions.
"""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# Load all ethnomathematics entries
ethno_rows = db.execute('''
    SELECT system_id, tradition, system_name, description, key_operations,
           structural_features, enriched_primitive_vector
    FROM ethnomathematics ORDER BY system_id
''').fetchall()

print(f"Ethnomathematics entries: {len(ethno_rows)}")

# Get max edge_id
max_eid = db.execute('SELECT COALESCE(MAX(edge_id), 0) FROM cross_domain_edges').fetchone()[0]
next_eid = max_eid + 1

# ============================================================
# MAPPING TABLE: system_id -> [(hub_id, damage_operator, reason)]
# ============================================================
# Explicit mappings based on domain knowledge of what each system confronts.

EXPLICIT_MAPPINGS = {
    # ===== CALENDARS — confront incommensurability =====
    'ANTIKYTHERA_MECHANISM': [
        ('IMPOSSIBILITY_CALENDAR', 'COMPOSE', 'Gear ratios mechanize the incommensurability of lunar/solar/zodiacal cycles via physical composition'),
        ('FORCED_SYMMETRY_BREAK', 'PARTITION', 'Partitions celestial cycles into discrete gear trains, each handling one period'),
    ],
    'MATH_SYS_114': [  # Tibetan Calendar
        ('IMPOSSIBILITY_CALENDAR', 'COMPOSE', 'Tibetan lunisolar calendar composes lunar months with solar year via intercalation'),
        ('FORCED_SYMMETRY_BREAK', 'DISTRIBUTE', 'Distributes incommensurability across intercalary month insertions'),
    ],
    'TIBETAN_ASTRONOMICAL_CALCULUS': [
        ('IMPOSSIBILITY_CALENDAR', 'COMPOSE', 'Lunisolar cycle computation addresses calendar incommensurability'),
    ],
    'MATH_SYS_116': [  # Balinese Pawukon
        ('IMPOSSIBILITY_CALENDAR', 'PARTITION', 'Multiple simultaneous interlocking cycles partition time without reconciling to solar year'),
        ('FORCED_SYMMETRY_BREAK', 'TRUNCATE', 'Truncates solar alignment entirely; accepts pure cyclical partition'),
    ],
    'ETHIOPIAN_CALENDAR_ARITHMETIC': [
        ('IMPOSSIBILITY_CALENDAR', 'TRUNCATE', 'Ethiopian calendar accepts 5-6 epagomenal days — truncated remainder of solar year'),
    ],
    'MEDIEVAL_EUROPEAN_COMPUTUS': [
        ('IMPOSSIBILITY_CALENDAR', 'COMPOSE', 'Computus composes lunar cycle (Metonic) with solar cycle (Julian/Gregorian) for Easter dating'),
        ('FORCED_SYMMETRY_BREAK', 'HIERARCHIZE', 'Hierarchical rules (golden number, epact, dominical letter) layer corrections'),
    ],
    'MAYAN_VIGESIMAL': [
        ('IMPOSSIBILITY_CALENDAR', 'PARTITION', 'Dual-gear: 365-day Haab + 260-day Tzolkin. Calendar Round = LCM = 18,980 days'),
    ],
    'MATH_SYS_215': [  # Mayan Calendar Round
        ('IMPOSSIBILITY_CALENDAR', 'PARTITION', 'LCM of 260 and 365 creates 52-year cycle; partitions time into dual interlocking grids'),
        ('FORCED_SYMMETRY_BREAK', 'COMPOSE', 'Composes two incommensurate cycles into a single Calendar Round'),
    ],
    'MAYAN_ECLIPSE_TABLE_ALGORITHMS': [
        ('IMPOSSIBILITY_CALENDAR', 'COMPOSE', 'Eclipse tables compose lunar and solar periods to predict occurrences'),
        ('FORCED_SYMMETRY_BREAK', 'TRUNCATE', 'Truncates continuous orbital dynamics to tabular lookup at discrete intervals'),
    ],
    'MATH_SYS_112': [  # Korean Joseon
        ('IMPOSSIBILITY_CALENDAR', 'COMPOSE', 'Joseon astronomical calculations compose lunar/solar cycles'),
    ],

    # ===== TUNING SYSTEMS — confront the Pythagorean comma =====
    'ETHNOMUSIC_PYTHAGOREAN_TUNING': [
        ('IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'CONCENTRATE', 'Wolf interval concentrates the comma in one spot'),
        ('FORCED_SYMMETRY_BREAK', 'CONCENTRATE', 'All damage in one interval; others remain pure'),
    ],
    'MATH_SYS_134': [  # Pythagorean Tuning
        ('IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'CONCENTRATE', 'Wolf interval absorbs the comma'),
        ('FORCED_SYMMETRY_BREAK', 'CONCENTRATE', 'Damage concentrated in rarely-used intervals'),
    ],
    'EQUAL_TEMPERAMENT_SYSTEM': [
        ('IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'DISTRIBUTE', 'Distributes comma equally across all 12 semitones'),
        ('FORCED_SYMMETRY_BREAK', 'QUANTIZE', 'Quantizes pitch space to equal logarithmic grid'),
    ],
    'MATH_SYS_135': [  # Equal Temperament
        ('IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'DISTRIBUTE', 'Uniform distribution of comma across all intervals'),
        ('FORCED_SYMMETRY_BREAK', 'QUANTIZE', 'Logarithmic quantization of continuous pitch'),
    ],
    'JUST_INTONATION_SYSTEM': [
        ('IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'TRUNCATE', 'Keeps pure ratios for some intervals, accepts that modulation breaks tuning'),
        ('FORCED_SYMMETRY_BREAK', 'PARTITION', 'Partitions keys into "good" and "bad" — damage isolated by key choice'),
    ],
    'MATH_SYS_136': [  # Gamelan Tuning
        ('IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'RANDOMIZE', 'Each gamelan has unique non-standardized tuning; randomizes across instruments'),
        ('FORCED_SYMMETRY_BREAK', 'TRUNCATE', 'Non-octave scales truncate the octave equivalence assumption'),
    ],

    # ===== FRACTION / NUMBER SYSTEMS — confront representation limits =====
    'EGYPTIAN_FRACTIONS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Unit fractions can approximate sqrt(2) but never represent it exactly; truncated representation'),
        ('IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'TRUNCATE', 'Greedy algorithm produces finite approximations; algebraic closure not achievable'),
    ],
    'MATH_SYS_202': [  # Egyptian Unit Fraction Decomposition
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Greedy decomposition truncates to finite sum of unit fractions'),
    ],
    'MATH_SYS_201': [  # Egyptian Duplation Multiplication
        ('BINARY_DECOMP_RECOMP', 'COMPOSE', 'Multiplication via binary decomposition is the canonical spoke of this hub'),
    ],
    'BABYLONIAN_SEXAGESIMAL': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'YBC 7289 tablet: sqrt(2) approximated to 6 sexagesimal places; truncated representation'),
    ],
    'MATH_SYS_203': [  # Babylonian Reciprocal Tables
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Reciprocal tables for regular numbers only; irregular numbers truncated/approximated'),
    ],
    'MATH_SYS_204': [  # Babylonian Square Root
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Iterative method (Heron) gives rational approximations; never reaches exact irrational'),
        ('BROUWER_FIXED_POINT', 'CONCENTRATE', 'Newton/Heron iteration concentrates on fixed point'),
    ],
    'ROMAN_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Non-positional system cannot represent fractions at all; truncates to integers'),
    ],

    # ===== YORUBA — subtractive composition confronts commutativity =====
    'YORUBA_BASE20': [
        ('IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT', 'DISTRIBUTE', 'Subtractive vigesimal: 45 = (3*20) - (10+5). Non-commutative composition of operations'),
    ],
    'YORUBA_BASE_20': [
        ('IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT', 'DISTRIBUTE', 'Subtraction from landmarks: order matters, operations do not commute'),
    ],
    'YORUBA_VIGESIMAL': [
        ('IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT', 'DISTRIBUTE', 'Subtractive base-20 makes operation order significant'),
    ],
    'YORUBA_IFA_COMBINATORICS': [
        ('CONDORCET_PARADOX', 'RANDOMIZE', '256 odu generated by binary divination; randomized selection from combinatorial space'),
    ],

    # ===== TSHOKWE SONA — Eulerian path obstructions =====
    'TSHOKWE_SONA': [
        ('EULER_CHARACTERISTIC_OBSTRUCTION', 'COMPOSE', 'Sona drawings trace Euler-like paths; odd-degree vertices create obstruction to single-stroke drawing'),
        ('HAIRY_BALL', 'PARTITION', 'Closed path patterns on surfaces confront topological constraints on vector fields'),
    ],
    'MATH_SYS_213': [  # Tshokwe Sona Eulerian
        ('EULER_CHARACTERISTIC_OBSTRUCTION', 'COMPOSE', 'Eulerian path construction directly confronts graph-theoretic obstructions'),
        ('EULER_POLYHEDRON_OBSTRUCTION', 'COMPOSE', 'Path counting on planar graphs relates to V-E+F = 2'),
    ],

    # ===== ABORIGINAL SYSTEMS — confront spatial/cognitive limits =====
    'ABORIGINAL_KINSHIP_ALGEBRA': [
        ('SOCIAL_CHOICE_IMPOSSIBILITY', 'PARTITION', 'Kinship moieties partition society into marriage classes; Arrow-like impossibility of satisfying all rules'),
        ('BURNSIDE_IMPOSSIBILITY', 'SYMMETRIZE', 'Kinship algebra forms cyclic/dihedral groups; Burnside counting applies to symmetry orbits'),
    ],
    'ABORIGINAL_SONGLINE_NAV': [
        ('IMPOSSIBILITY_MAP_PROJECTION', 'COMPOSE', 'Songlines encode 3D geography into 1D oral sequences; lossy projection from surface to song'),
        ('IMPOSSIBILITY_CALENDAR', 'RANDOMIZE', 'Aboriginal seasonal calendars use elastic time tied to ecological markers, not fixed periods'),
    ],

    # ===== DIVINATION SYSTEMS — confront stochastic limits =====
    'BAMANA_BINARY_DIVINATION': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'RANDOMIZE', 'Binary generation creates discrete random states; confronts continuous-discrete boundary'),
    ],
    'BAMANA_DIVINATION': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'RANDOMIZE', 'Binary divination system generates discrete outcomes from continuous sand process'),
    ],
    'BAMANA_SAND_DIVINATION': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Recursive parity operations always terminate — bounded recursion avoids halting problem'),
        ('IMPOSSIBILITY_NK_FITNESS_LANDSCAPE', 'RANDOMIZE', 'Binary landscape of divination states; randomized exploration of outcome space'),
    ],
    'I_CHING_BINARY': [
        ('CONDORCET_PARADOX', 'RANDOMIZE', '64 hexagrams cover binary state space; randomized oracle avoids cyclic preference'),
    ],

    # ===== ALGEBRAIC SYSTEMS — confront solvability limits =====
    'AL_KHWARIZMI_ALGEBRA': [
        ('IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'TRUNCATE', 'Al-jabr solves degree 1-2; the method truncates at quadratics — cannot reach quintics'),
        ('ALGEBRAIC_COMPLETION', 'COMPOSE', 'Completion (al-jabr) + reduction (al-muqabala) = canonical spoke'),
    ],
    'OMAR_KHAYYAM_CUBICS': [
        ('IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'TRUNCATE', 'Geometric conic intersection solves cubics; method truncates at degree 3'),
        ('GALOIS_UNSOLVABILITY', 'TRUNCATE', 'Geometric methods cannot express radical solutions — truncated at what geometry allows'),
    ],
    'MATH_SYS_212': [  # Geometric Cubic Solutions
        ('IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'TRUNCATE', 'Conic intersection method stops at degree 3'),
        ('GALOIS_UNSOLVABILITY', 'TRUNCATE', 'Geometric construction inherently limited in algebraic degree'),
    ],
    'EUCLID_BOOK_X_ALGEBRA': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'HIERARCHIZE', 'Euclid classifies irrationals into hierarchy of types; confronts incommensurability head-on'),
        ('IMPOSSIBILITY_TRANSCENDENCE_E_PI', 'TRUNCATE', 'Classification system cannot reach transcendentals; truncated at algebraic irrationals'),
    ],
    'MATH_SYS_206': [  # Diophantine equations
        ('MATIYASEVICH_HILBERT10', 'TRUNCATE', 'Specific Diophantine problems solvable; general decidability impossible (Hilbert 10th)'),
        ('FERMAT_LAST_THEOREM', 'TRUNCATE', 'Seeks integer solutions to polynomial equations; FLT says x^n+y^n=z^n has none for n>2'),
    ],
    'MATH_SYS_210': [  # Bhaskara Chakravala
        ('IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'COMPOSE', 'Cyclic method composes iterative steps to solve Pell equation — algebraic composition'),
    ],

    # ===== INFINITY / LIMITS — confront foundational impossibilities =====
    'JAIN_INFINITY': [
        ('CANTOR_DIAGONALIZATION', 'HIERARCHIZE', 'Jain classification of 5 types of infinity anticipates transfinite hierarchy'),
        ('FOUNDATIONAL_IMPOSSIBILITY', 'PARTITION', 'Distinguishing finite/infinite/infinitely-infinite partitions the foundational landscape'),
    ],
    'SURREAL_NUMBERS': [
        ('CANTOR_DIAGONALIZATION', 'EXTEND', 'Surreals extend the number line past all ordinals; confronts Cantor by going further'),
        ('FOUNDATIONAL_IMPOSSIBILITY', 'EXTEND', 'Recursive construction extends number system beyond ZFC-standard reals'),
    ],
    'SURRREAL_NUMBERS': [
        ('CANTOR_DIAGONALIZATION', 'EXTEND', 'Surreal numbers include infinitesimals and transfinites'),
    ],
    'KERALA_SCHOOL': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Infinite series for pi/trig truncated to finite terms for computation'),
        ('IMPOSSIBILITY_TRANSCENDENCE_E_PI', 'TRUNCATE', 'Series converge to transcendentals but each partial sum is rational — truncated rationality'),
    ],
    'KERALA_SERIES': [
        ('IMPOSSIBILITY_TRANSCENDENCE_E_PI', 'TRUNCATE', 'Madhava series for pi converges but each truncation is rational'),
    ],
    'MATH_SYS_205': [  # Eudoxus Method of Exhaustion
        ('IMPOSSIBILITY_SQUARING_CIRCLE', 'TRUNCATE', 'Method of exhaustion approximates areas but cannot square the circle exactly'),
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Geometric approximation truncates at finite refinement'),
    ],
    'MATH_SYS_105': [  # Al-Kashi Decimal Expansion
        ('IMPOSSIBILITY_TRANSCENDENCE_E_PI', 'TRUNCATE', 'Computed pi to 16 decimal places — truncated representation of transcendental'),
    ],
    'MATH_SYS_211': [  # Al-Kashi Decimal Expansion Algorithms
        ('IMPOSSIBILITY_TRANSCENDENCE_E_PI', 'TRUNCATE', 'High-precision but always truncated decimal expansion of pi'),
    ],

    # ===== SYMMETRY SYSTEMS — confront crystallographic/topological limits =====
    'NAVAJO_SYMMETRY_WEAVING': [
        ('IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PARTITION', 'Weaving constrains to 2D wallpaper groups; restricted to the 17 allowed symmetries'),
        ('PHYS_SYMMETRY_CONSTRUCTION', 'SYMMETRIZE', 'Physical weaving grid forces discrete symmetry groups'),
    ],
    'MATH_SYS_121': [  # Navajo Symmetry Systems
        ('IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PARTITION', 'Sand painting symmetries partition into allowed discrete symmetry groups'),
    ],
    'MATH_SYS_122': [  # Pomo Basket Geometry
        ('IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PARTITION', 'Basket weaving patterns partition into allowed 2D symmetry types'),
        ('PHYS_SYMMETRY_CONSTRUCTION', 'SYMMETRIZE', 'Cylindrical basket geometry constrains to frieze groups'),
    ],
    'ISLAMIC_MUQARNAS_GEOMETRY': [
        ('IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'EXTEND', 'Muqarnas achieve quasi-5-fold symmetry by extending to 3D — bypassing 2D restriction'),
        ('PHYS_SYMMETRY_CONSTRUCTION', 'COMPOSE', '3D honeycomb from modular units composes small symmetries into large pattern'),
    ],
    'JAPANESE_SANGAKU': [
        ('IMPOSSIBILITY_SQUARING_CIRCLE', 'TRUNCATE', 'Sangaku problems compute pi-related quantities via geometric constructions; truncated'),
    ],
    'JAPANESE_WASAN': [
        ('IMPOSSIBILITY_SQUARING_CIRCLE', 'TRUNCATE', 'Wasan tradition derived circle-packing results truncated to rational approximations'),
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Geometric methods produce approximations of irrationals'),
    ],
    'JAPANESE_WASAN_SANGAKU': [
        ('IMPOSSIBILITY_SQUARING_CIRCLE', 'TRUNCATE', 'Temple geometry problems involving circle areas/perimeters confront pi irrationality'),
    ],

    # ===== FRACTAL / RECURSIVE — confront scaling limits =====
    'AFRICAN_FRACTAL_VILLAGE_LAYOUTS': [
        ('RECURSIVE_SPATIAL_EXTENSION', 'COMPOSE', 'Fractal settlement layouts compose recursive scaling rules'),
        ('IMPOSSIBILITY_NK_FITNESS_LANDSCAPE', 'HIERARCHIZE', 'Hierarchical settlement structure navigates multi-scale fitness landscape'),
    ],
    'MATH_SYS_120': [  # Shona Fractal Architecture
        ('RECURSIVE_SPATIAL_EXTENSION', 'COMPOSE', 'Recursive geometric patterns in settlement layout'),
    ],

    # ===== CRYPTANALYSIS — confronts information limits =====
    'AL_KINDI_CRYPTANALYSIS': [
        ('SHANNON_CAPACITY', 'REDUCE', 'Frequency analysis reduces ciphertext to plaintext by exploiting information redundancy'),
        ('IMPOSSIBILITY_INFORMATION_BOTTLENECK', 'REDUCE', 'Cipher analysis compresses message through statistical bottleneck'),
    ],
    'AL_KINDI_CRYPTO': [
        ('SHANNON_CAPACITY', 'REDUCE', 'Frequency analysis exploits non-uniform distribution to break cipher'),
    ],
    'AL_KINDI_CRYPTOANALYSIS': [
        ('ONE_TIME_PAD_NECESSITY', 'DISTRIBUTE', 'Frequency analysis works because key is shorter than message; OTP would defeat it'),
        ('SHANNON_CAPACITY', 'REDUCE', 'Statistical reduction of ciphertext exploits channel capacity limits'),
    ],

    # ===== COMPUTING DEVICES — confront computation limits =====
    'MATH_SYS_127': [  # Jacquard Loom
        ('HALTING_PROBLEM', 'TRUNCATE', 'Punch card programs are finite; halting is trivially decidable for finite programs'),
        ('CHURCH_UNDECIDABILITY', 'TRUNCATE', 'Finite state machine (loom) = decidable fragment of computation'),
    ],
    'MATH_SYS_216': [  # Jacquard Loom Binary Control
        ('HALTING_PROBLEM', 'TRUNCATE', 'Binary punch cards define finite programs; always halt'),
    ],
    'MATH_SYS_128': [  # Difference Engine
        ('HALTING_PROBLEM', 'TRUNCATE', 'Finite polynomial table computation always terminates'),
        ('IMPOSSIBILITY_UNIVERSAL_APPROXIMATION_RATE_IMPOSSIBILITY', 'TRUNCATE', 'Polynomial tables approximate functions at fixed polynomial rate'),
    ],
    'PASCALINE': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Mechanical addition always terminates — finite bounded computation'),
    ],
    'LEIBNIZ_WHEEL': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Mechanical multiplication always terminates'),
    ],
    'NAPERS_BONES': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Lookup-based multiplication always terminates'),
    ],

    # ===== LOGIC SYSTEMS — confront incompleteness =====
    'PARACONSISTENT_LOGIC': [
        ('GODEL_INCOMPLETENESS', 'DISTRIBUTE', 'Tolerates contradiction without explosion; distributes inconsistency damage'),
        ('FOUNDATIONAL_IMPOSSIBILITY', 'DISTRIBUTE', 'Sacrifices explosion principle to maintain consistency with contradictions'),
    ],
    'LAMBDA_CALCULUS': [
        ('HALTING_PROBLEM', 'EXTEND', 'Turing-complete; confronts halting problem directly. Church-Turing thesis.'),
        ('GODEL_INCOMPLETENESS', 'EXTEND', 'Expressive enough to encode Godel sentences'),
    ],
    'FREGE_BEGRIFF': [
        ('IMPOSSIBILITY_NAIVE_SET_THEORY', 'EXTEND', 'Begriffsschrift extends logic; Russell paradox shows the extension is inconsistent'),
    ],
    'FREGE_BEGRIFFSSCHRIFT': [
        ('IMPOSSIBILITY_NAIVE_SET_THEORY', 'EXTEND', 'First formal system; vulnerable to Russell paradox — naive comprehension fails'),
        ('GODEL_INCOMPLETENESS', 'EXTEND', 'Sufficiently strong formal system falls under Godel'),
    ],
    'MATH_SYS_129': [  # Polish Notation
        ('HALTING_PROBLEM', 'TRUNCATE', 'Fixed notation; expression evaluation always terminates (no recursion)'),
    ],
    'MATH_SYS_130': [  # Peirce Existential Graphs
        ('GODEL_INCOMPLETENESS', 'EXTEND', 'Graphical logic system expressive enough to confront incompleteness'),
        ('FOUNDATIONAL_IMPOSSIBILITY', 'EXTEND', 'Diagrammatic reasoning extends formal systems to visual domain'),
    ],

    # ===== MODERN FORMAL SYSTEMS =====
    'HOTT': [
        ('FOUNDATIONAL_IMPOSSIBILITY', 'EXTEND', 'Homotopy type theory extends foundations with univalence axiom'),
        ('GODEL_INCOMPLETENESS', 'EXTEND', 'Computationally verifiable proofs; still subject to incompleteness'),
    ],
    'FUZZY_SET_THEORY': [
        ('IMPOSSIBILITY_NAIVE_SET_THEORY', 'EXTEND', 'Extends membership to [0,1]; avoids crisp set paradoxes by grading membership'),
    ],
    'P_ADICS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'EXTEND', 'p-adic completion provides alternative metric; some irrationals become p-adically rational'),
        ('HASSE_MINKOWSKI_FAILURE', 'EXTEND', 'Local-global principle uses p-adic completions; Hasse-Minkowski failure shows limits'),
    ],
    'P_ADIC_NUMBERS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'EXTEND', 'Alternative completion of Q; extends number system in non-Archimedean direction'),
        ('METRIC_REDEFINITION', 'COMPOSE', 'p-adic metric redefines distance; canonical spoke of METRIC_REDEFINITION hub'),
    ],
    'TROPICAL_ALGEBRA': [
        ('IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT', 'DISTRIBUTE', 'Min-plus algebra changes the algebraic operations; distributivity holds differently'),
    ],
    'TROPICAL_MATH': [
        ('IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT', 'DISTRIBUTE', 'Redefines addition as min/max; changes which algebraic laws hold'),
    ],
    'TROPICAL_MATHEMATICS': [
        ('IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT', 'DISTRIBUTE', 'Tropical semiring: addition=min, multiplication=addition. Algebraic structure change.'),
    ],
    'APL_NOTATION': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Array operations on finite arrays always terminate'),
    ],
    'MATH_SYS_217': [  # Kolmogorov Complexity
        ('HALTING_PROBLEM', 'EXTEND', 'K(x) is uncomputable — directly confronts halting problem'),
        ('GODEL_INCOMPLETENESS', 'EXTEND', 'Chaitin incompleteness: cannot prove K(x) > c for most x'),
        ('RICE_THEOREM', 'EXTEND', 'Non-trivial property of programs; undecidable by Rice'),
    ],
    'MATH_SYS_218': [  # Game Theory Payoff Matrices
        ('CONDORCET_PARADOX', 'PARTITION', 'Finite game matrices partition strategy space into discrete payoff cells'),
        ('COMMONS_DILEMMA', 'PARTITION', 'Prisoner dilemma payoff matrix encodes the commons tragedy'),
    ],
    'MATH_SYS_220': [  # Quantum Circuit Diagrams
        ('IMPOSSIBILITY_NO_CLONING_THEOREM', 'COMPOSE', 'Quantum circuits compose unitaries; no-cloning prevents FANOUT gate'),
        ('HEISENBERG_UNCERTAINTY', 'COMPOSE', 'Measurement gates in circuits confront uncertainty via composed operations'),
    ],

    # ===== COUNTING / BODY SYSTEMS — confront cognitive limits =====
    'MATH_SYS_125': [  # Papuan Body-Part Counting
        ('MILLERS_LAW', 'PARTITION', 'Body parts partition number line into ~27 chunks; maps to working memory'),
    ],
    'PAPUAN_BODY_COUNTING_SYSTEM': [
        ('MILLERS_LAW', 'PARTITION', 'Sequential body mapping partitions number range into memorable segments'),
    ],
    'MATH_SYS_124': [  # Piraha Counting
        ('MILLERS_LAW', 'TRUNCATE', 'System truncates at ~3; extreme truncation of number line'),
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Approximate number system cannot distinguish rationals from irrationals'),
    ],
    'MATH_SYS_123': [  # Munduruku
        ('MILLERS_LAW', 'TRUNCATE', 'Approximate number system with ~5 distinctions; truncated number representation'),
    ],
    'MATH_SYS_119': [  # Kpelle Classification
        ('MILLERS_LAW', 'PARTITION', 'Classification system partitions objects into manageable categories'),
    ],
    'MATH_SYS_117': [  # Akan Gold Weights
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Discrete weight standards truncate continuous mass to standard values'),
    ],

    # ===== NAVIGATION — confront projection impossibility =====
    'POLYNESIAN_NAVIGATION': [
        ('IMPOSSIBILITY_MAP_PROJECTION', 'RANDOMIZE', 'Star compass distributes navigation error stochastically across multiple readings'),
    ],
    'POLYNESIAN_WAVE_NAVIGATION_MODEL': [
        ('IMPOSSIBILITY_MAP_PROJECTION', 'DISTRIBUTE', 'Wave pattern reading distributes spatial information across multiple sensory channels'),
        ('GABOR_LIMIT', 'DISTRIBUTE', 'Reading wave interference distributes time-frequency analysis across spatial domain'),
    ],
    'MATH_SYS_214': [  # Wave Interference Navigation
        ('IMPOSSIBILITY_MAP_PROJECTION', 'DISTRIBUTE', 'Wave pattern inference distributes spatial computation'),
        ('GABOR_LIMIT', 'DISTRIBUTE', 'Interferometric navigation confronts time-frequency resolution limits'),
    ],
    'MATH_SYS_126': [  # Tongan Navigation
        ('IMPOSSIBILITY_MAP_PROJECTION', 'RANDOMIZE', 'Statistical wave pattern reading randomizes over observation noise'),
    ],
    'ISLAMIC_QIBLA_TRIGONOMETRY': [
        ('IMPOSSIBILITY_MAP_PROJECTION', 'TRUNCATE', 'Spherical trig for qibla direction truncates to great circle arc on curved surface'),
    ],

    # ===== NUMERAL SYSTEMS (basic) — confront representation limits =====
    'BRAHMI_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Decimal notation truncates irrational values'),
    ],
    'CHINESE_ROD_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Positional decimal system truncates infinite decimals'),
    ],
    'CHINESE_ROD_NEGATIVE_NUMBER_SYSTEM': [
        ('IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT', 'EXTEND', 'Red/black rods extend number system to include negatives; signed arithmetic'),
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'EXTEND', 'Negative numbers extend the representable number line'),
    ],
    'MATH_SYS_209': [  # Brahmagupta Zero
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'EXTEND', 'Zero and negatives extend the number system; confronts representation boundary'),
        ('FOUNDATIONAL_IMPOSSIBILITY', 'EXTEND', 'Zero arithmetic rules formalize a foundational extension'),
    ],
    'AZTEC_VIGESIMAL': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Base-20 positional system truncates at integer values'),
    ],
    'INCA_QUIPU': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Knot-based positional encoding truncates to integer values'),
        ('SHANNON_CAPACITY', 'COMPOSE', 'Hierarchical cord structure composes information across multiple channels'),
    ],
    'INCAN_QUIPU': [
        ('SHANNON_CAPACITY', 'COMPOSE', 'Multi-dimensional encoding (position, color, knot type) composes information channels'),
    ],
    'INCA_KHIPU_POSITIONAL_ENCODING': [
        ('SHANNON_CAPACITY', 'COMPOSE', 'Positional + color + knot-type encoding composes multiple information channels'),
    ],
    'INCAN_YUPANA': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Grid computation with discrete token placement'),
    ],
    'INCAN_YUPANA_CALCULATOR': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Discrete computational grid'),
    ],

    # ===== ABACUS / MECHANICAL — confront bounded computation =====
    'CHINESE_ABACUS_SUANPAN': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Finite bead manipulation always terminates'),
    ],
    'JAPANESE_SOROBAN': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Finite bead manipulation always terminates'),
    ],
    'JAPANESE_SOROBAN_OPTIMIZED_ALGORITHMS': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Optimized finite bead procedures always terminate'),
        ('IMPOSSIBILITY_FITTS_HICK_SPEED_ACCURACY', 'DISTRIBUTE', 'Optimized algorithms distribute speed-accuracy tradeoff across multiple bead movements'),
    ],
    'RUSSIAN_SCHOTY': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Linear abacus computation always terminates'),
    ],
    'SLIDE_RULE': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Analog logarithmic scale truncated by physical precision'),
        ('GABOR_LIMIT', 'TRUNCATE', 'Physical scale resolution imposes time-frequency-like tradeoff on precision'),
    ],

    # ===== MODULAR / CHINESE REMAINDER =====
    'CHINESE_REMAINDER_SYSTEM': [
        ('FERMAT_LAST_THEOREM', 'PARTITION', 'Modular decomposition partitions integer domain into coprime residue classes'),
    ],
    'MATH_SYS_208': [  # Chinese Remainder Algorithm
        ('FERMAT_LAST_THEOREM', 'PARTITION', 'Modular decomposition partitions problem across coprime moduli'),
    ],
    'CHINESE_MAGIC_SQUARE_GENERALIZATION': [
        ('FOUR_SQUARES_OBSTRUCTION', 'COMPOSE', 'Magic square constraints compose additive conditions across rows/columns/diagonals'),
    ],
    'MATH_SYS_207': [  # Magic Square Construction
        ('FOUR_SQUARES_OBSTRUCTION', 'COMPOSE', 'Constraint-based construction of magic squares'),
    ],
    'MATH_SYS_110': [  # Lo Shu
        ('FOUR_SQUARES_OBSTRUCTION', 'COMPOSE', 'Lo Shu 3x3 magic square: constraint satisfaction on integer grid'),
    ],

    # ===== NUMBER THEORY =====
    'MATH_SYS_106': [  # Thabit ibn Qurra
        ('FERMAT_LAST_THEOREM', 'EXTEND', 'Amicable numbers extend number-theoretic relationships; Thabit formula generates pairs'),
    ],
    'MATH_SYS_103': [  # Gematria
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Letter-number mapping is finite discrete encoding'),
    ],
    'MATH_SYS_109': [  # Ibn Munim Combinatorics
        ('CONDORCET_PARADOX', 'PARTITION', 'Combinatorial enumeration partitions possibility space into counted subsets'),
    ],
    'MATH_SYS_115': [  # Jain Combinatorics
        ('CONDORCET_PARADOX', 'PARTITION', 'Large number enumeration partitions combinatorial space'),
    ],

    # ===== GRAPH / DIAGRAM SYSTEMS =====
    'CATEGORY_STRING_DIAGRAMS': [
        ('GODEL_INCOMPLETENESS', 'EXTEND', 'String diagrams extend reasoning about composition; still subject to incompleteness'),
    ],
    'PENROSE_DIAGRAMS': [
        ('PENROSE_SINGULARITY', 'COMPOSE', 'Penrose diagrams compose causal structure; singularity visible as diagram boundary'),
    ],
    'PENROSE_TENSOR_DIAGRAMS': [
        ('IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY', 'COMPOSE', 'Tensor networks compose high-dimensional operations via graphical contractions'),
    ],
    'MATH_SYS_219': [  # Tensor Diagram Notation
        ('IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY', 'COMPOSE', 'Tensor contraction diagrams compress exponential index complexity'),
    ],
    'MATH_SYS_131': [  # Feynman Diagrams
        ('IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY', 'COMPOSE', 'Path integrals summed via finite diagram expansion — compositional approach to infinite-dimensional integral'),
    ],
    'MATH_SYS_132': [  # Knuth Up-Arrow
        ('CANTOR_DIAGONALIZATION', 'EXTEND', 'Hyper-operations extend arithmetic toward transfinite; each arrow level = new infinity type'),
    ],
    'MATH_SYS_133': [  # Conway Chain Arrow
        ('CANTOR_DIAGONALIZATION', 'EXTEND', 'Chain arrows extend past up-arrows; approaches ordinal arithmetic'),
    ],

    # ===== UNDECIPHERED — mapping is speculative but structural =====
    'ISHANGO_BONE': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Notch counting is inherently discrete/integer; truncates continuous quantity'),
    ],
    'MATH_SYS_137': [  # Indus Script
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Hypothesized numerical encoding; discrete symbols truncate continuous values'),
    ],
    'MATH_SYS_138': [  # Proto-Elamite
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Accounting tablets encode discrete quantities'),
    ],
    'MATH_SYS_139': [  # Rongorongo
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Undeciphered; if numerical, necessarily discrete truncation'),
    ],
    'MATH_SYS_140': [  # Linear A
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Partial number system known; discrete notation truncates continuous'),
    ],

    # ===== PROSODY / COMBINATORICS =====
    'INDIAN_PROSODY_BINARY_METRICS': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Finite binary enumeration of meters always terminates'),
        ('BINARY_DECOMP_RECOMP', 'COMPOSE', 'Pingala binary decomposition = canonical spoke of binary hub'),
    ],

    # ===== MISC =====
    'MATH_SYS_101': [  # Ge'ez Numerals
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Non-positional integer notation'),
    ],
    'MATH_SYS_102': [  # Armenian Numerals
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Alphabetic integer notation'),
    ],
    'MATH_SYS_104': [  # Al-Uqlidisi Decimal Fractions
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Early decimal fractions truncate infinite expansions'),
    ],
    'MATH_SYS_107': [  # Al-Samawal
        ('IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'TRUNCATE', 'Symbolic polynomial manipulation; algebraic notation cannot solve quintics'),
    ],
    'MATH_SYS_108': [  # Al-Tusi Trigonometry
        ('IMPOSSIBILITY_SQUARING_CIRCLE', 'TRUNCATE', 'Trigonometric tables truncate transcendental values'),
    ],
    'MATH_SYS_111': [  # Counting Board Matrix
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Matrix methods on integers; truncated to rational solutions'),
    ],
    'MATH_SYS_113': [  # Vietnamese Nom
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Hybrid numeral system; discrete notation'),
    ],
    'MATH_SYS_118': [  # Ethiopian Multiplication
        ('BINARY_DECOMP_RECOMP', 'COMPOSE', 'Doubling/halving = binary decomposition canonical spoke'),
    ],
    'LEIBNIZ_CHARACTERISTICA': [
        ('GODEL_INCOMPLETENESS', 'EXTEND', 'Universal formal language ambition confronts incompleteness directly'),
        ('FOUNDATIONAL_IMPOSSIBILITY', 'EXTEND', 'Leibniz dream of universal calculus of reasoning; Godel shows it cannot be complete'),
    ],
    'POLISH_NOTATION': [
        ('HALTING_PROBLEM', 'TRUNCATE', 'Fixed expression evaluation; always terminates'),
    ],
    'MATH_SYS_118': [  # Ethiopian Multiplication (duplicate key, will overwrite)
        ('BINARY_DECOMP_RECOMP', 'COMPOSE', 'Canonical binary decomposition spoke'),
    ],
    'EGYPTIAN_HIEROGLYPHIC': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Additive integer-only notation'),
    ],
    'EGYPTIAN_HIEROGLYPHIC_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Base-10 additive integer notation'),
    ],
    'EGYPTIAN_HIERATIC': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Ciphered integer notation'),
    ],
    'EGYPTIAN_HIERATIC_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Cursive integer notation'),
    ],
    'EGYPTIAN_WEIGHT_BALANCE_CALCULUS': [
        ('ALGEBRAIC_COMPLETION', 'COMPOSE', 'Balance-scale reasoning composes equilibrium — al-jabr pattern predating al-jabr'),
    ],
    'SUMERIAN_TOKENS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Clay tokens: discrete physical units for counting'),
    ],
    'SUMERIAN_TOKEN_ACCOUNTING': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Token accounting is inherently discrete'),
    ],
    'GREEK_ATTIC_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Additive integer notation'),
    ],
    'GREEK_IONIC_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Alphabetic integer notation'),
    ],
    'DEVANAGARI_NUMERALS': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Decimal integer notation'),
    ],
    'BABYLONIAN_RECIPROCAL_TABLE_SYSTEM': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Reciprocal tables for regular numbers only; irrationals excluded'),
    ],
    'INCAN_QUIPU': [
        ('IMPOSSIBILITY_RATIONAL_SQRT2', 'TRUNCATE', 'Knotted string encoding truncates to integers'),
    ],
}

# Step 3: Insert cross_domain_edges
inserted = 0
skipped = 0
mapped_systems = set()
unmapped_systems = []

all_hub_ids = set(r[0] for r in db.execute('SELECT comp_id FROM abstract_compositions').fetchall())

for row in ethno_rows:
    sys_id = row[0]
    if sys_id in EXPLICIT_MAPPINGS:
        mapped_systems.add(sys_id)
        for hub_id, damage_op, reason in EXPLICIT_MAPPINGS[sys_id]:
            if hub_id not in all_hub_ids:
                print(f'  WARNING: hub {hub_id} not found in DB, skipping for {sys_id}')
                skipped += 1
                continue

            source_id = f'ETHNO_{sys_id}'
            target_id = f'{hub_id}'

            try:
                db.execute('''
                    INSERT INTO cross_domain_edges
                    (edge_id, source_resolution_id, target_resolution_id, shared_damage_operator, edge_type, provenance)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', [next_eid, source_id, target_id, damage_op, 'tradition_hub_mapping',
                      f'aletheia_tradition: {reason[:200]}'])
                next_eid += 1
                inserted += 1
            except Exception as e:
                print(f'  ERROR inserting edge for {sys_id} -> {hub_id}: {e}')
                skipped += 1
    else:
        unmapped_systems.append(sys_id)

db.commit()

# Report
total_edges = db.execute('SELECT COUNT(*) FROM cross_domain_edges').fetchone()[0]
tradition_edges = db.execute("SELECT COUNT(*) FROM cross_domain_edges WHERE edge_type = 'tradition_hub_mapping'").fetchone()[0]

print()
print("=" * 70)
print("TRADITION-HUB MAPPING RESULTS")
print(f"  Total ethnomathematics systems:    {len(ethno_rows)}")
print(f"  Systems mapped:                    {len(mapped_systems)}")
print(f"  Systems unmapped:                  {len(unmapped_systems)}")
print(f"  Edges inserted:                    {inserted}")
print(f"  Edges skipped/errored:             {skipped}")
print(f"  Total tradition edges in DB:       {tradition_edges}")
print(f"  Total edges in DB:                 {total_edges}")
print("=" * 70)

if unmapped_systems:
    print(f"\nUnmapped systems ({len(unmapped_systems)}):")
    for s in sorted(unmapped_systems):
        print(f"  {s}")

# Damage operator distribution for tradition edges
print("\nDamage operator distribution (tradition edges):")
rows = db.execute("""
    SELECT shared_damage_operator, COUNT(*)
    FROM cross_domain_edges
    WHERE edge_type = 'tradition_hub_mapping'
    GROUP BY shared_damage_operator
    ORDER BY 2 DESC
""").fetchall()
for r in rows:
    print(f"  {r[0]:20s} {r[1]:4d}")

# Hub coverage
print("\nTop hubs by tradition connections:")
rows = db.execute("""
    SELECT target_resolution_id, COUNT(*)
    FROM cross_domain_edges
    WHERE edge_type = 'tradition_hub_mapping'
    GROUP BY target_resolution_id
    ORDER BY 2 DESC
    LIMIT 15
""").fetchall()
for r in rows:
    print(f"  {r[0]:55s} {r[1]:4d}")

# Save results
results = {
    'total_systems': len(ethno_rows),
    'mapped': len(mapped_systems),
    'unmapped': len(unmapped_systems),
    'edges_inserted': inserted,
    'unmapped_systems': sorted(unmapped_systems),
}
with open('noesis/v2/tradition_hub_mapping_results.json', 'w') as f:
    json.dump(results, f, indent=2)

db.close()
print("\nResults saved to noesis/v2/tradition_hub_mapping_results.json")
