"""
Aporia — Expand catalog from recently crawled paper sources.

Adds:
  1. Physics: ~148 questions from arXiv:2510.06348 (particle physics frontiers)
  2. Mathematics: 14 questions from Randomstrasse101 (2024+2025 papers)
"""

import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load_jsonl(path):
    qs = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    qs.append(json.loads(line))
    return qs

def write_jsonl(path, qs):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for q in qs:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

def normalize(t):
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t)

def next_id(existing, code):
    max_num = 0
    for q in existing:
        m = re.match(rf"{code}-(\d+)", q["id"])
        if m:
            max_num = max(max_num, int(m.group(1)))
    return max_num

def q(qid, domain, subdomain, title, statement, **kw):
    return {
        "id": qid, "title": title, "domain": domain,
        "subdomain": subdomain, "statement": statement,
        "status": kw.get("status", "open"),
        "importance": kw.get("importance", ""),
        "year_posed": kw.get("year_posed", None),
        "posed_by": kw.get("posed_by", ""),
        "sources": kw.get("sources", []),
        "tags": kw.get("tags", []),
        "related_ids": [], "papers": [], "notes": kw.get("notes", ""),
    }


# ---------------------------------------------------------------------------
# Physics: arXiv:2510.06348 — particle physics frontiers
# ---------------------------------------------------------------------------

def physics_questions():
    S = "https://arxiv.org/abs/2510.06348"
    T = ["particle_physics_frontiers"]
    qs = []

    def p(sub, title, stmt):
        qs.append(("physics", sub, title, stmt, S, T))

    # --- fundamental_symmetries ---
    p("fundamental_symmetries", "Lorentz invariance exactness", "Is Lorentz invariance an exact symmetry at all energy scales or does it break at the Planck scale?")
    p("fundamental_symmetries", "CPT symmetry exactness", "Is CPT symmetry exact, or is it violated at some energy scale?")
    p("fundamental_symmetries", "CP violation beyond CKM", "Is there a source of CP violation beyond the CKM matrix?")
    p("fundamental_symmetries", "Strong CP problem", "Why is the QCD vacuum angle theta so small?")
    p("fundamental_symmetries", "Axion existence", "Does the QCD axion exist as the solution to the strong CP problem?")
    p("fundamental_symmetries", "Fine-structure constant variation", "Does the fine-structure constant vary with cosmological time or position?")
    p("fundamental_symmetries", "Proton-to-electron mass ratio constancy", "Is the proton-to-electron mass ratio constant across cosmological time?")
    p("fundamental_symmetries", "Baryon number conservation", "Is baryon number exactly conserved or violated at some scale?")
    p("fundamental_symmetries", "Lepton number conservation", "Is total lepton number exactly conserved?")
    p("fundamental_symmetries", "Discrete symmetry origin", "What is the origin of C, P, and T as discrete symmetries in the Standard Model?")
    p("fundamental_symmetries", "Matter-antimatter gravitational symmetry", "Do matter and antimatter experience identical gravitational interactions?")
    p("fundamental_symmetries", "Equivalence principle universality", "Does the weak equivalence principle hold for all forms of matter and energy?")
    p("fundamental_symmetries", "Parity violation origin", "Why does the weak force maximally violate parity?")
    p("fundamental_symmetries", "Charge quantization origin", "Why is electric charge quantized in integer multiples of e/3?")
    p("fundamental_symmetries", "Time reversal violation direct", "Can direct T-violation be measured independently of CP violation and CPT?")

    # --- higgs_physics ---
    p("higgs_physics", "Higgs boson uniqueness", "Is the 125 GeV Higgs boson the only scalar in the electroweak sector?")
    p("higgs_physics", "Higgs self-coupling measurement", "What is the exact value of the Higgs trilinear self-coupling?")
    p("higgs_physics", "Higgs quartic self-coupling", "Can the Higgs quartic self-coupling be measured directly?")
    p("higgs_physics", "Higgs compositeness", "Is the Higgs boson elementary or a composite bound state?")
    p("higgs_physics", "Electroweak vacuum stability", "Is the electroweak vacuum absolutely stable, metastable, or unstable?")
    p("higgs_physics", "Electroweak phase transition order", "Is the electroweak phase transition first-order or a crossover?")
    p("higgs_physics", "Higgs mass naturalness", "Why is the Higgs mass so much lighter than the Planck scale?")
    p("higgs_physics", "Higgs coupling universality", "Do Higgs couplings to fermions and bosons follow the Standard Model pattern exactly?")
    p("higgs_physics", "Higgs invisible decays", "Does the Higgs boson have invisible decay channels beyond the Standard Model?")
    p("higgs_physics", "Higgs CP properties", "Is the Higgs boson a pure CP-even state or does it have CP-odd admixture?")
    p("higgs_physics", "Higgs portal to dark sector", "Does the Higgs boson serve as a portal to a hidden dark sector?")
    p("higgs_physics", "Extended Higgs sector", "Does nature realize a two-Higgs-doublet model or larger scalar sector?")
    p("higgs_physics", "Higgs width direct measurement", "Can the Higgs total width be measured directly with precision?")
    p("higgs_physics", "Electroweak symmetry breaking dynamics", "Is electroweak symmetry breaking driven solely by the Higgs mechanism?")
    p("higgs_physics", "Higgs-inflaton connection", "Is the Higgs field the inflaton or connected to the inflaton?")
    p("higgs_physics", "Higgs vacuum alignment", "What determines the vacuum alignment in extended Higgs models?")

    # --- beyond_standard_model ---
    p("beyond_standard_model", "Extra spatial dimensions", "Do extra spatial dimensions exist beyond the three we observe?")
    p("beyond_standard_model", "Large extra dimensions (ADD)", "Are there large extra dimensions at the sub-millimeter scale?")
    p("beyond_standard_model", "Warped extra dimensions (RS)", "Does a warped fifth dimension explain the hierarchy between the Planck and electroweak scales?")
    p("beyond_standard_model", "New long-range forces", "Are there new macroscopic forces beyond gravity and electromagnetism?")
    p("beyond_standard_model", "Quark-lepton compositeness", "Are quarks and leptons composed of more fundamental preons?")
    p("beyond_standard_model", "Technicolor or composite Higgs", "Is electroweak symmetry breaking driven by a new strong interaction?")
    p("beyond_standard_model", "Supersymmetry in nature", "Is supersymmetry realized in nature at any energy scale?")
    p("beyond_standard_model", "Superpartner mass scale", "If SUSY exists, what is the mass scale of the lightest superpartners?")
    p("beyond_standard_model", "Z-prime boson existence", "Does a Z' gauge boson from an extended gauge group exist?")
    p("beyond_standard_model", "W-prime boson existence", "Does a W' charged gauge boson exist beyond the Standard Model W?")
    p("beyond_standard_model", "Leptoquark existence", "Do leptoquarks exist as predicted by grand unified theories?")
    p("beyond_standard_model", "Magnetic monopole existence", "Do magnetic monopoles exist as predicted by grand unified theories?")
    p("beyond_standard_model", "Fourth generation fermions", "Does a sequential fourth generation of quarks and leptons exist?")
    p("beyond_standard_model", "Heavy neutral leptons", "Do heavy neutral leptons beyond the three known neutrinos exist?")
    p("beyond_standard_model", "Long-lived particle searches", "Are there long-lived particles with macroscopic decay lengths at colliders?")
    p("beyond_standard_model", "Dark photon existence", "Does a dark photon kinetically mixed with the SM photon exist?")
    p("beyond_standard_model", "Hidden valley sector", "Is there a hidden valley sector with light confined states?")
    p("beyond_standard_model", "String theory low-energy signatures", "Can string theory produce testable signatures at accessible energies?")
    p("beyond_standard_model", "Proton radius puzzle resolution", "What is the true proton charge radius and what explains the muonic measurement discrepancy?")

    # --- dark_matter ---
    p("dark_matter", "Dark matter particle identity", "What is the particle identity of dark matter?")
    p("dark_matter", "WIMP existence", "Are weakly interacting massive particles the dark matter?")
    p("dark_matter", "Axion dark matter", "Is the dark matter composed primarily of axions or axion-like particles?")
    p("dark_matter", "Sterile neutrino dark matter", "Are keV-scale sterile neutrinos the dark matter?")
    p("dark_matter", "Dark matter self-interaction", "Does dark matter have significant self-interactions?")
    p("dark_matter", "Dark matter species diversity", "Is dark matter a single species or a multi-component dark sector?")
    p("dark_matter", "Dark matter laboratory detection", "Can dark matter be detected directly in terrestrial laboratory experiments?")
    p("dark_matter", "Dark matter collider production", "Can dark matter particles be produced and identified at colliders?")
    p("dark_matter", "Dark matter indirect detection", "Can dark matter annihilation or decay products be unambiguously identified in cosmic rays?")
    p("dark_matter", "Dark matter substructure", "What is the small-scale substructure of the dark matter halo?")
    p("dark_matter", "Primordial black hole dark matter", "Are primordial black holes a significant component of dark matter?")
    p("dark_matter", "Fuzzy dark matter", "Is the dark matter composed of ultralight bosons with de Broglie wavelengths on galactic scales?")
    p("dark_matter", "Dark matter-baryon interaction", "Does dark matter interact with baryons through any force besides gravity?")
    p("dark_matter", "MOND vs dark matter", "Can modified gravity fully replace dark matter in explaining all observations?")
    p("dark_matter", "Dark matter cosmic evolution", "Has the dark matter abundance or properties evolved with cosmic time?")

    # --- neutrino_physics ---
    p("neutrino_physics", "Neutrino mass hierarchy", "Is the neutrino mass ordering normal or inverted?")
    p("neutrino_physics", "Neutrino absolute mass scale", "What is the absolute mass scale of the lightest neutrino?")
    p("neutrino_physics", "Neutrino Majorana nature", "Are neutrinos Majorana or Dirac fermions?")
    p("neutrino_physics", "Neutrinoless double beta decay", "Does neutrinoless double beta decay occur in nature?")
    p("neutrino_physics", "Neutrino CP violation", "Is there CP violation in the lepton sector, and what is the value of delta_CP?")
    p("neutrino_physics", "Sterile neutrino existence", "Do light sterile neutrinos exist?")
    p("neutrino_physics", "Neutrino mass mechanism", "What is the mechanism that generates neutrino masses?")
    p("neutrino_physics", "Seesaw mechanism scale", "If the seesaw mechanism operates, what is the scale of the heavy right-handed neutrinos?")
    p("neutrino_physics", "Leptogenesis viability", "Can leptogenesis via heavy neutrino decays explain the baryon asymmetry?")
    p("neutrino_physics", "Cosmic neutrino background detection", "Can the relic neutrino background from the Big Bang be directly detected?")
    p("neutrino_physics", "Neutrino magnetic moment", "Does the neutrino have an anomalously large magnetic moment?")
    p("neutrino_physics", "NSI (non-standard interactions)", "Do neutrinos have non-standard interactions beyond the weak force?")
    p("neutrino_physics", "Reactor neutrino anomaly", "What explains the observed deficit of reactor antineutrinos at short baselines?")
    p("neutrino_physics", "Gallium anomaly", "What causes the deficit of electron neutrinos in gallium source experiments?")
    p("neutrino_physics", "Supernova neutrino burst physics", "What can the next galactic supernova neutrino burst reveal about neutrino properties?")
    p("neutrino_physics", "Neutrino flavor ratio from astrophysical sources", "What is the flavor composition of high-energy astrophysical neutrinos at Earth?")

    # --- qcd ---
    p("qcd", "Color confinement proof", "Can quark confinement be rigorously proven from QCD?")
    p("qcd", "Glueball observation", "Can glueballs be unambiguously identified experimentally?")
    p("qcd", "Pomeron nature", "What is the QCD nature of the Pomeron?")
    p("qcd", "QCD phase diagram mapping", "What is the detailed phase structure of QCD at finite temperature and baryon density?")
    p("qcd", "QCD critical point existence", "Does the QCD critical point exist in the temperature-density plane?")
    p("qcd", "Quark-gluon plasma properties", "What are the precise transport properties of the quark-gluon plasma?")
    p("qcd", "Nucleon spin decomposition", "How is the proton spin distributed among quarks, gluons, and orbital angular momentum?")
    p("qcd", "Exotic hadron classification", "What is the internal structure of XYZ states: tetraquarks, molecules, or hybrids?")
    p("qcd", "Pentaquark structure", "What is the internal dynamics of pentaquark states observed at LHCb?")
    p("qcd", "Gluon saturation (Color Glass Condensate)", "Does gluon saturation occur at small-x and can the Color Glass Condensate be confirmed?")
    p("qcd", "Proton structure at high x", "What is the precise parton distribution in the proton at large momentum fraction?")
    p("qcd", "EMC effect origin", "What causes the modification of parton distributions inside nuclei?")
    p("qcd", "Odderon observation confirmation", "Is the odderon observation at the LHC confirmed with independent measurements?")
    p("qcd", "QCD vacuum structure", "What is the structure of the QCD vacuum including instantons and topological effects?")

    # --- grand_unification ---
    p("grand_unification", "Grand unification realization", "Is grand unification of the strong and electroweak forces realized in nature?")
    p("grand_unification", "Coupling constant unification", "Do the three gauge coupling constants unify at a single energy scale?")
    p("grand_unification", "Proton decay observation", "Can proton decay be observed, and what is its lifetime?")
    p("grand_unification", "GUT gauge group", "What is the correct grand unified gauge group: SU(5), SO(10), E6, or another?")
    p("grand_unification", "Gravity weakness explanation", "Why is gravity so much weaker than the other fundamental forces?")
    p("grand_unification", "Gauge hierarchy problem", "What stabilizes the enormous hierarchy between the electroweak and Planck scales?")
    p("grand_unification", "Fermion mass hierarchy", "What explains the vast hierarchy of fermion masses spanning six orders of magnitude?")
    p("grand_unification", "Yukawa coupling pattern", "Is there a principle that determines the pattern of Yukawa couplings?")
    p("grand_unification", "Gauge coupling origin", "Why are there exactly three gauge groups with the specific coupling strengths observed?")

    # --- cosmology ---
    p("cosmology", "Baryon asymmetry mechanism", "What mechanism produced the matter-antimatter asymmetry in the universe?")
    p("cosmology", "Dark energy nature", "What is the physical nature of dark energy?")
    p("cosmology", "Dark energy evolution", "Does the dark energy equation of state evolve with time or is it a cosmological constant?")
    p("cosmology", "Cosmic inflation mechanism", "What is the specific mechanism that drove cosmic inflation?")
    p("cosmology", "Inflation observable predictions", "Can inflation be confirmed through B-mode polarization or other observables?")
    p("cosmology", "Hubble tension resolution", "What resolves the discrepancy between local and CMB-based measurements of H0?")
    p("cosmology", "S8 tension resolution", "What explains the tension between CMB and large-scale structure measurements of S8?")
    p("cosmology", "CMB blackbody precision", "Are there spectral distortions in the CMB blackbody spectrum from early-universe processes?")
    p("cosmology", "Cosmological lithium problem", "Why does primordial lithium-7 abundance disagree with Big Bang nucleosynthesis predictions?")
    p("cosmology", "Dark energy particle physics connection", "Can dark energy be understood from particle physics principles?")
    p("cosmology", "Cosmic coincidence problem", "Why are the dark matter and dark energy densities comparable at the present epoch?")
    p("cosmology", "Vacuum energy catastrophe", "Why is the observed vacuum energy 120 orders of magnitude smaller than quantum field theory predicts?")
    p("cosmology", "Phase transitions in early universe", "What phase transitions occurred in the early universe and what relics did they produce?")
    p("cosmology", "Gravitational wave background spectrum", "What is the stochastic gravitational wave background from cosmological sources?")

    # --- flavor_physics ---
    p("flavor_physics", "CKM unitarity precision", "Does the CKM matrix satisfy unitarity exactly at high precision?")
    p("flavor_physics", "Cabibbo angle anomaly", "Is the first-row CKM unitarity deficit (Cabibbo angle anomaly) a sign of new physics?")
    p("flavor_physics", "Charged lepton flavor violation", "Do charged lepton flavor violating decays (mu -> e gamma) occur?")
    p("flavor_physics", "Generation count origin", "Why are there exactly three generations of quarks and leptons?")
    p("flavor_physics", "Quark-lepton complementarity", "Is the relationship between quark and lepton mixing angles a coincidence or a symmetry?")
    p("flavor_physics", "B anomalies resolution", "Are the anomalies in B-meson decays signs of lepton flavor universality violation?")
    p("flavor_physics", "Muon g-2 new physics", "Is the muon anomalous magnetic moment discrepancy evidence for new physics?")
    p("flavor_physics", "Electron g-2 precision", "Does the electron g-2 measurement reveal new physics at higher precision?")
    p("flavor_physics", "Flavor changing neutral currents beyond SM", "Are there flavor-changing neutral current processes beyond the Standard Model?")
    p("flavor_physics", "CP violation in Bs system", "Is CP violation in the Bs meson system consistent with the Standard Model?")
    p("flavor_physics", "Rare kaon decays (K -> pi nu nubar)", "Do rare kaon decay rates match Standard Model predictions precisely?")
    p("flavor_physics", "Top quark properties precision", "Do precision measurements of top quark properties reveal deviations from the Standard Model?")
    p("flavor_physics", "Flavor symmetry origin", "Is there an underlying flavor symmetry that dictates the fermion mass and mixing pattern?")
    p("flavor_physics", "Electric dipole moments", "Do permanent electric dipole moments of fundamental particles exist?")
    p("flavor_physics", "Mu-to-e conversion in nuclei", "Can coherent muon-to-electron conversion in nuclei be observed?")
    p("flavor_physics", "Tau lepton rare decays", "Do tau leptons exhibit lepton flavor violating or CP violating decays?")

    return qs


# ---------------------------------------------------------------------------
# Mathematics: Randomstrasse101 papers (2024 + 2025)
# ---------------------------------------------------------------------------

def math_questions():
    S24 = "https://arxiv.org/abs/2504.20539"
    S25 = "https://arxiv.org/abs/2603.29571"
    T = ["randomstrasse"]
    qs = []

    def m(sub, title, stmt, source):
        qs.append(("mathematics", sub, title, stmt, source, T))

    # 2024 paper
    m("discrepancy_theory", "Matrix Spencer conjecture",
      "Does Spencer's discrepancy bound O(sqrt(n)) extend to matrix-valued settings with operator norm?", S24)
    m("group_theory", "Group Spencer conjecture",
      "Can Spencer's discrepancy theorem be generalized to non-abelian group settings?", S24)
    m("dynamical_systems", "Globally synchronizing regular graphs",
      "Which regular graphs have the property that all coupled oscillators synchronize for all initial conditions?", S24)
    m("stochastic_geometry", "Ellipsoid fitting sharp transition",
      "Is there a sharp threshold for the number of random points needed to fit an ellipsoid in n dimensions?", S24)
    m("discrepancy_theory", "Komlos conjecture on discrepancy",
      "Does every set of n vectors in R^n with norm at most 1 have a signing with discrepancy O(1)?", S24)
    m("combinatorics", "Hadamard matrix discrepancy",
      "What is the discrepancy of the Hadamard matrix and does it achieve the conjectured lower bound?", S24)
    m("statistical_physics", "SK model sampling threshold",
      "Is there a sharp computational threshold for sampling from the Sherrington-Kirkpatrick spin glass model?", S24)

    # 2025 paper
    m("probability_theory", "Type-2 constant of tensors",
      "What is the type-2 constant of tensor product spaces and does it grow polynomially in dimension?", S25)
    m("graph_theory", "Lovasz number of Erdos-Renyi graphs",
      "What is the typical Lovasz theta number of an Erdos-Renyi random graph G(n,1/2)?", S25)
    m("signal_processing", "Phase retrieval injectivity",
      "What is the minimal number of measurements needed for injective phase retrieval in C^n?", S25)
    m("quantum_information", "Mutually unbiased bases in dimension 6",
      "Do seven mutually unbiased bases exist in dimension 6?", S25)
    m("graph_theory", "Paley graph clique number",
      "What is the asymptotic clique number of the Paley graph on p vertices?", S25)
    m("convex_geometry", "KLS conjecture for log-concave measures",
      "Does the Kannan-Lovasz-Simonovits isoperimetric conjecture hold for all log-concave measures?", S25)
    m("random_matrix_theory", "Sharp graph matrix bounds",
      "Can the norm of random graph matrices be bounded sharply up to 1+epsilon factors?", S25)

    return qs


# ---------------------------------------------------------------------------
# Generic add-to-domain logic
# ---------------------------------------------------------------------------

def add_to_domain(domain, code, new_entries):
    path = ROOT / domain / "questions.jsonl"
    existing = load_jsonl(path)
    titles = {normalize(e["title"]) for e in existing}
    counter = next_id(existing, code)

    added = []
    skipped = 0
    for (dom, sub, title, stmt, source, tags) in new_entries:
        nt = normalize(title)
        if nt in titles:
            skipped += 1
            continue
        counter += 1
        entry = q(f"{code}-{counter:04d}", dom, sub, title, stmt,
                  sources=[source], tags=tags)
        titles.add(nt)
        added.append(entry)

    all_qs = existing + added
    write_jsonl(path, all_qs)

    print(f"\n  [{code}] {domain}")
    print(f"    Existing:            {len(existing)}")
    print(f"    New candidates:      {len(new_entries)}")
    print(f"    Skipped (duplicate): {skipped}")
    print(f"    Added:               {len(added)}")
    print(f"    Total:               {len(all_qs)}")


def main():
    print("Aporia — expand from papers")

    phys = physics_questions()
    add_to_domain("physics", "PHYS", phys)

    math = math_questions()
    add_to_domain("mathematics", "MATH", math)

    print("\nDone.")


if __name__ == "__main__":
    main()
