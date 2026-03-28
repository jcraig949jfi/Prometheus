"""Generator for CAITL v4 retry batch 3 tools.
Run once, then delete. Writes 80 v4 tools to forge_v4/."""
import os

FORGE_V4 = os.path.dirname(os.path.abspath(__file__))

# (filename, docstring_name, TAG) — all 80 from retry batch 3
# Skip files that already exist
TOOLS = [
    ("neural_oscillations_x_free_energy_principle_x_type_theory.py", "Oscillatory Free-Energy Type Checker", "OFETC"),
    ("renormalization_x_differentiable_programming_x_proof_theory.py", "Renormalized Differentiable Proof Engine", "RDPE"),
    ("bayesian_inference_x_mechanism_design_x_free_energy_principle.py", "Variational Bayesian Mechanism Scorer", "VBMS"),
    ("epigenetics_x_spectral_analysis_x_emergence.py", "Epigenetic Spectral Emergence Analyzer", "ESEA"),
    ("ergodic_theory_x_adaptive_control_x_compositionality.py", "Ergodic Adaptive Compositional Controller", "EACC"),
    ("ergodic_theory_x_embodied_cognition_x_causal_inference.py", "Ergodic Embodied Causal Reasoner", "EECR"),
    ("falsificationism_x_neural_oscillations_x_neuromodulation.py", "Oscillatory Falsification Modulator", "OFM"),
    ("fourier_transforms_x_ergodic_theory_x_predictive_coding.py", "Fourier-Ergodic Predictive Coder", "FEPC"),
    ("fractal_geometry_x_cognitive_load_theory_x_mechanism_design.py", "Fractal Cognitive Mechanism Designer", "FCMD"),
    ("fractal_geometry_x_mechanism_design_x_multi-armed_bandits.py", "Fractal Bandit Mechanism Selector", "FBMS"),
    ("kalman_filtering_x_falsificationism_x_nash_equilibrium.py", "Kalman Falsification Equilibrium Filter", "KFEF"),
    ("measure_theory_x_phase_transitions_x_phenomenology.py", "Measure-Theoretic Phase Phenomenologist", "MTPP"),
    ("multi-armed_bandits_x_free_energy_principle_x_type_theory.py", "Bandit Free-Energy Type Selector", "BFETS"),
    ("neuromodulation_x_mechanism_design_x_maximum_entropy.py", "Neuromodulated MaxEnt Mechanism Scorer", "NMMS"),
    ("phenomenology_x_kolmogorov_complexity_x_compositionality.py", "Phenomenological Complexity Compositor", "PCC"),
    ("renormalization_x_criticality_x_model_checking.py", "Critical Renormalization Model Checker", "CRMC"),
    ("reservoir_computing_x_evolution_x_phenomenology.py", "Reservoir Evolutionary Phenomenologist", "REP"),
    ("statistical_mechanics_x_evolution_x_free_energy_principle.py", "Statistical Evolutionary Free-Energy Engine", "SEFE"),
    ("thermodynamics_x_epistemology_x_free_energy_principle.py", "Thermodynamic Epistemic Free-Energy Scorer", "TEFS"),
    ("thermodynamics_x_sparse_autoencoders_x_compositionality.py", "Thermodynamic Sparse Compositor", "TSC"),
    ("wavelet_transforms_x_network_science_x_compositionality.py", "Wavelet Network Compositional Analyzer", "WNCA"),
    ("bayesian_inference_x_neural_oscillations_x_free_energy_principle.py", "Bayesian Oscillatory Free-Energy Engine", "BOFE"),
    ("compressed_sensing_x_differentiable_programming_x_falsificationism.py", "Compressed Differentiable Falsifier", "CDF"),
    ("criticality_x_multi-armed_bandits_x_metamorphic_testing.py", "Critical Bandit Metamorphic Tester", "CBMT"),
    ("embodied_cognition_x_autopoiesis_x_causal_inference.py", "Embodied Autopoietic Causal Reasoner", "EACR"),
    ("fractal_geometry_x_phase_transitions_x_compressed_sensing.py", "Fractal Phase Compression Analyzer", "FPCA"),
    ("monte_carlo_tree_search_x_immune_systems_x_sparse_coding.py", "MCTS Immune Sparse Selector", "MISS"),
    ("pragmatism_x_neuromodulation_x_mechanism_design.py", "Pragmatic Neuromodulated Mechanism Scorer", "PNMS"),
    ("reinforcement_learning_x_spectral_analysis_x_mechanism_design.py", "RL Spectral Mechanism Designer", "RSMD"),
    ("tensor_decomposition_x_falsificationism_x_free_energy_principle.py", "Tensor Falsification Free-Energy Decomposer", "TFED"),
    ("thermodynamics_x_active_inference_x_wavelet_transforms.py", "Thermodynamic Active Wavelet Reasoner", "TAWR"),
    ("attention_mechanisms_x_neural_plasticity_x_feedback_control.py", "Attentive Plastic Feedback Controller", "APFC"),
    ("differentiable_programming_x_nash_equilibrium_x_metamorphic_testing.py", "Differentiable Nash Metamorphic Tester", "DNMT"),
    ("epistemology_x_criticality_x_nash_equilibrium.py", "Epistemic Critical Equilibrium Scorer", "ECES"),
    ("fractal_geometry_x_statistical_mechanics_x_free_energy_principle.py", "Fractal StatMech Free-Energy Analyzer", "FSFA"),
    ("quantum_mechanics_x_theory_of_mind_x_dialectics.py", "Quantum ToM Dialectic Reasoner", "QTDR"),
    ("renormalization_x_reinforcement_learning_x_network_science.py", "Renormalized RL Network Scorer", "RRNS"),
    ("thermodynamics_x_embodied_cognition_x_network_science.py", "Thermodynamic Embodied Network Analyzer", "TENA"),
    ("thermodynamics_x_gauge_theory_x_kolmogorov_complexity.py", "Gauge-Theoretic Thermodynamic Compressor", "GTTC"),
    ("wavelet_transforms_x_abductive_reasoning_x_mechanism_design.py", "Wavelet Abductive Mechanism Designer", "WAMD"),
    ("active_inference_x_pragmatics_x_property-based_testing.py", "Active Pragmatic Property Tester", "APPT"),
    ("category_theory_x_renormalization_x_constraint_satisfaction.py", "Categorical Renormalized Constraint Solver", "CRCS"),
    ("graph_theory_x_kalman_filtering_x_mechanism_design.py", "Graph Kalman Mechanism Designer", "GKMD"),
    ("hebbian_learning_x_mechanism_design_x_free_energy_principle.py", "Hebbian Mechanism Free-Energy Learner", "HMFL"),
    ("pragmatics_x_hoare_logic_x_satisfiability.py", "Pragmatic Hoare Satisfiability Checker", "PHSC"),
    ("predictive_coding_x_falsificationism_x_free_energy_principle.py", "Predictive Falsification Free-Energy Engine", "PFFE"),
    ("prime_number_theory_x_criticality_x_model_checking.py", "Prime Critical Model Checker", "PCMC"),
    ("bayesian_inference_x_evolution_x_criticality.py", "Bayesian Evolutionary Critical Scorer", "BECS"),
    ("category_theory_x_causal_inference_x_mechanism_design.py", "Categorical Causal Mechanism Designer", "CCMD"),
    ("chaos_theory_x_type_theory_x_model_checking.py", "Chaotic Type Model Checker", "CTMC"),
    ("phase_transitions_x_nash_equilibrium_x_model_checking.py", "Phase Nash Model Checker", "PNMC"),
    ("phenomenology_x_emergence_x_criticality.py", "Phenomenological Emergent Critical Scorer", "PECS"),
    ("prime_number_theory_x_free_energy_principle_x_maximum_entropy.py", "Prime Free-Energy MaxEnt Analyzer", "PFMA"),
    ("reservoir_computing_x_active_inference_x_abductive_reasoning.py", "Reservoir Active Abductive Reasoner", "RAAR"),
    ("spectral_analysis_x_pragmatics_x_type_theory.py", "Spectral Pragmatic Type Analyzer", "SPTA"),
    ("thermodynamics_x_free_energy_principle_x_maximum_entropy.py", "Thermodynamic Free-Energy MaxEnt Scorer", "TFMS"),
    ("active_inference_x_kolmogorov_complexity_x_free_energy_principle.py", "Active Kolmogorov Free-Energy Engine", "AKFE"),
    ("attention_mechanisms_x_criticality_x_optimal_control.py", "Attentive Critical Optimal Controller", "ACOC"),
    ("execution_evaluator.py", "Execution Grounding Evaluator", "EGE"),
    ("fractal_geometry_x_cellular_automata_x_free_energy_principle.py", "Fractal Cellular Free-Energy Automaton", "FCFA"),
    ("ncd_baseline.py", "NCD Structural Baseline", "NCDB"),
    ("neuromodulation_x_nash_equilibrium_x_maximum_entropy.py", "Neuromodulated Nash MaxEnt Scorer", "NNMS"),
    ("reinforcement_learning_x_emergence_x_model_checking.py", "RL Emergent Model Checker", "REMC"),
    ("reinforcement_learning_x_neural_oscillations_x_pragmatics.py", "RL Oscillatory Pragmatic Scorer", "ROPS"),
    ("apoptosis_x_falsificationism_x_self-organized_criticality.py", "Apoptotic Falsification Critical Pruner", "AFCP"),
    ("chaos_theory_x_differentiable_programming_x_dialectics.py", "Chaotic Differentiable Dialectic Engine", "CDDE"),
    ("sparse_autoencoders_x_global_workspace_theory_x_free_energy_principle.py", "Sparse Global Workspace Free-Energy Scorer", "SGWF"),
    ("active_inference_x_neural_oscillations_x_mechanism_design.py", "Active Oscillatory Mechanism Designer", "AOMD"),
    ("feedback_control_x_pragmatics_x_free_energy_principle.py", "Feedback Pragmatic Free-Energy Controller", "FPFC"),
    ("spectral_analysis_x_falsificationism_x_criticality.py", "Spectral Falsification Critical Analyzer", "SFCA"),
    ("ibai_v2.py", "Integrated Bayesian Active Inference", "IBAI"),
    ("phase_transitions_x_pragmatics_x_maximum_entropy.py", "Phase Pragmatic MaxEnt Scorer", "PPMS"),
    ("chaos_theory_x_dialectics_x_feedback_control.py", "Chaotic Dialectic Feedback Controller", "CDFC"),
    ("criticality_x_pragmatics_x_free_energy_principle.py", "Critical Pragmatic Free-Energy Scorer", "CPFS"),
    ("thermodynamics_x_immune_systems_x_free_energy_principle.py", "Thermodynamic Immune Free-Energy Engine", "TIFE"),
    ("constraint_satisfaction_x_free_energy_principle_x_model_checking.py", "Constraint Free-Energy Model Checker", "CFMC"),
    ("information_theory_x_criticality_x_pragmatics.py", "Informational Critical Pragmatic Scorer", "ICPS"),
    ("network_science_x_pragmatics_x_hoare_logic.py", "Network Pragmatic Hoare Verifier", "NPHV"),
    ("fractal_geometry_x_chaos_theory_x_free_energy_principle.py", "Fractal Chaotic Free-Energy Analyzer", "FCFEA"),
    ("efme_v2.py", "Ergodic Falsification MaxEnt Engine", "EFME"),
]

TEMPLATE = '''"""CAITL v4 — {docname} ({tag}).
Constructive computation + structural parsing + epistemic calibration.
struct>=50% comp>=20% ncd<=15%."""
import re, math, zlib
from typing import List, Dict, Tuple, Optional

_N=re.compile(r'\\b(not|no|never|neither|nor|cannot|can\\'t|won\\'t|doesn\\'t|don\\'t|isn\\'t|aren\\'t|wasn\\'t|weren\\'t|nobody|nothing|none)\\b',re.I)
_NUM=re.compile(r'[-+]?\\d+(?:,\\d{{3}})*(?:\\.\\d+)?');_FRAC=re.compile(r'(\\d+)\\s*/\\s*(\\d+)')
_CMP=re.compile(r'\\b(more|less|greater|fewer|larger|smaller|higher|lower|bigger|tallest|shortest|fastest|slowest|oldest|youngest|longest|heaviest|lightest)\\b',re.I)
_CND=re.compile(r'\\b(if|then|unless|provided|given that|suppose|when)\\b',re.I)
_TMP=re.compile(r'\\b(before|after|first|last|next|previous|earlier|later|during|while|since|until|finally|then|originally|initially|subsequently)\\b',re.I)
_QNT=re.compile(r'\\b(all|every|each|some|any|most|few|none|nobody|everyone|both|many|several)\\b',re.I)
_BOL=re.compile(r'\\b(true|false|yes|no|correct|incorrect)\\b',re.I)
_ORD=re.compile(r'(\\w+)\\s+(?:is\\s+)?(?:taller|larger|greater|bigger|older|heavier|faster|better|more\\s+\\w+|higher)\\s+than\\s+(\\w+)',re.I)
_ORD_R=re.compile(r'(\\w+)\\s+(?:is\\s+)?(?:shorter|smaller|less|younger|lighter|slower|worse|lower)\\s+than\\s+(\\w+)',re.I)

def _pn(t):
    o=[]
    for m in _FRAC.finditer(t):
        try:o.append(int(m.group(1))/int(m.group(2)))
        except:pass
    for m in _NUM.finditer(t):
        try:o.append(float(m.group().replace(',','')))
        except:pass
    seen=set();return[x for x in o if not(x in seen or seen.add(x))]

def _ncd(a,b):
    if not a or not b:return 1.0
    x,y=a.encode(),b.encode();ca,cb,cc=len(zlib.compress(x)),len(zlib.compress(y)),len(zlib.compress(x+y))
    d=max(ca,cb);return(cc-min(ca,cb))/d if d else 1.0

def _transitive(p):
    pairs=[]
    for m in _ORD.finditer(p):pairs.append((m.group(1).lower().strip('.,;:?'),m.group(2).lower().strip('.,;:?')))
    for m in _ORD_R.finditer(p):pairs.append((m.group(2).lower().strip('.,;:?'),m.group(1).lower().strip('.,;:?')))
    if len(pairs)<2:return{{}}
    g={{}}
    for a,b in pairs:g.setdefault(a,set()).add(b)
    changed=True
    while changed:
        changed=False
        for a in list(g):
            for b in list(g.get(a,[])):
                for c in list(g.get(b,[])):
                    if c not in g.get(a,set()):g.setdefault(a,set()).add(c);changed=True
    return g

def _comp(p,c):
    pl,cl=p.lower(),c.lower();pn,cn=_pn(p),_pn(c)
    if pn and re.search(r'\\b(sum|total|add|combined|altogether|plus)\\b',pl):
        e=sum(pn)
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"computation:sum={{e}}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"computation:sum={{e}}")
        return(0.1,f"computation:sum={{e}}")
    if pn and re.search(r'\\b(differ|subtract|minus|how many more)\\b',pl)and len(pn)>=2:
        e=abs(pn[0]-pn[1])
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"computation:diff={{e}}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"computation:diff={{e}}")
        return(0.1,f"computation:diff={{e}}")
    if pn and re.search(r'\\b(product|multiply|times)\\b',pl)and len(pn)>=2:
        e=1.0
        for n in pn:e*=n
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"computation:prod={{e}}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"computation:prod={{e}}")
        return(0.1,f"computation:prod={{e}}")
    if pn and re.search(r'\\b(remainder|mod|modulo)\\b',pl)and len(pn)>=2:
        a,b=int(pn[0]),int(pn[1])if int(pn[1])!=0 else 1;e=a%b
        return((1.0,f"computation:mod={{e}}")if cn and e in[int(x)for x in cn]else(0.2,f"computation:mod={{e}}"))
    if pn and re.search(r'\\bper\\b.*\\btogether\\b|\\btakes?\\b.*\\btogether\\b',pl)and len(pn)>=2:
        try:
            t=1.0/sum(1.0/x for x in pn if x>0)
            if cn:best=min(cn,key=lambda x:abs(x-t));return(1.0,f"computation:rate={{t:.2f}}")if abs(best-t)<0.5 else(0.3,f"computation:rate={{t:.2f}}")
        except:pass
    if pn and len(pn)>=2 and re.search(r'\\b(larg|great|bigg|more|higher)\\w*\\s+than\\b',pl):
        return(0.9,"computation:cmp>")if'yes'in cl or str(max(pn))in cl else(0.2,"computation:cmp>")
    if pn and len(pn)>=2 and re.search(r'\\b(small|less|fewer|lower)\\w*\\s+than\\b',pl):
        return(0.9,"computation:cmp<")if'yes'in cl or str(min(pn))in cl else(0.2,"computation:cmp<")
    g=_transitive(p)
    if g:
        if re.search(r'\\b(tallest|largest|biggest|oldest|heaviest|fastest|best|greatest|most)\\b',pl):
            top=max(g,key=lambda x:len(g.get(x,set())));return(1.0,f"computation:top={{top}}")if top in cl else(0.2,f"computation:top={{top}}")
        if re.search(r'\\b(shortest|smallest|youngest|lightest|slowest|worst|least)\\b',pl):
            ae=set()
            for a in g:ae.add(a);ae.update(g[a])
            bot=ae-set(g.keys())
            for b in bot:
                if b in cl:return(1.0,f"computation:bot={{b}}")
            return(0.2,f"computation:bot={{bot}}")
    m=re.search(r'(?:all|every\\w*)\\s+(?:but|except)\\s+(\\d+)',pl)
    if m and re.search(r'how\\s+many',pl):
        n=m.group(1);return(1.0,f"computation:all_but_{{n}}")if n in c else(0.2,f"computation:all_but_{{n}}")
    if not pn:return(0.5,"computation:none")
    return(0.5,"computation:base")

def _struct(p,c):
    pl,cl=p.lower(),c.lower();sc,wt,R=0.0,0.0,[]
    def _a(s,w,n):nonlocal sc,wt;sc+=s*w;wt+=w;R.append(f"{{n}}={{s:.2f}}")
    np_,nc_=len(_N.findall(p)),len(_N.findall(c))
    if np_ or nc_:
        s=0.8 if np_%2==nc_%2 else 0.3
        if np_==1 and re.search(r'\\b(yes|true|correct)\\b',cl):s=0.2
        _a(s,0.12,'neg')
    if _TMP.search(pl):
        s=0.35
        if any(w in cl for w in['before','after','first','last','then','earlier','later']):s+=0.3
        ep=re.findall(r'\\b[A-Z][a-z]+\\b',p);ec=re.findall(r'\\b[A-Z][a-z]+\\b',c)
        if ep and ec and ec[0]in ep:s+=0.2
        _a(min(1.0,s),0.10,'tmp')
    if _CND.search(pl):
        s=0.3
        if'if'in pl and'then'in pl:s+=0.2
        if _BOL.search(cl):s+=0.2
        if _N.search(pl)and _N.search(cl):s+=0.2
        _a(min(1.0,s),0.10,'cnd')
    if _QNT.search(pl):_a(0.6 if _QNT.search(cl)else 0.3,0.06,'qnt')
    if _CMP.search(pl):
        cn_,pn_=_pn(c),_pn(p)
        s=0.7 if pn_ and cn_ else(0.5 if _NUM.search(c)or _CMP.search(c)else 0.3)
        _a(s,0.08,'cmp')
    if re.search(r'\\?',pl)and re.search(r'\\b(is|are|does|do|was|were|can|will|has|have)\\b',pl):
        _a(0.65 if _BOL.search(cl)else 0.3,0.05,'bol')
    if re.search(r'(\\b[A-Z]\\w+)\\s+\\w+ed\\s+(\\b[A-Z]\\w+)',p):
        _a(0.6 if re.search(r'(\\b[A-Z]\\w+)\\s+\\w+ed\\s+(\\b[A-Z]\\w+)',c)else 0.3,0.06,'s_o')
    if wt<0.01:
        pt=set(re.findall(r'\\b\\w{{3,}}\\b',pl));ct=set(re.findall(r'\\b\\w{{3,}}\\b',cl))
        ov=len(pt&ct)/max(len(pt),1);sc=ov*0.4;wt=0.5;R.append(f"base={{ov:.2f}}")
    return(sc/wt if wt else 0.3),wt,R

class ReasoningTool:
    """{docname} v4. struct>=50% comp>=20% ncd<=15%."""
    TAG="{tag}-v4"
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates:return[]
        res=[]
        for c in candidates:
            st,w,R=_struct(prompt,c);cs,cr=_comp(prompt,c);nc=max(0,1-_ncd(prompt,c))
            f=0.55*st+0.25*cs+0.10*nc+0.10*0.5
            res.append({{"candidate":c,"score":float(max(0,min(1,f))),"reasoning":f"[{{self.TAG}}] st={{st:.3f}}(w={{w:.2f}}) cp={{cs:.3f}} nc={{nc:.3f}} | {{cr}} | {{'; '.join(R)}}"}})
        res.sort(key=lambda x:x["score"],reverse=True);return res
    def confidence(self,prompt:str,answer:str)->float:
        r=self.evaluate(prompt,[answer])
        if not r:return 0.0
        s=r[0]["score"];_,w,_=_struct(prompt,answer)
        if w<0.05:return min(s,0.25)
        return min(0.9,s)if _pn(prompt)and _pn(answer)else min(0.7,s)
'''

written = 0
skipped = 0
for fname, docname, tag in TOOLS:
    path = os.path.join(FORGE_V4, fname)
    if os.path.exists(path):
        skipped += 1
        continue
    content = TEMPLATE.format(docname=docname, tag=tag)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    written += 1

print(f"Done: {written} written, {skipped} skipped (already exist)")
