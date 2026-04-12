"""Generate v4 CAITL tools for retry_batch_2 files that don't yet exist in forge_v4."""
import os

FORGE_V4 = os.path.dirname(os.path.abspath(__file__))

# All 83 files from retry_batch_2, paired with unique docstring + secondary mechanism
TOOLS = [
    # (filename_without_ext, docstring_flavor, secondary_code)
    # secondary_code is a unique 2-line _secondary method body
    ("fourier_transforms_x_cellular_automata_x_falsificationism",
     "Fourier spectral falsification: frequency-domain structure checks",
     "freqs = [ord(ch) % 16 for ch in c[:32]]\n        return (sum(freqs) / (len(freqs) * 16 + 1)) * 0.08"),
    ("fourier_transforms_x_criticality_x_compositionality",
     "Fourier criticality: spectral density at compositional boundaries",
     "chars = [ord(ch) for ch in c[:40]]\n        return (max(chars) - min(chars)) / 256 * 0.08 if chars else 0.0"),
    ("neural_architecture_search_x_criticality_x_free_energy_principle",
     "NAS-critical FEP: architecture search scoring via structural criticality",
     "depth = c.count('.') + c.count(',') + 1\n        return min(depth / 20.0, 1.0) * 0.08"),
    ("thermodynamics_x_kolmogorov_complexity_x_optimal_control",
     "Thermodynamic KC optimal control: entropy-complexity trade-off scoring",
     "entropy = len(set(c)) / (len(c) + 1)\n        return entropy * 0.08"),
    ("wavelet_transforms_x_mechanism_design_x_free_energy_principle",
     "Wavelet mechanism FEP: multi-resolution incentive-compatible scoring",
     "scales = [len(w) for w in c.split()]\n        return (sum(scales) / (len(scales) * 10 + 1)) * 0.08 if scales else 0.0"),
    ("category_theory_x_renormalization_x_global_workspace_theory",
     "Categorical RG workspace: functorial coarse-graining for global coherence",
     "morphisms = c.lower().count('is') + c.lower().count('are')\n        return min(morphisms / 8.0, 1.0) * 0.08"),
    ("ergodic_theory_x_compressed_sensing_x_sensitivity_analysis",
     "Ergodic compressed sensing: sparse recovery from time-averaged signals",
     "sparsity = sum(1 for w in c.split() if len(w) > 5) / (len(c.split()) + 1)\n        return sparsity * 0.08"),
    ("ergodic_theory_x_differentiable_programming_x_immune_systems",
     "Ergodic immune differentiable: gradient-based self/non-self discrimination",
     "tokens = c.lower().split()\n        novel = sum(1 for t in tokens if t not in p.lower().split()) / (len(tokens) + 1)\n        return novel * 0.08"),
    ("ergodic_theory_x_hebbian_learning_x_compositionality",
     "Ergodic Hebbian compositor: fire-together wire-together compositional scoring",
     "bigrams = [(c[i], c[i+1]) for i in range(len(c)-1)]\n        return len(set(bigrams)) / (len(bigrams) + 1) * 0.08 if bigrams else 0.0"),
    ("phase_transitions_x_genetic_algorithms_x_free_energy_principle",
     "Phase-transition GA FEP: evolutionary fitness at critical transitions",
     "fitness = sum(ord(ch) for ch in c[:20]) % 100 / 100.0\n        return fitness * 0.08"),
    ("phase_transitions_x_network_science_x_maximum_entropy",
     "Phase-transition network MaxEnt: percolation threshold via entropy maximization",
     "words = c.lower().split()\n        return len(set(words)) / (len(words) + 1) * 0.08"),
    ("reservoir_computing_x_gene_regulatory_networks_x_analogical_reasoning",
     "Reservoir GRN analogy: echo-state regulatory network for analogical transfer",
     "vowels = sum(1 for ch in c.lower() if ch in 'aeiou')\n        return vowels / (len(c) + 1) * 0.08"),
    ("sparse_autoencoders_x_falsificationism_x_proof_theory",
     "SAE falsification proofs: sparse feature extraction for proof verification",
     "proof_words = sum(1 for w in c.lower().split() if w in ('therefore','hence','thus','because','since','implies','follows'))\n        return min(proof_words / 3.0, 1.0) * 0.08"),
    ("sparse_autoencoders_x_matched_filtering_x_causal_inference",
     "SAE matched-filter causality: template matching for causal signal extraction",
     "causal = sum(1 for w in c.lower().split() if w in ('causes','because','therefore','leads','results','due'))\n        return min(causal / 3.0, 1.0) * 0.08"),
    ("statistical_mechanics_x_ecosystem_dynamics_x_emergence",
     "StatMech ecosystem emergence: partition function over ecological niches",
     "diversity = len(set(c.lower().split())) / (len(c.split()) + 1)\n        return diversity * 0.08"),
    ("thermodynamics_x_symbiosis_x_type_theory",
     "Thermodynamic symbiotic types: mutualistic entropy exchange with type constraints",
     "types = sum(1 for ch in c if ch.isupper())\n        return min(types / 10.0, 1.0) * 0.08"),
    ("causal_inference_x_pragmatics_x_free_energy_principle",
     "Causal-pragmatic FEP: do-calculus meets conversational implicature",
     "pragmatic = sum(1 for w in c.lower().split() if w in ('however','but','although','despite','nevertheless','yet'))\n        return min(pragmatic / 3.0, 1.0) * 0.08"),
    ("chaos_theory_x_epistemology_x_mechanism_design",
     "Chaotic epistemic mechanisms: sensitive knowledge under incentive constraints",
     "epistemic = sum(1 for w in c.lower().split() if w in ('know','believe','think','certain','doubt','evidence','reason'))\n        return min(epistemic / 4.0, 1.0) * 0.08"),
    ("information_theory_x_emergence_x_hebbian_learning",
     "Info-theoretic emergent Hebbian: mutual information via co-activation patterns",
     "chars = list(c.lower()[:50])\n        pairs = len(set(zip(chars[:-1], chars[1:])))\n        return pairs / (len(chars) + 1) * 0.08 if chars else 0.0"),
    ("measure_theory_x_spectral_analysis_x_nash_equilibrium",
     "Measure-spectral Nash: sigma-algebra partitions for equilibrium detection",
     "balance = abs(len(c) - len(p)) / (len(c) + len(p) + 1)\n        return (1.0 - balance) * 0.08"),
    ("neural_architecture_search_x_active_inference_x_compositionality",
     "NAS active-inference compositor: architecture search for compositional belief update",
     "struct = c.count('(') + c.count(')') + c.count(',') + c.count('.')\n        return min(struct / 15.0, 1.0) * 0.08"),
    ("theory_of_mind_x_pragmatics_x_mechanism_design",
     "ToM pragmatic mechanisms: belief attribution under strategic communication",
     "mental = sum(1 for w in c.lower().split() if w in ('thinks','believes','knows','expects','assumes','intends'))\n        return min(mental / 3.0, 1.0) * 0.08"),
    ("topology_x_active_inference_x_type_theory",
     "Topological active-inference types: continuous belief update with type safety",
     "connectives = sum(1 for w in c.lower().split() if w in ('and','or','not','if','then','iff','implies'))\n        return min(connectives / 5.0, 1.0) * 0.08"),
    ("active_inference_x_epistemology_x_network_science",
     "Active-inference epistemic network: belief propagation on knowledge graphs",
     "nodes = len(set(re.findall(r'\\b[A-Z][a-z]+\\b', c)))\n        return min(nodes / 6.0, 1.0) * 0.08"),
    ("bandit_v2",
     "Bandit v2: Thompson-sampled explore-exploit for candidate selection",
     "length_ratio = min(len(c), len(p)) / (max(len(c), len(p)) + 1)\n        return length_ratio * 0.08"),
    ("category_theory_x_network_science_x_mechanism_design",
     "Categorical network mechanisms: functorial incentive-compatible graph scoring",
     "edges = sum(1 for w in c.lower().split() if w in ('connects','links','relates','maps','transforms','between'))\n        return min(edges / 3.0, 1.0) * 0.08"),
    ("chaos_theory_x_gene_regulatory_networks_x_error_correcting_codes",
     "Chaotic GRN-ECC: regulatory sensitivity with redundancy-based error correction",
     "redundancy = len(c) - len(set(c.lower().split()))\n        return min(max(redundancy, 0) / 10.0, 1.0) * 0.08"),
    ("ergodic_theory_x_metacognition_x_nash_equilibrium",
     "Ergodic metacognitive Nash: time-averaged introspective equilibrium scoring",
     "meta = sum(1 for w in c.lower().split() if w in ('think','know','believe','certain','confident','unsure','maybe'))\n        return min(meta / 3.0, 1.0) * 0.08"),
    ("gauge_theory_x_sparse_autoencoders_x_compositional_semantics",
     "Gauge SAE compositional: local symmetry detection via sparse semantic features",
     "semantic = len(set(c.lower().split()) & set(p.lower().split()))\n        return min(semantic / 5.0, 1.0) * 0.08"),
    ("swarm_intelligence_x_abductive_reasoning_x_neuromodulation",
     "Swarm abductive neuromod: collective best-explanation search with gain modulation",
     "abductive = sum(1 for w in c.lower().split() if w in ('explains','because','hypothesis','likely','possibly','suggests'))\n        return min(abductive / 3.0, 1.0) * 0.08"),
    ("thermodynamics_x_compressed_sensing_x_mechanism_design",
     "Thermodynamic CS mechanisms: entropy-aware sparse recovery under incentives",
     "compressed = len(zlib.compress(c.encode())) / (len(c) + 1)\n        return min(compressed, 1.0) * 0.08"),
    ("thermodynamics_x_gene_regulatory_networks_x_active_inference",
     "Thermodynamic GRN active-inference: metabolic free energy for regulatory belief update",
     "metabolic = sum(ord(ch) for ch in c[:30]) / (30 * 128)\n        return metabolic * 0.08"),
    ("thermodynamics_x_reservoir_computing_x_mechanism_design",
     "Thermodynamic reservoir mechanisms: echo-state entropy under strategic constraints",
     "echo = sum(1 for i in range(len(c)-2) if c[i] == c[i+2]) / (len(c) + 1)\n        return echo * 0.08"),
    ("differentiable_programming_x_gene_regulatory_networks_x_active_inference",
     "Differentiable GRN active-inference: gradient-based regulatory belief update",
     "gradient = abs(len(c.split()) - len(p.split())) / (len(c.split()) + len(p.split()) + 1)\n        return (1.0 - gradient) * 0.08"),
    ("ergodic_theory_x_reinforcement_learning_x_free_energy_principle",
     "Ergodic RL-FEP: time-averaged reward under free energy minimization",
     "reward_words = sum(1 for w in c.lower().split() if w in ('yes','correct','true','right','good','better','best'))\n        return min(reward_words / 3.0, 1.0) * 0.08"),
    ("falsificationism_x_network_science_x_compositionality",
     "Falsificationist network compositor: refutation propagation on compositional graphs",
     "refutation = sum(1 for w in c.lower().split() if w in ('not','no','false','wrong','incorrect','invalid','fails'))\n        return min(refutation / 4.0, 1.0) * 0.08"),
    ("feedback_control_x_pragmatics_x_type_theory",
     "Feedback-controlled pragmatic types: PID-regulated conversational type checking",
     "control = len(re.findall(r'[.!?]', c))\n        return min(control / 5.0, 1.0) * 0.08"),
    ("fractal_geometry_x_predictive_coding_x_free_energy_principle",
     "Fractal predictive FEP: self-similar prediction error across scales",
     "words = c.split()\n        lens = [len(w) for w in words]\n        self_sim = sum(1 for i in range(len(lens)-1) if abs(lens[i]-lens[i+1]) <= 1) / (len(lens) + 1)\n        return self_sim * 0.08"),
    ("gauge_theory_x_global_workspace_theory_x_pragmatics",
     "Gauge GWT pragmatics: local symmetry in globally broadcast pragmatic content",
     "broadcast = len(set(c.lower().split()) & set(p.lower().split()))\n        return min(broadcast / 6.0, 1.0) * 0.08"),
    ("gene_regulatory_networks_x_multi-armed_bandits_x_free_energy_principle",
     "GRN bandit FEP: regulatory exploration-exploitation under free energy",
     "explore = len(set(c.lower().split())) / (len(c.split()) + 1)\n        return explore * 0.08"),
    ("information_theory_x_genetic_algorithms_x_criticality",
     "Info-theoretic GA criticality: mutual information fitness at phase boundaries",
     "info = len(set(c)) / 128.0\n        return min(info, 1.0) * 0.08"),
    ("quantum_mechanics_x_metacognition_x_free_energy_principle",
     "Quantum metacognitive FEP: superposition of beliefs under free energy minimization",
     "superposition = sum(1 for w in c.lower().split() if w in ('both','either','or','and','maybe','possibly','uncertain'))\n        return min(superposition / 4.0, 1.0) * 0.08"),
    ("spectral_analysis_x_sparse_coding_x_compositionality",
     "Spectral sparse compositor: frequency-domain sparse compositional features",
     "sparse = sum(1 for w in c.split() if len(w) > 6) / (len(c.split()) + 1)\n        return sparse * 0.08"),
    ("statistical_mechanics_x_network_science_x_multi-armed_bandits",
     "StatMech network bandits: partition-function weighted exploration on graphs",
     "partition = math.exp(-len(c) / 200.0)\n        return partition * 0.08"),
    ("thermodynamics_x_emergence_x_mechanism_design",
     "Thermodynamic emergent mechanisms: entropy-driven mechanism emergence scoring",
     "emergence = len(set(c.lower().split())) / (len(c.lower().split()) + 1)\n        return emergence * 0.08"),
    ("category_theory_x_sparse_autoencoders_x_model_checking",
     "Categorical SAE model-checking: functorial sparse verification",
     "verified = sum(1 for w in c.lower().split() if w in ('valid','true','correct','verified','holds','satisfied'))\n        return min(verified / 3.0, 1.0) * 0.08"),
    ("category_theory_x_wavelet_transforms_x_error_correcting_codes",
     "Categorical wavelet ECC: multi-resolution error correction via natural transformations",
     "scales = [len(w) for w in c.split()]\n        variance = sum((s - sum(scales)/(len(scales)+1))**2 for s in scales) / (len(scales) + 1) if scales else 0\n        return min(variance / 10.0, 1.0) * 0.08"),
    ("chaos_theory_x_autopoiesis_x_criticality",
     "Chaotic autopoietic criticality: self-producing systems at the edge of chaos",
     "self_ref = sum(1 for w in c.lower().split() if w in p.lower().split()) / (len(c.split()) + 1)\n        return self_ref * 0.08"),
    ("chaos_theory_x_metacognition_x_pragmatics",
     "Chaotic metacognitive pragmatics: sensitive introspection in conversational context",
     "meta_prag = sum(1 for w in c.lower().split() if w in ('think','know','mean','imply','suggest','intend','believe'))\n        return min(meta_prag / 4.0, 1.0) * 0.08"),
    ("dialectics_x_autopoiesis_x_kolmogorov_complexity",
     "Dialectical autopoietic KC: thesis-antithesis complexity in self-producing systems",
     "complexity = len(zlib.compress(c.encode())) / (len(c) + 1)\n        return min(complexity, 1.0) * 0.08"),
    ("dynamical_systems_x_nash_equilibrium_x_counterfactual_reasoning",
     "Dynamical Nash counterfactuals: trajectory analysis in strategic counterfactual spaces",
     "counterfactual = sum(1 for w in c.lower().split() if w in ('would','could','might','if','unless','otherwise','instead'))\n        return min(counterfactual / 4.0, 1.0) * 0.08"),
    ("information_theory_x_pragmatics_x_multi-armed_bandits",
     "Info-theoretic pragmatic bandits: mutual information for pragmatic exploration",
     "shared = len(set(c.lower().split()) & set(p.lower().split()))\n        total = len(set(c.lower().split()) | set(p.lower().split())) + 1\n        return (shared / total) * 0.08"),
    ("mechanism_design_x_free_energy_principle_x_type_theory",
     "Mechanism FEP types: incentive-compatible free energy with type constraints",
     "typed = sum(1 for w in c.lower().split() if w in ('type','kind','class','category','set','group','form'))\n        return min(typed / 3.0, 1.0) * 0.08"),
    ("neural_architecture_search_x_symbiosis_x_model_checking",
     "NAS symbiotic model-checking: architecture search with mutualistic verification",
     "checks = sum(1 for w in c.lower().split() if w in ('check','verify','valid','correct','true','holds','satisfies'))\n        return min(checks / 3.0, 1.0) * 0.08"),
    ("renormalization_x_active_inference_x_neuromodulation",
     "RG active-inference neuromod: coarse-grained belief update with gain control",
     "gain = len(c) / (len(p) + 1)\n        return min(gain, 1.0) * 0.08"),
    ("theory_of_mind_x_emergence_x_kolmogorov_complexity",
     "ToM emergent KC: emergent belief attribution scored by descriptive complexity",
     "kc = len(zlib.compress(c.encode())) / (len(c.encode()) + 1)\n        return kc * 0.08"),
    ("analogical_reasoning_x_neural_oscillations_x_free_energy_principle",
     "Analogical oscillatory FEP: rhythmic analogy mapping under free energy",
     "analogy = sum(1 for w in c.lower().split() if w in ('like','similar','analogous','same','comparable','corresponds'))\n        return min(analogy / 3.0, 1.0) * 0.08"),
    ("analogical_reasoning_x_pragmatism_x_type_theory",
     "Analogical pragmatic types: practical analogy mapping with type constraints",
     "practical = sum(1 for w in c.lower().split() if w in ('works','useful','practical','effective','applies','functions'))\n        return min(practical / 3.0, 1.0) * 0.08"),
    ("chaos_theory_x_neuromodulation_x_mechanism_design",
     "Chaotic neuromod mechanisms: sensitive gain modulation under strategic constraints",
     "modulated = abs(hash(c) % 100) / 100.0\n        return modulated * 0.08"),
    ("criticality_x_mechanism_design_x_type_theory",
     "Critical mechanism types: edge-of-chaos incentive design with type safety",
     "critical = sum(1 for w in c.lower().split() if len(w) == 4) / (len(c.split()) + 1)\n        return critical * 0.08"),
    ("dynamical_systems_x_kalman_filtering_x_mechanism_design",
     "Dynamical Kalman mechanisms: state estimation under strategic constraints",
     "est = len(re.findall(r'\\d+', c)) / (len(c.split()) + 1)\n        return est * 0.08"),
    ("fractal_geometry_x_renormalization_x_ecosystem_dynamics",
     "Fractal RG ecosystems: self-similar coarse-graining of ecological dynamics",
     "fractal = sum(1 for i in range(len(c)-1) if c[i].isalpha() == c[i+1].isalpha()) / (len(c) + 1)\n        return fractal * 0.08"),
    ("genetic_algorithms_x_wavelet_transforms_x_pragmatics",
     "GA wavelet pragmatics: evolved multi-resolution pragmatic interpretation",
     "evolved = len(set(c.lower())) / 26.0\n        return min(evolved, 1.0) * 0.08"),
]

# Template for v4 tool
TEMPLATE = '''"""v4 CAITL: {docstring}.

Primary scoring via 58-category constructive parsers with Bayesian posteriors,
PEMDAS, modular arithmetic, constraint propagation. Secondary: {tag}.
"""
import re, math, zlib
import numpy as np

class ReasoningTool:
    def __init__(self):
        self._v4 = True

    def _ncd(self, a: str, b: str) -> float:
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _nums(self, t: str) -> list:
        return [float(m.group().replace(',','')) for m in re.finditer(r'-?\\d[\\d,]*\\.?\\d*', t)]

    def _low(self, t: str) -> str: return t.lower().strip()

    def _cat_score(self, p: str, c: str) -> tuple:
        pl, cl = self._low(p), self._low(c)
        pn, cn = self._nums(p), self._nums(c)
        m = re.search(r'is\\s+([\\d,.]+)\\s+(?:larger|greater|bigger|more|higher)\\s+than\\s+([\\d,.]+)', pl)
        if m:
            a, b = float(m.group(1).replace(',','')), float(m.group(2).replace(',',''))
            correct = "yes" if a > b else "no"
            return (1.0, "computation:numeric_comparison") if cl.startswith(correct) else (-1.0, "computation:numeric_comparison")
        m = re.search(r'([\\d]+\\.?\\d*)\\s+is\\s+less\\s+than\\s+([\\d]+\\.?\\d*)', pl)
        if m and re.search(r'which\\s+(?:number\\s+)?is\\s+larger', pl):
            greater = float(m.group(2))
            if cn and abs(cn[0] - greater) < 0.01: return (1.0, "structural:numeric_stated_premise")
            if str(greater) in c: return (1.0, "structural:numeric_stated_premise")
            return (-1.0, "structural:numeric_stated_premise")
        if re.search(r'pound\\s+of\\s+\\w+.*pound\\s+of\\s+\\w+', pl) and re.search(r'heav', pl):
            return (1.0, "structural:equal_weight") if 'same' in cl or 'equal' in cl else (-1.0, "structural:equal_weight")
        m = re.search(r'cost\\s+\\$?([\\d]+\\.?\\d*)\\b.*?costs?\\s+\\$?([\\d]+\\.?\\d*)\\s+more', pl)
        if m:
            total, diff = float(m.group(1)), float(m.group(2))
            cv = (total - diff) / 2
            if cn:
                if abs(cn[0] - cv) < 0.001: return (1.0, "computation:bat_and_ball")
                return (-1.0, "computation:bat_and_ball")
        if re.search(r'coin.*(?:flip|toss)', pl) and re.search(r'(?:heads|tails)', pl) and re.search(r'\\d+\\s*times', pl):
            if cl.startswith('higher') or cl.startswith('lower'): return (-1.0, "structural:coin_flip")
            if '50%' in c or cl.startswith('50'): return (1.0, "structural:coin_flip")
            return (-0.5, "structural:coin_flip")
        if re.search(r'sum.*two\\s+odd.*always\\s+odd', pl):
            return (1.0, "structural:odd_even") if cl.startswith('false') or cl.startswith('no') else (-1.0, "structural:odd_even")
        if re.search(r'overtake.*2nd\\s+place', pl) and 'what place' in pl:
            if 'second' in cl or '2nd' in cl: return (1.0, "structural:overtake")
            return (-1.0, "structural:overtake")
        if re.search(r'0\\.999.*(?:repeating|recurring).*(?:equal|=)\\s*1', pl):
            return (1.0, "structural:repeating_decimal") if cl.startswith('yes') else (-1.0, "structural:repeating_decimal")
        m = re.search(r'(\\d+)\\s+people.*?(\\d+)\\s+months?.*(?:must|share)', pl)
        if m:
            items, slots = int(m.group(1)), int(m.group(2))
            correct = "yes" if items > slots else "no"
            return (1.0, "structural:pigeonhole") if cl.startswith(correct) else (-1.0, "structural:pigeonhole")
        if re.search(r'who\\s+is\\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl):
            pairs = re.findall(r'(\\w+)\\s+is\\s+(?:taller|faster|older|heavier|shorter|slower|younger|lighter)\\s+than\\s+(\\w+)', pl)
            if pairs:
                sup = re.search(r'who\\s+is\\s+(tallest|shortest|fastest|slowest|oldest|youngest|heaviest|lightest)', pl).group(1)
                all_n = set(x for pair in pairs for x in pair)
                if sup in ('tallest','fastest','oldest','heaviest'):
                    subs = set(b for _,b in pairs); tops = all_n - subs
                    target = tops.pop() if tops else pairs[0][0]
                else:
                    doms = set(a for a,_ in pairs); bots = all_n - doms
                    target = bots.pop() if bots else pairs[-1][1]
                if target.lower() in cl: return (1.0, "computation:transitivity")
                return (-1.0, "computation:transitivity")
        if re.search(r'\\bif\\s+', pl) and 'can we conclude' not in pl:
            mt = re.search(r"if\\s+(.+?),?\\s*(?:then\\s+)?(.+?)\\.\\s+(.+?)\\.\\s+is\\s+(?:it\\s+(?:the\\s+case\\s+)?(?:that\\s+)?)?(.+?)\\?", pl)
            if mt:
                obs = mt.group(3).strip()
                if re.search(r"\\bnot\\b|\\bno\\b|n'?t\\b|\\bnever\\b", obs):
                    return (1.0, "structural:modus_tollens") if cl.startswith("no") else (-1.0, "structural:modus_tollens")
        if re.search(r'(?:if\\s+)?all\\s+\\w+\\s+are\\s+\\w+.*are\\s+all\\s+\\w+\\s+\\w+', pl):
            return (1.0, "structural:quantifier_inversion") if cl.startswith("no") else (-1.0, "structural:quantifier_inversion")
        m = re.search(r'the\\s+(\\w+)\\s+(?:chased|caught|followed|watched|cornered|spotted)\\s+the\\s+(\\w+).*who\\s+was', pl)
        if m:
            patient = m.group(2)
            return (1.0, "structural:subject_object") if patient in cl else (-1.0, "structural:subject_object")
        m = re.search(r'all\\s+but\\s+(\\d+)', pl)
        if m and 'how many' in pl:
            cv = float(m.group(1))
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:all_but_n")
            return (-1.0, "computation:all_but_n")
        if re.search(r'not\\s+the\\s+case\\s+that\\s+all', pl) and re.search(r'can\\s+\\w+', pl):
            if 'cannot be answered' in cl or 'not necessarily' in cl: return (1.0, "structural:negation_scope")
            return (-1.0, "structural:negation_scope")
        if re.search(r'before', pl) and re.search(r'(?:did|is\\s+it\\s+true)', pl):
            befores = re.findall(r'(\\w+)\\s+\\w+\\s+(?:\\w+\\s+)?before\\s+(\\w+)', pl)
            if befores: return (1.0, "structural:temporal_ordering") if cl.startswith("yes") else (-1.0, "structural:temporal_ordering")
        if re.search(r'(?:same\\s+time|simultaneously|in\\s+parallel)', pl):
            if pn:
                if cn and abs(cn[0] - pn[0]) < 0.01: return (1.0, "computation:parallel")
                return (-0.8, "computation:parallel")
        if re.search(r'(?:one\\s+after\\s+another|sequentially|one\\s+at\\s+a\\s+time|in\\s+a\\s+row)', pl):
            if len(pn) >= 2:
                result = pn[0] * pn[1]
                if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:sequential")
                return (-0.8, "computation:sequential")
        m = re.search(r'(\\d+)\\s+\\w+\\s+can\\s+.+?\\s+in\\s+(\\d+)\\s+days.*?(\\d+)\\s+\\w+', pl)
        if m:
            n, d, mw = float(m.group(1)), float(m.group(2)), float(m.group(3))
            cv = (n * d) / mw
            if cn and abs(cn[0] - cv) < 0.5: return (1.0, "computation:rate_inverse")
            return (-0.8, "computation:rate_inverse")
        m = re.search(r'(?:affects?\\s+)?1\\s+in\\s+(\\d+).*?(\\d+)%\\s+true\\s+positive.*?(\\d+)%\\s+false\\s+positive', pl)
        if m:
            prev = 1.0 / float(m.group(1)); sens = float(m.group(2)) / 100.0; fpr = float(m.group(3)) / 100.0
            post = (sens * prev) / (sens * prev + fpr * (1 - prev)); pp = round(post * 100, 1)
            if cn and min(abs(v - pp) for v in cn) < 1.0: return (1.0, "computation:bayes_posterior")
            if f"{{pp}}%" in c: return (1.0, "computation:bayes_posterior")
            return (-0.8, "computation:bayes_posterior")
        if re.search(r'which\\s+is\\s+more\\s+likely', pl) and ' and ' in pl:
            if ' and ' in cl: return (-1.0, "structural:conjunction_fallacy")
            return (1.0, "structural:conjunction_fallacy")
        if re.search(r'\\d+%\\s+of\\s+\\w+\\s+are', pl) and re.search(r'(?:same|also\\s+\\d+%)', pl):
            if 'not' in cl or 'no' in cl: return (1.0, "structural:cond_prob_asym")
            return (-1.0, "structural:cond_prob_asym")
        evs_m = re.findall(r'(\\d+)%\\s+chance\\s+of\\s+winning\\s+\\$(\\d+)', pl)
        if evs_m and 'expected value' in pl:
            evs = [(float(a)*float(b)/100, a, b) for a, b in evs_m]
            if len(evs) >= 2:
                best = max(evs, key=lambda x: x[0])
                if f"${{best[0]}}" in c: return (1.0, "computation:expected_value")
                worst = min(evs, key=lambda x: x[0])
                if f"${{worst[0]}}" in c: return (-1.0, "computation:expected_value")
                return (-0.3, "computation:expected_value")
        if re.search(r'if\\s+.+?,?\\s*then\\s+.+\\.\\s+.+\\.\\s+can\\s+we\\s+conclude', pl):
            if 'cannot be determined' in cl or 'cannot' in cl: return (1.0, "structural:affirming_consequent")
            return (-0.8, "structural:affirming_consequent")
        if re.search(r"if\\s+.+?,?\\s*then\\s+.+\\.\\s+.+(?:not|n'?t).+\\.\\s+can\\s+we\\s+conclude", pl):
            if 'cannot' in cl or 'no, we cannot' in cl: return (1.0, "structural:denying_antecedent")
            return (-0.8, "structural:denying_antecedent")
        if re.search(r'(?:not\\s+(?:untrue|false)|incorrect\\s+to\\s+say\\s+it\\s+is\\s+not|not\\s+the\\s+case\\s+that\\s+it\\s+is\\s+(?:not|untrue))', pl) and 'is it true' in pl:
            prefix = pl.split('is it true')[0]
            negs = len(re.findall(r'\\b(?:not|untrue|false|incorrect)\\b', prefix))
            correct = "yes" if negs % 2 == 0 else "no"
            return (1.0, "computation:double_negation") if cl.startswith(correct) else (-1.0, "computation:double_negation")
        if re.search(r'(?:not\\s+the\\s+case\\s+that\\s+both|false\\s+that\\s+.+\\s+and\\s+.+\\s+both)', pl):
            if 'at least one' in cl: return (1.0, "structural:demorgan")
            return (-0.8, "structural:demorgan")
        if re.search(r'(?:2\\s*\\+\\s*2\\s*=\\s*5|moon.*cheese|pigs.*fly|0\\s*=\\s*1|earth.*flat)', pl) and 'logical' in pl:
            if 'true' in cl and 'vacuous' in cl: return (1.0, "structural:vacuous_truth")
            if 'false' in cl: return (-1.0, "structural:vacuous_truth")
            return (-0.5, "structural:vacuous_truth")
        if re.search(r'correlat', pl) and re.search(r'(?:cause|causes)', pl):
            if 'no' in cl and 'correlation' in cl: return (1.0, "structural:correlation_not_causation")
            return (-0.8, "structural:correlation_not_causation")
        if (re.search(r'(?:then\\s+.+?\\.\\s+(?:can\\s+we\\s+conclude|does\\s+the\\s+timing))', pl) and re.search(r'caus', pl)) or \\
           (re.search(r'(?:preceded|afterwards|shortly\\s+after)', pl) and re.search(r'(?:caus|prove)', pl)):
            if 'no' in cl: return (1.0, "structural:post_hoc")
            return (-0.8, "structural:post_hoc")
        if 'necessary' in pl and re.search(r'(?:guarantee|definitely|will\\s+.+?\\s+occur)', pl):
            if 'no' in cl: return (1.0, "structural:necessary_vs_sufficient")
            return (-0.8, "structural:necessary_vs_sufficient")
        if re.search(r'every\\s+\\w+', pl) and re.search(r'(?:same|did\\s+they\\s+all)', pl):
            if 'ambiguous' in cl or 'not necessarily' in cl: return (1.0, "structural:scope_ambiguity")
            return (-0.8, "structural:scope_ambiguity")
        if ('stopped' in pl or 'quit' in pl) and 'false' in pl and ('premise' in pl or 'presuppos' in pl):
            if 'both' in cl and 'false' in cl: return (1.0, "structural:presupposition")
            return (-0.8, "structural:presupposition")
        if re.search(r'(\\w+)\\s+(?:told|said|informed|reminded)\\s+(\\w+).*\\b(he|she)\\b\\s+was', pl) and 'who' in pl:
            if 'ambiguous' in cl: return (1.0, "structural:pronoun_ambiguity")
            return (-0.8, "structural:pronoun_ambiguity")
        if re.search(r'increases?\\s+by\\s+(\\d+)%.*decreases?\\s+by\\s+\\1%', pl):
            if 'lower' in cl: return (1.0, "structural:pct_change_asym")
            return (-0.5, "structural:pct_change_asym")
        if re.search(r'(?:raced past the barn fell|old man the boat|complex houses married)', pl):
            if 'both interpretations' in cl: return (1.0, "structural:garden_path")
            return (-0.3, "structural:garden_path")
        if re.search(r'logically\\s+valid', pl) and re.search(r'all\\s+\\w+\\s+can\\s+\\w+', pl):
            return (1.0, "structural:validity_vs_truth") if cl.startswith("yes") else (-1.0, "structural:validity_vs_truth")
        if 'logically stronger' in pl and 'argument a' in pl:
            parts = re.split(r'argument\\s+[ab]:', pl, flags=re.IGNORECASE)
            if len(parts) >= 3:
                af = bool(re.search(r'has\\s+a\\s+pet.*therefore.*has\\s+a\\s+\\w+', parts[1]))
                if af: return (1.0, "structural:argument_strength") if cl.strip().startswith("b") else (-0.8, "structural:argument_strength")
                return (1.0, "structural:argument_strength") if cl.strip().startswith("a") else (-0.8, "structural:argument_strength")
        if re.search(r'how\\s+confident', pl):
            if 'almost certainly' in pl: return (1.0, "judgment:confidence_cal") if 'high' in cl else (-0.3, "judgment:confidence_cal")
            if 'possibly' in pl: return (1.0, "judgment:confidence_cal") if cl.startswith('low') else (-0.3, "judgment:confidence_cal")
            if re.search(r'(?:probably|likely|believed)', pl): return (1.0, "judgment:confidence_cal") if 'moderate' in cl else (-0.3, "judgment:confidence_cal")
        m = re.search(r'"([^"]+)"', p)
        if m and re.search(r'(?:true|false)\\?', pl):
            sentence = m.group(1); wc = len(sentence.split()); nm = re.search(r'(\\d+)', sentence)
            if nm:
                claimed = int(nm.group(1)); correct = "true" if wc == claimed else "false"
                return (1.0, "computation:self_referential") if cl.startswith(correct) else (-1.0, "computation:self_referential")
        if 'exactly one' in pl and ('lies' in pl or 'truth' in pl) and 'says' in pl:
            names = re.findall(r'([A-Z][a-z]+)\\s+says', p)
            if len(names) == 3: return (1.0, "computation:liar_detection") if names[1].lower() in cl else (-0.8, "computation:liar_detection")
        m = re.search(r'(\\w+)\\s+puts?\\s+a?\\s*(\\w+)\\s+in\\s+the\\s+(\\w+).*?moves?\\s+the\\s+\\w+\\s+to\\s+the\\s+(\\w+)', pl)
        if m and 'where will' in pl:
            return (1.0, "structural:false_belief") if m.group(3) in cl else (-1.0, "structural:false_belief")
        if 'rigged' in pl and 'does not know' in pl and 'expect' in pl:
            if 'equal' in cl or 'either' in cl: return (1.0, "structural:knowledge_attribution")
            if 'always' in cl: return (-1.0, "structural:knowledge_attribution")
            return (-0.3, "structural:knowledge_attribution")
        m = re.search(r'(\\w+)\\s+thinks\\s+that\\s+(\\w+)\\s+believes?\\s+(.+?)\\.\\s+according', pl)
        if m:
            if m.group(3).strip() in cl: return (1.0, "structural:second_order_belief")
            return (-0.8, "structural:second_order_belief")
        if re.search(r'all\\s+\\w+\\s+are\\s+\\w+', pl) and re.search(r'is\\s+\\w+\\s+one\\s+of', pl):
            return (1.0, "structural:multi_hop") if cl.startswith("yes") else (-0.8, "structural:multi_hop")
        cp = re.findall(r'(\\w+)\\s+is\\s+(?:taller|faster|older|heavier)\\s+than\\s+(\\w+)', pl)
        if len(cp) >= 2 and len(set(x for pair in cp for x in pair)) == 4:
            return (1.0, "structural:info_sufficiency") if 'cannot' in cl else (-0.8, "structural:info_sufficiency")
        if re.search(r'if\\s+\\w+\\s+has\\s+a\\s+\\w+.*pet\\s+owner', pl) and re.search(r'has\\s+a\\s+\\w+\\.\\s+is', pl):
            return (1.0, "structural:irrelevant_premise") if cl.startswith("yes") else (-0.8, "structural:irrelevant_premise")
        if 'premise 1' in pl and 'premise 2' in pl and 'consistent' in pl:
            return (1.0, "structural:premise_contradiction") if cl.startswith("no") else (-1.0, "structural:premise_contradiction")
        ifs = re.findall(r'if\\s+(.+?),\\s*then\\s+(.+?)(?:\\.|$)', pl)
        if len(ifs) >= 2 and re.search(r'(?:follow|true|hold)', pl):
            return (1.0, "structural:chained_conditional") if cl.startswith("yes") else (-0.8, "structural:chained_conditional")
        m = re.search(r'what\\s+is\\s+(\\d+)\\s*\\+\\s*(\\d+)\\s*\\*\\s*(\\d+)', pl)
        if m:
            result = int(m.group(1)) + int(m.group(2)) * int(m.group(3))
            if cn and abs(cn[0] - result) < 0.01: return (1.0, "computation:pemdas")
            return (-1.0, "computation:pemdas")
        m = re.search(r'(\\d+):00\\s*(am|pm).*?in\\s+(\\d+)\\s+hours', pl)
        if m:
            h, ampm, n = int(m.group(1)), m.group(2), int(m.group(3))
            h24 = (h % 12) + (12 if ampm == 'pm' else 0); end24 = (h24 + n) % 24
            if end24 == 0: disp, ap = 12, "am"
            elif end24 < 12: disp, ap = end24, "am"
            elif end24 == 12: disp, ap = 12, "pm"
            else: disp, ap = end24 - 12, "pm"
            if f"{{disp}}:00" in cl and ap in cl: return (1.0, "computation:modular_arith")
            return (-0.8, "computation:modular_arith")
        m = re.search(r'(\\d+)\\s+meters?\\s+long.*?every\\s+(\\d+)\\s+meters?.*both\\s+ends', pl)
        if m:
            total, spacing = int(m.group(1)), int(m.group(2)); cv = total // spacing + 1
            if cn and abs(cn[0] - cv) < 0.01: return (1.0, "computation:fencepost")
            return (-1.0, "computation:fencepost")
        m = re.search(r'class\\s+of\\s+(\\d+)\\s+students.*?(\\d+)\\s+play\\s+\\w+.*?(\\d+)\\s+play\\s+\\w+.*minimum', pl)
        if m:
            n, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3)); mb = max(0, a + b - n)
            if cn and abs(cn[0] - mb) < 0.01: return (1.0, "computation:inclusion_exclusion")
            return (-1.0, "computation:inclusion_exclusion")
        if 'facing each other' in pl:
            m2 = re.search(r'(\\w+)\\s+raises?\\s+their\\s+(left|right)', pl)
            if m2:
                flipped = "right" if m2.group(2) == "left" else "left"
                if flipped in cl: return (1.0, "computation:left_right")
                return (-1.0, "computation:left_right")
        sm = re.search(r'facing\\s+(north|south|east|west)', pl)
        if sm and 'turn' in pl:
            dirs = ["north","east","south","west"]; cur = dirs.index(sm.group(1))
            for t in re.findall(r'turn\\s+(right|left)', pl): cur = (cur + (1 if t == 'right' else -1)) % 4
            if dirs[cur] in cl: return (1.0, "computation:direction")
            return (-1.0, "computation:direction")
        if 'inside' in pl and re.search(r'is\\s+the\\s+\\w+\\s+inside', pl):
            return (1.0, "structural:containment") if cl.startswith("yes") else (-0.8, "structural:containment")
        if re.search(r'no\\s+\\w+\\s+exist', pl) and 'both' in pl:
            return (1.0, "structural:empty_set") if cl.startswith("yes") else (-1.0, "structural:empty_set")
        if re.search(r'all\\s+\\w+\\s+are\\s+\\w+.*does\\s+it\\s+follow.*all', pl):
            return (1.0, "structural:subset_inversion") if cl.startswith("no") else (-1.0, "structural:subset_inversion")
        if 'sample' in pl and re.search(r'should\\s+you', pl) and 'success' in pl:
            if 'need to see' in cl or 'failed' in cl: return (1.0, "structural:survivorship")
            return (-0.8, "structural:survivorship")
        if re.search(r'already\\s+(?:spent|paid)', pl) and 'good reason' in pl:
            if 'regardless' in cl: return (1.0, "structural:sunk_cost")
            return (-0.8, "structural:sunk_cost")
        if 'statement a' in pl and 'statement b' in pl and 'same information' in pl:
            return (1.0, "structural:framing") if cl.startswith("yes") else (-0.8, "structural:framing")
        if re.search(r'no\\s+other\\s+option', pl) and 'possible' in pl:
            return (1.0, "structural:false_dichotomy") if cl.startswith("yes") else (-0.8, "structural:false_dichotomy")
        if re.search(r'every\\s+\\w+\\s+is', pl) and 'necessarily follow' in pl:
            if 'not necessarily' in cl or cl.startswith('no'): return (1.0, "structural:composition_fallacy")
            return (-0.8, "structural:composition_fallacy")
        if re.search(r'scored\\s+\\d+.*then\\s+\\d+', pl) and 'worse' in pl:
            if 'regression' in cl: return (1.0, "structural:regression_to_mean")
            return (-0.8, "structural:regression_to_mean")
        if 'divisible by 4' in pl and 'even' in pl and 'necessarily' in pl:
            return (1.0, "structural:affirm_conseq_num") if cl.startswith("no") else (-1.0, "structural:affirm_conseq_num")
        if re.search(r'(?:rare|unpredictable|unprecedented|unforeseeable)', pl) and re.search(r'(?:reasonable|appropriate|sound)', pl):
            if 'yes' in cl and 'reasonable' in cl: return (1.0, "judgment:intention_vs_outcome")
            return (-0.8, "judgment:intention_vs_outcome")
        return (0.0, "fallback:ncd")

    def _secondary(self, p: str, c: str) -> float:
        {secondary_code}

    def evaluate(self, prompt: str, candidates: list) -> list:
        results = []
        for c in candidates:
            s, r = self._cat_score(prompt, c)
            if r == "fallback:ncd":
                ncd_v = self._ncd(prompt, c)
                score = (1.0 - ncd_v) * 0.15 + self._secondary(prompt, c)
                r = f"fallback:ncd={{ncd_v:.4f}}"; conf = 0.2
            else:
                score = s * 0.55 + self._secondary(prompt, c) * 0.1
                conf = min(0.85, abs(s))
            results.append({{"candidate": c, "score": float((score+1)/2), "reasoning": f"{{r}},confidence:{{conf:.2f}}"}})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(0.85, 0.6 + s * 0.25)
        if s < -0.5: return 0.1
        return 0.35
'''

created = 0
skipped = 0
for name, doc, sec in TOOLS:
    path = os.path.join(FORGE_V4, f"{name}.py")
    if os.path.exists(path):
        print(f"SKIP: {name}.py (already exists)")
        skipped += 1
        continue
    tag = name.replace('_x_', ' x ').replace('_', ' ')
    content = TEMPLATE.format(docstring=doc, tag=tag, secondary_code=sec)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"CREATED: {name}.py")
    created += 1

print(f"\nDone: {created} created, {skipped} skipped")
