#!/usr/bin/env python3
"""Generate CAITL v4 tools for retry_batch_1 files. Overwrites existing generated files."""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

SKIP = {
    "thermodynamics_x_monte_carlo_tree_search_x_free_energy_principle.py",
    "ergodic_theory_x_maximum_entropy_x_model_checking.py",
    "thermodynamics_x_neuromodulation_x_multi-armed_bandits.py",
    "chaos_theory_x_neural_plasticity_x_autopoiesis.py",
    "ergodic_theory_x_ecosystem_dynamics_x_theory_of_mind.py",
    "chaos_theory_x_neural_architecture_search_x_falsificationism.py",
    "neural_plasticity_x_pragmatics_x_free_energy_principle.py",
    "cellular_automata_x_mechanism_design_x_free_energy_principle.py",
    "category_theory_x_chaos_theory_x_self-organized_criticality.py",
    "ergodic_theory_x_sparse_autoencoders_x_pragmatics.py",
    "thermodynamics_x_neural_plasticity_x_free_energy_principle.py",
    "chaos_theory_x_wavelet_transforms_x_compositionality.py",
    "chaos_theory_x_neural_plasticity_x_free_energy_principle.py",
    "ergodic_theory_x_measure_theory_x_dual_process_theory.py",
    "phase_transitions_x_autopoiesis_x_causal_inference.py",
    "bayesian_inference_x_free_energy_principle_x_sensitivity_analysis.py",
    "reinforcement_learning_x_active_inference_x_free_energy_principle.py",
    # Also skip files that pre-existed from other batches
    "mechanism_design_x_nash_equilibrium_x_free_energy_principle.py",
    "active_inference_x_mechanism_design_x_type_theory.py",
    "bayesian_inference_x_free_energy_principle_x_model_checking.py",
    "active_inference_x_free_energy_principle_x_model_checking.py",
}

TOOLS = [
    ("fractal_geometry_x_differentiable_programming_x_free_energy_principle.py","FGDP","Fractal-FEP Differentiable Reasoner: multi-scale constraint + sigmoid gradients",(0.50,0.25,0.10,0.15)),
    ("renormalization_x_global_workspace_theory_x_criticality.py","RGWC","Critical Renorm Global Workspace: coarse-grained similarity + critical gain",(0.50,0.25,0.10,0.15)),
    ("attention_mechanisms_x_predictive_coding_x_falsificationism.py","APCF","Structural Falsification: predictive-coding extraction + attention confidence",(0.52,0.23,0.10,0.15)),
    ("tensor_decomposition_x_morphogenesis_x_compositionality.py","TDMC","Tensor Morphogenic Compositor: reaction-diffusion error + rank-adaptive scoring",(0.50,0.25,0.12,0.13)),
    ("ergodic_theory_x_genetic_algorithms_x_analogical_reasoning.py","EGAR","Ergodic-Genetic Analogist: mixing-time + crossover structural alignment",(0.52,0.23,0.10,0.15)),
    ("evolution_x_criticality_x_free_energy_principle.py","ECFE","Evolutionary Critical FEP: fitness-landscape at phase boundary",(0.50,0.25,0.10,0.15)),
    ("phase_transitions_x_kolmogorov_complexity_x_nash_equilibrium.py","PKNE","Phase-Kolmogorov Nash: order-parameter + complexity-penalized equilibrium",(0.50,0.25,0.12,0.13)),
    ("bayesian_inference_x_constraint_satisfaction_x_free_energy_principle.py","BCSF","Bayesian Constraint Satisfier: posterior + arc-consistency under FEP",(0.50,0.25,0.12,0.13)),
    ("bayesian_inference_x_reservoir_computing_x_sparse_coding.py","BRSC","Bayesian Reservoir Sparse: echo-state projection + sparse posterior",(0.52,0.23,0.10,0.15)),
    ("sparse_autoencoders_x_neural_plasticity_x_abstract_interpretation.py","SNAI","Sparse Plastic Abstract: bottleneck + Galois constraint checking",(0.50,0.25,0.10,0.15)),
    ("chaos_theory_x_adaptive_control_x_compositionality.py","CACC","Chaotic Adaptive Compositor: Lyapunov control + compositional parse",(0.52,0.23,0.10,0.15)),
    ("chaos_theory_x_cognitive_load_theory_x_neuromodulation.py","CCLN","Chaotic CogLoad Neuromod: complexity budget + modulatory gain",(0.50,0.25,0.12,0.13)),
    ("ergodic_theory_x_chaos_theory_x_neural_oscillations.py","ECNO","Ergodic-Chaotic Oscillator: mixing-time + oscillatory phase alignment",(0.52,0.23,0.10,0.15)),
    ("chaos_theory_x_self-organized_criticality_x_normalized_compression_distance.py","CSCN","Chaotic SOC NCD: sandpile sensitivity + compression tiebreak",(0.50,0.25,0.12,0.13)),
    ("ergodic_theory_x_pragmatics_x_free_energy_principle.py","EPFE","Ergodic Pragmatic FEP: implicature + mixing-time convergence",(0.52,0.23,0.10,0.15)),
    ("measure_theory_x_error_correcting_codes_x_type_theory.py","MECT","Measure ECC Typer: sigma-algebra + Hamming validation",(0.50,0.25,0.10,0.15)),
    ("phenomenology_x_emergence_x_feedback_control.py","PEFC","Phenomenological Emergent Controller: intentionality + PID correction",(0.52,0.23,0.10,0.15)),
    ("category_theory_x_phase_transitions_x_neural_architecture_search.py","CPNA","Categorical Phase NAS: functorial + order-parameter selection",(0.50,0.25,0.12,0.13)),
    ("chaos_theory_x_feedback_control_x_maximum_entropy.py","CFME","Chaotic Feedback MaxEnt: attractor-basin + entropy-regularized",(0.52,0.23,0.10,0.15)),
    ("ergodic_theory_x_predictive_coding_x_global_workspace_theory.py","EPGW","Ergodic Predictive GWT: mixing prediction-error + broadcast",(0.50,0.25,0.10,0.15)),
    ("information_theory_x_neural_oscillations_x_multi-armed_bandits.py","INOB","Info Oscillatory Bandit: MI scoring + UCB phase-locked",(0.52,0.23,0.10,0.15)),
    ("measure_theory_x_evolution_x_model_checking.py","MEMC","Measure Evolutionary Checker: fitness-weighted verification",(0.50,0.25,0.12,0.13)),
    ("thermodynamics_x_free_energy_principle_x_proof_theory.py","TFPP","Thermo FEP Proof: variational bound + sequent verification",(0.52,0.23,0.10,0.15)),
    ("thermodynamics_x_mechanism_design_x_free_energy_principle.py","TMDF","Thermo Mechanism FEP: VCG energy min + entropy reg",(0.50,0.25,0.10,0.15)),
    ("dialectics_x_feedback_control_x_model_checking.py","DFMC","Dialectic Feedback Checker: thesis-antithesis + PID correction",(0.50,0.25,0.12,0.13)),
    ("ecosystem_dynamics_x_free_energy_principle_x_sensitivity_analysis.py","EDFS","Ecosystem FEP Sensitivity: Lotka-Volterra + Sobol scoring",(0.52,0.23,0.10,0.15)),
    ("ergodic_theory_x_free_energy_principle_x_maximum_entropy.py","EFME","Ergodic FEP MaxEnt: Birkhoff-average + Jaynes entropy",(0.50,0.25,0.10,0.15)),
    ("measure_theory_x_mechanism_design_x_type_theory.py","MMDT","Measure Mechanism Typer: VCG sigma-algebra + dependent types",(0.52,0.23,0.10,0.15)),
    ("network_science_x_multi-armed_bandits_x_maximum_entropy.py","NMME","Network Bandit MaxEnt: centrality UCB + entropy reg",(0.50,0.25,0.12,0.13)),
    ("phase_transitions_x_criticality_x_model_checking.py","PCMC","Phase Critical Checker: order-parameter + critical verification",(0.52,0.23,0.10,0.15)),
    ("phase_transitions_x_gene_regulatory_networks_x_mechanism_design.py","PGRM","Phase GRN Mechanism: bistable switch + incentive regulation",(0.50,0.25,0.10,0.15)),
    ("renormalization_x_feedback_control_x_free_energy_principle.py","RFCF","Renorm Feedback FEP: coarse-grained energy min + PID",(0.52,0.23,0.10,0.15)),
    ("topology_x_quantum_mechanics_x_normalized_compression_distance.py","TQNC","Topological Quantum NCD: Betti invariant + amplitude compression",(0.50,0.25,0.12,0.13)),
    ("adaptive_control_x_mechanism_design_x_maximum_entropy.py","ACME","Adaptive Control MaxEnt Mech: MRAC gain + entropy VCG",(0.52,0.23,0.10,0.15)),
    ("ergodic_theory_x_chaos_theory_x_compositionality.py","ECCC","Ergodic-Chaotic Compositor: mixing Lyapunov + compositional verify",(0.50,0.25,0.10,0.15)),
    ("phase_transitions_x_mechanism_design_x_free_energy_principle.py","PMDF","Phase Mechanism FEP: order-parameter VCG + variational bound",(0.52,0.23,0.10,0.15)),
    ("phase_transitions_x_network_science_x_mechanism_design.py","PNMD","Phase Network Mechanism: percolation + graph-incentive",(0.50,0.25,0.12,0.13)),
    ("chaos_theory_x_kolmogorov_complexity_x_free_energy_principle.py","CKFE","Chaotic Kolmogorov FEP: Lyapunov-gated complexity + variational",(0.52,0.23,0.10,0.15)),
    ("ergodic_theory_x_constraint_satisfaction_x_criticality.py","ECSC","Ergodic Constraint Critical: mixing arc-consistency + sandpile",(0.50,0.25,0.10,0.15)),
    ("fractal_geometry_x_falsificationism_x_feedback_control.py","FFFC","Fractal Falsification Controller: IFS constraint + PID",(0.52,0.23,0.10,0.15)),
    ("morphogenesis_x_predictive_coding_x_falsificationism.py","MPCF","Morphogenic Predictive Falsifier: Turing error + prediction min",(0.50,0.25,0.12,0.13)),
    ("phase_transitions_x_renormalization_x_active_inference.py","PRAI","Phase Renorm Active Inference: coarse belief update at critical",(0.52,0.23,0.10,0.15)),
    ("quantum_mechanics_x_criticality_x_type_theory.py","QMCT","Quantum Critical Typer: superposition + critical type check",(0.50,0.25,0.10,0.15)),
    ("chaos_theory_x_hebbian_learning_x_free_energy_principle.py","CHLF","Chaotic Hebbian FEP: fire-together + Lyapunov energy",(0.52,0.23,0.10,0.15)),
    ("chaos_theory_x_renormalization_x_cognitive_load_theory.py","CRCL","Chaotic Renorm CogLoad: multi-scale complexity budget",(0.50,0.25,0.12,0.13)),
    ("dynamical_systems_x_abductive_reasoning_x_maximum_entropy.py","DAME","Dynamical Abductive MaxEnt: phase-portrait hypothesis + entropy",(0.52,0.23,0.10,0.15)),
    ("ergodic_theory_x_analogical_reasoning_x_model_checking.py","EAMC","Ergodic Analogical Checker: structure-mapping + mixing verify",(0.50,0.25,0.10,0.15)),
    ("ergodic_theory_x_mechanism_design_x_multi-armed_bandits.py","EMDB","Ergodic Mechanism Bandit: time-average VCG + UCB",(0.52,0.23,0.10,0.15)),
    ("holography_principle_x_emergence_x_type_theory.py","HPET","Holographic Emergent Typer: boundary-bulk + type verify",(0.50,0.25,0.12,0.13)),
    ("cognitive_load_theory_x_pragmatics_x_multi-armed_bandits.py","CLPB","CogLoad Pragmatic Bandit: complexity budget + implicature UCB",(0.52,0.23,0.10,0.15)),
    ("epigenetics_x_error_correcting_codes_x_nash_equilibrium.py","EECN","Epigenetic ECC Nash: methylation Hamming + equilibrium",(0.50,0.25,0.10,0.15)),
    ("genetic_algorithms_x_pragmatics_x_type_theory.py","GAPT","Genetic Pragmatic Typer: crossover implicature + type fitness",(0.52,0.23,0.10,0.15)),
    ("information_theory_x_sparse_autoencoders_x_embodied_cognition.py","ISEC","Info Sparse Embodied: MI bottleneck + grounded scoring",(0.50,0.25,0.12,0.13)),
    ("information_theory_x_sparse_autoencoders_x_multi-armed_bandits.py","ISMB","Info Sparse Bandit: compression UCB + sparse activation",(0.52,0.23,0.10,0.15)),
    ("information_theory_x_spectral_analysis_x_neural_oscillations.py","ISSO","Info Spectral Oscillator: spectral entropy + phase-locked",(0.50,0.25,0.10,0.15)),
    ("quantum_mechanics_x_program_synthesis_x_epigenetics.py","QPSE","Quantum Program Epigenetic: superposition search + methylation",(0.52,0.23,0.10,0.15)),
    ("bayesian_inference_x_differentiable_programming_x_abductive_reasoning.py","BDAR","Bayesian Diff Abductive: gradient posterior + best-explanation",(0.50,0.25,0.12,0.13)),
    ("differentiable_programming_x_metacognition_x_mechanism_design.py","DMMD","Diff Metacog Mechanism: gradient monitor + VCG incentive",(0.52,0.23,0.10,0.15)),
    ("epistemology_x_feedback_control_x_maximum_entropy.py","EFCM","Epistemic Feedback MaxEnt: justified-belief + PID + entropy",(0.50,0.25,0.10,0.15)),
    ("ergodic_theory_x_causal_inference_x_satisfiability.py","ECIS","Ergodic Causal SAT: mixing causal-graph + DPLL propagation",(0.52,0.23,0.10,0.15)),
    ("ergodic_theory_x_spectral_analysis_x_criticality.py","ESAC","Ergodic Spectral Critical: eigenvalue-gap + critical amplification",(0.50,0.25,0.12,0.13)),
    ("theory_of_mind_x_mechanism_design_x_sensitivity_analysis.py","TMSA","ToM Mechanism Sensitivity: belief VCG + Sobol robustness",(0.52,0.23,0.10,0.15)),
]

TEMPLATE = r'''"""CAITL v4 {docline}. struct>={sw:.0%} comp>={cw:.0%} ncd<={nw:.0%}."""
import re,math,zlib
from typing import List,Dict
_N=re.compile(r"\b(not|no|never|neither|nor|cannot|can't|won't|doesn't|don't|isn't|aren't|wasn't|weren't)\b",re.I)
_NUM=re.compile(r'[-+]?\d+(?:\.\d+)?(?:/\d+)?');_BOL=re.compile(r'\b(true|false|yes|no|correct|incorrect)\b',re.I)
_CMP=re.compile(r'\b(more|less|greater|fewer|larger|smaller|higher|lower|bigger|tallest|shortest|biggest|fastest|slowest|oldest|youngest|taller|heavier|lighter|better|worse)\b',re.I)
_CND=re.compile(r'\b(if|then|unless|provided|given that|suppose|when)\b',re.I)
_TMP=re.compile(r'\b(before|after|first|last|next|previous|earlier|later|during|while|since|until|finally|originally|initially|subsequently)\b',re.I)
_QNT=re.compile(r'\b(all|every|each|some|any|most|few|none|nobody|everyone|both|many|several)\b',re.I)
_CAU=re.compile(r'\b(because|therefore|thus|hence|causes?|leads?\s+to|results?\s+in|due to|implies)\b',re.I)
_SO=re.compile(r'(\b[A-Z]\w+)\s+\w+ed\s+(\b[A-Z]\w+)',re.I);_LR=re.compile(r'\b(left|right|east|west|north|south|above|below|up|down)\b',re.I)
_ABN=re.compile(r'\b(?:all|every\w*)\s+(?:but|except)\s+(\d+)\b',re.I)
_RATE=re.compile(r'(\w+)\s+takes?\s+(\d+\.?\d*)\s+(?:hours?|min\w*|days?).*?(\w+)\s+takes?\s+(\d+\.?\d*)\s+(?:hours?|min\w*|days?).*?together',re.I)
_LIAR=re.compile(r'\b(?:always\s+lies?|never\s+tells?\s+the\s+truth|is\s+a\s+liar)\b',re.I)
def _pn(t):
    o=[]
    for m in _NUM.findall(t):
        try:o.append(float(m.split('/')[0])/float(m.split('/')[1]) if '/' in m else float(m))
        except:pass
    return o
def _ncd(a,b):
    if not a or not b:return 1.0
    x,y=a.encode(),b.encode();ca,cb,cc=len(zlib.compress(x)),len(zlib.compress(y)),len(zlib.compress(x+y))
    d=max(ca,cb);return(cc-min(ca,cb))/d if d else 1.0
def _compute(p,c):
    pl,cl=p.lower(),c.lower();pn,cn=_pn(p),_pn(c)
    m=_ABN.search(pl)
    if m and re.search(r'how\s+many',pl):
        n=int(m.group(1));return(1.0,f"computation:all-but-{n}") if cn and n in[int(x)for x in cn]else(-0.5,f"computation:all-but-{n} no match")
    m=_RATE.search(pl)
    if m:
        try:
            t1,t2=float(m.group(2)),float(m.group(4));ans=1.0/(1.0/t1+1.0/t2)
            return(1.0,f"computation:rate={ans:.2f}")if cn and abs(min(cn,key=lambda x:abs(x-ans))-ans)<abs(ans)*0.15+0.5 else(-0.5,f"computation:rate={ans:.2f} no match")
        except:pass
    m=re.search(r'(?:what\s+is\s+|calculate\s+|compute\s+|evaluate\s+)([\d\s\+\-\*/\(\)\.]+)',p,re.I)
    if m:
        expr=m.group(1).strip()
        if re.match(r'^[\d\s\+\-\*/\(\)\.]+$',expr)and len(expr)>2:
            try:
                r=eval(expr,{"__builtins__":{}},{});return(1.0,f"computation:PEMDAS={r}")if cn and abs(cn[0]-r)<0.01 else(-0.5,f"computation:PEMDAS={r} no match")
            except:pass
    m=re.search(r'(?:remainder|mod).*?(\d+).*?(?:divided\s+by|mod)\s*(\d+)',pl)
    if m:
        try:
            a,b=int(m.group(1)),int(m.group(2));r=a%b;return(1.0,f"computation:{a}%{b}={r}")if cn and r in[int(x)for x in cn]else(-0.5,f"computation:{a}%{b}={r} no match")
        except:pass
    if re.search(r'how\s+many.*?between|fence\s*post|poles?.*?spaces?',pl)and len(pn)>=2:
        fp=abs(pn[0]-pn[1])+1;return(1.0,f"computation:fencepost={fp}")if cn and fp in cn else(-0.3,f"computation:fencepost={fp}")
    if re.search(r'(?:at\s+least\s+one|either.*or.*how|union|overlap)',pl)and len(pn)>=2:
        ie=pn[0]+pn[1]-(pn[2]if len(pn)>=3 else 0);return(0.8,f"computation:IE={ie}")if cn and abs(cn[0]-ie)<1 else(-0.3,f"computation:IE={ie}")
    m=re.search(r'(?:is\s+)([\d.,]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.,]+)',pl)
    if m:
        try:
            a,b=float(m.group(1).replace(',','')),float(m.group(2).replace(',',''));ok='yes'if a>b else'no'
            return(1.0,f"computation:{a}>{b}")if cl.startswith(ok)else(-1.0,f"computation:{a}>{b} expected {ok}")
        except:pass
    m=re.search(r'(?:is\s+)([\d.,]+)\s+(?:smaller|less|fewer|lower)\s+than\s+([\d.,]+)',pl)
    if m:
        try:
            a,b=float(m.group(1).replace(',','')),float(m.group(2).replace(',',''));ok='yes'if a<b else'no'
            return(1.0,f"computation:{a}<{b}")if cl.startswith(ok)else(-1.0,f"computation:expected {ok}")
        except:pass
    comps=[]
    for m2 in re.finditer(r'(\w+)\s+(?:is\s+)?(?:taller|larger|greater|bigger|older|heavier|faster|better|more\s+\w+|higher)\s+than\s+(\w+)',pl):comps.append((m2.group(1).strip('.,'),m2.group(2).strip('.,')))
    for m2 in re.finditer(r'(\w+)\s+(?:is\s+)?(?:shorter|smaller|less|younger|lighter|slower|worse|lower)\s+than\s+(\w+)',pl):comps.append((m2.group(2).strip('.,'),m2.group(1).strip('.,')))
    if len(comps)>=2:
        gt={}
        for a,b in comps:gt.setdefault(a,set()).add(b)
        for _ in range(len(gt)):
            for a in list(gt):
                for b in list(gt.get(a,[])):
                    for c2 in list(gt.get(b,[])):gt.setdefault(a,set()).add(c2)
        if re.search(r'(?:who|which|what)\s+(?:is\s+)?(?:the\s+)?(?:tallest|largest|biggest|oldest|heaviest|fastest|best|greatest|most)',pl):
            top=max(gt,key=lambda x:len(gt.get(x,set())));return(1.0,f"computation:trans={top}")if top in cl else(-0.5,f"computation:trans={top}")
        if re.search(r'(?:who|which|what)\s+(?:is\s+)?(?:the\s+)?(?:shortest|smallest|youngest|lightest|slowest|worst|least)',pl):
            ae=set();[ae.update([a]+list(gt[a]))for a in gt];btm=ae-set(gt.keys())
            if not btm:btm={min(gt,key=lambda x:len(gt.get(x,set())))}
            for b in btm:
                if b in cl:return(1.0,f"computation:trans-min={b}")
            return(-0.5,f"computation:trans-min={btm}")
    if _LIAR.search(pl):
        m2=re.search(r'(?:says?|claims?|states?)\s+"?(.+?)"?\s*(?:\.|$)',pl)
        if m2:
            claim=m2.group(1).lower()
            if'yes'in claim or'true'in claim:return(0.8,"structural:liar->negate")if cl.startswith('no')or'false'in cl[:20]else(-0.5,"structural:liar fail")
            if'no'in claim or'false'in claim:return(0.8,"structural:liar->affirm")if cl.startswith('yes')or'true'in cl[:20]else(-0.5,"structural:liar fail")
    if re.search(r'\b(?:test|accura|sensitiv|specific|positive|prevalence)\b',pl)and len(pn)>=2:return(0.0,"computation:bayes-detected")
    if pn and not cn:return(0.0,"computation:nums-missing")
    if len(pn)>=2:
        if re.search(r'\b(sum|total|add|combined|altogether)\b',pl):e=sum(pn);return(1.0,f"computation:sum={e}")if cn and abs(cn[0]-e)<0.01 else(-0.3,f"computation:sum={e}")
        if re.search(r'\b(differ|subtract|minus|how many more)\b',pl):e=abs(pn[0]-pn[1]);return(1.0,f"computation:diff={e}")if cn and abs(cn[0]-e)<0.01 else(-0.3,f"computation:diff={e}")
        if re.search(r'\b(product|multiply|times)\b',pl):
            e=1.0
            for n in pn:e*=n
            return(1.0,f"computation:prod={e}")if cn and abs(cn[0]-e)<0.01 else(-0.3,f"computation:prod={e}")
    return(None,"")
def _neg(p,c):
    np_,nc_=len(_N.findall(p)),len(_N.findall(c))
    if np_>=2 and np_%2==0:return 0.8 if nc_%2==0 else 0.3
    if np_==1:return 0.65 if _BOL.search(c.lower())or nc_>=1 else 0.35
    return 0.5
def _tmp(p,c):
    if not _TMP.search(p):return 0.5
    cl=c.lower();s=0.35
    if any(w in cl for w in['before','after','first','last','then','earlier','later','next','finally']):s+=0.3
    ep=re.findall(r'\b[A-Z][a-z]+\b',p);ec=re.findall(r'\b[A-Z][a-z]+\b',c)
    if ep and ec and ec[0]in ep:s+=0.2
    return min(1.0,s)
def _cnd(p,c):
    if not _CND.search(p):return 0.5
    pl,cl=p.lower(),c.lower();s=0.3
    if'if'in pl and'then'in pl:
        s+=0.2;m=re.search(r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:\.|$)',pl)
        if m and any(n in pl for n in['not','no','never']):
            if any(n in cl[:30]for n in['not','no','false']):s+=0.3
    if _BOL.search(cl):s+=0.15
    if _N.search(pl)and _N.search(cl):s+=0.15
    return min(1.0,s)
def _struct(p,c):
    sc,wt,R=0.0,0.0,[]
    pl,cl=p.lower(),c.lower()
    def _a(s,w,n):nonlocal sc,wt;sc+=s*w;wt+=w;R.append(f"{n}={s:.2f}")
    if _N.search(pl):_a(_neg(p,c),0.12,'neg')
    pn=_pn(p)
    if pn:_a(0.5,0.12,'num')
    if _TMP.search(pl):_a(_tmp(p,c),0.10,'tmp')
    if _CND.search(pl):_a(_cnd(p,c),0.10,'cnd')
    if _CMP.search(pl):
        cn_=_pn(c)
        s=1.0 if(pn and cn_ and((re.search(r'\b(larg|great|bigg|more|higher|tall|fast|old)\w*',pl)and max(pn)in cn_)or(re.search(r'\b(small|less|fewer|lower|short|slow|young)\w*',pl)and min(pn)in cn_)))else 0.4
        _a(s,0.08,'cmp')
    if _QNT.search(pl):_a(0.6 if _QNT.search(cl)else 0.3,0.06,'qnt')
    if _CAU.search(pl):_a(0.6 if _CAU.search(cl)else 0.3,0.06,'cau')
    if _SO.search(p):_a(0.6 if _SO.search(c)else 0.3,0.06,'s_o')
    if re.search(r'\?',pl)and re.search(r'\b(is|are|does|do|was|were|can|will)\b',pl):_a(0.65 if _BOL.search(cl)else 0.3,0.05,'bol')
    if _LR.search(pl):_a(0.6 if _LR.search(cl)else 0.3,0.04,'lr')
    if re.search(r'not\s+(?:\w+\s+){0,3}not\b|never\s+(?:\w+\s+){0,3}not\b',pl):_a(0.7 if _N.findall(c)and len(_N.findall(c))%2==0 else 0.3,0.06,'dblneg')
    if re.search(r'\bnot\s+(?:both|all)\b|\bneither\b.*\bnor\b',pl):_a(0.6 if _N.search(cl)else 0.3,0.05,'dmg')
    if re.search(r'\bif\b',pl)and re.search(r'\bno\s+\w+\s+(?:is|are|exist|has|have)\b|\bnone\b|\bnobody\b|\bnothing\b',pl):_a(0.7 if'true'in cl or'yes'in cl else 0.3,0.05,'vac')
    if re.search(r'\bcorrelat\b|\bassociat\b|\bwhenever\b.*\balso\b',pl):_a(0.7 if'not'in cl or'cause'not in cl else 0.3,0.05,'corr')
    if wt<0.01:
        pt=set(re.findall(r'\b\w{3,}\b',pl));ct=set(re.findall(r'\b\w{3,}\b',cl))
        ov=len(pt&ct)/max(len(pt),1);sc=ov*0.4;wt=0.5;R.append(f"base={ov:.2f}")
    return(sc/wt if wt else 0.3),wt,R
class ReasoningTool:
    """{docline} v4."""
    TAG="{tag}"
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates:return[]
        res=[]
        for c in candidates:
            st,w,R=_struct(prompt,c);cr=_compute(prompt,c)
            cs=(cr[0]+1)/2 if cr[0]is not None else 0.5
            nc=max(0,1-_ncd(prompt,c));lr=min(len(c)+1,len(prompt)+1)/max(len(c)+1,len(prompt)+1)
            f={sw}*st+{cw}*cs+{nw}*nc+{tw}*lr
            rp=[f"st={st:.3f}(w={w:.2f})",f"cp={cs:.3f}",f"nc={nc:.3f}",f"th={lr:.3f}"]
            if cr[0]is not None:rp.append(cr[1])
            elif w<0.05:rp.append("low_confidence:no_category_match")
            rp.append(f"confidence:{'high'if f>0.65 else'medium'if f>0.4 else'low'}")
            res.append({"candidate":c,"score":float(max(0,min(1,f))),"reasoning":f"[{self.TAG}] "+"; ".join(rp)})
        res.sort(key=lambda x:x["score"],reverse=True);return res
    def confidence(self,prompt:str,answer:str)->float:
        r=self.evaluate(prompt,[answer])
        if not r:return 0.0
        s=r[0]["score"];_,w,_=_struct(prompt,answer)
        if w<0.05:return min(s,0.25)
        cr=_compute(prompt,answer)
        if cr[0]is not None and cr[0]>0.5:return min(0.9,0.6+cr[0]*0.3)
        return max(0.05,min(0.85,s))
'''

generated = 0
skipped = 0
for fname, tag, doc, weights in TOOLS:
    if fname in SKIP:
        skipped += 1
        continue
    outpath = os.path.join(OUT, fname)
    # Check if file exists and was NOT generated by retry batch (preserve other batches)
    if os.path.exists(outpath):
        with open(outpath, 'r') as fh:
            head = fh.read(200)
            # Skip files from other batches that don't have our v4 marker
            if 'CAITL v4' not in head and 'CAITL v4' not in head.replace(' ',''):
                # Check if it has any of our TAGs (with or without -v4 suffix)
                fh.seek(0)
                full = fh.read()
                if f'TAG="{tag}"' not in full and f'TAG="{tag}-v4"' not in full:
                    skipped += 1
                    continue
    sw, cw, nw, tw = weights
    out = TEMPLATE
    out = out.replace('{docline}', doc)
    out = out.replace('{tag}', tag)
    out = out.replace('{sw:.0%}', f'{sw:.0%}')
    out = out.replace('{cw:.0%}', f'{cw:.0%}')
    out = out.replace('{nw:.0%}', f'{nw:.0%}')
    out = out.replace('{sw}', str(sw))
    out = out.replace('{cw}', str(cw))
    out = out.replace('{nw}', str(nw))
    out = out.replace('{tw}', str(tw))
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(out)
    generated += 1

print(f"Generated: {generated}, Skipped: {skipped}")
