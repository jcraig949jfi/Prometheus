"""
Aporia — Expand non-math domains with additional sources.

Adds: medicine (new domain), additional physics from Smale/Simon,
additional CS problems, and fills gaps in existing domains.
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


def add_to_domain(domain, code, new_entries):
    path = ROOT / domain / "questions.jsonl"
    existing = load_jsonl(path)
    titles = {normalize(e["title"]) for e in existing}

    max_num = 0
    for e in existing:
        m = re.match(rf"{code}-(\d+)", e["id"])
        if m:
            max_num = max(max_num, int(m.group(1)))

    added = 0
    for sub, title, stmt, kw in new_entries:
        if normalize(title) in titles:
            continue
        max_num += 1
        existing.append(q(f"{code}-{max_num:04d}", domain, sub, title, stmt, **kw))
        titles.add(normalize(title))
        added += 1

    write_jsonl(path, existing)
    print(f"  {domain}: {added} added, {len(existing)} total")


def main():
    WIKI_MED = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_medicine"

    # ── Medicine (new domain) ────────────────────────────────────────
    add_to_domain("medicine", "MED", [
        ("nosology", "Definition of disease", "No overarching definition distinguishes physiological processes from subjective patient suffering.", {"sources": [WIKI_MED]}),
        ("clinical_methodology", "Evidence-based medicine application", "How results from large patient samples apply to individual cases remains debated.", {"sources": [WIKI_MED]}),
        ("psychiatry", "Diagnostic reliability of mental disorders", "Inter-rater reliability varies enormously across psychiatric diagnoses.", {"sources": [WIKI_MED]}),
        ("psychiatry", "Cultural issues in mental disorder definition", "Mental illness definitions remain partially based on societal norms.", {"sources": [WIKI_MED]}),
        ("psychiatry", "Causal classification of mental disorders", "Psychiatric disorders are classified by symptoms rather than etiology.", {"sources": [WIKI_MED]}),
        ("etiology", "Idiopathic diseases", "Numerous diseases lack understood causes or effective treatments.", {"sources": [WIKI_MED]}),
        ("pharmacology", "Mechanism of drug action", "How certain medications work remains unknown, including general anesthesia, paracetamol, and lithium.", {"sources": [WIKI_MED]}),
        ("oncology", "Cancer cure", "No universal cure exists for cancer; mechanisms of metastasis remain incompletely understood.", {"sources": [WIKI_MED]}),
        ("immunology", "Autoimmune disease triggers", "What triggers the immune system to attack the body's own tissues?", {"sources": [WIKI_MED]}),
        ("neurology", "Alzheimer's disease mechanism", "The precise mechanism and primary cause of Alzheimer's neurodegeneration is unknown.", {"sources": [WIKI_MED]}),
        ("infectious_disease", "Antibiotic resistance", "How to sustainably address the growing crisis of antimicrobial resistance?", {"sources": [WIKI_MED]}),
        ("aging", "Aging reversal", "Can biological aging be slowed, halted, or reversed?", {"sources": [WIKI_MED]}),
        ("pain_medicine", "Chronic pain mechanism", "Why does pain persist after tissue healing in chronic pain conditions?", {"sources": [WIKI_MED]}),
    ])

    # ── Physics expansions ───────────────────────────────────────────
    WIKI_PHYS = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_physics"
    add_to_domain("physics", "PHYS", [
        ("particle_physics", "Neutron lifetime puzzle", "Bottle and beam experiments give discrepant neutron lifetime measurements.", {"sources": [WIKI_PHYS]}),
        ("particle_physics", "Proton spin crisis", "How do quarks and gluons carry the proton's spin?", {"sources": [WIKI_PHYS]}),
        ("particle_physics", "Reactor antineutrino anomaly", "Measured antineutrino flux from reactors is 6% below prediction.", {"sources": [WIKI_PHYS]}),
        ("particle_physics", "Pentaquarks and exotic hadrons", "What quark combinations are possible and what is the nature of exotic hadrons?", {"sources": [WIKI_PHYS]}),
        ("particle_physics", "Koide formula", "Why does the charged lepton mass ratio equal 2/3 with such precision?", {"sources": [WIKI_PHYS]}),
        ("particle_physics", "Glueballs", "Do glueball particles exist in nature?", {"sources": [WIKI_PHYS]}),
        ("particle_physics", "Gallium anomaly", "Why are neutrino capture rates on gallium lower than expected?", {"sources": [WIKI_PHYS]}),
        ("nuclear_physics", "QCD phase diagram", "What are the phases of strongly interacting matter?", {"sources": [WIKI_PHYS]}),
        ("nuclear_physics", "Color glass condensate", "Do gluons form a dense system and what are the BFKL signatures?", {"sources": [WIKI_PHYS]}),
        ("nuclear_physics", "Nuclear force nature", "What underlies the nuclear force and what explains the EMC effect?", {"sources": [WIKI_PHYS]}),
        ("nuclear_physics", "Heaviest chemical element", "What is the heaviest possible naturally occurring element?", {"sources": [WIKI_PHYS]}),
        ("condensed_matter", "Glass transition mechanism", "What physical processes underlie the glass transition?", {"sources": [WIKI_PHYS]}),
        ("condensed_matter", "Topological order at finite temperature", "Does topological order persist at non-zero temperature?", {"sources": [WIKI_PHYS]}),
        ("condensed_matter", "Metal whiskering", "What mechanism drives spontaneous metallic whisker growth?", {"sources": [WIKI_PHYS]}),
        ("condensed_matter", "Cryogenic electron emission", "Why does electron emission increase at lower temperatures?", {"sources": [WIKI_PHYS]}),
        ("cosmology", "Hubble tension", "Why do different methods for measuring H0 give discrepant results?", {"sources": [WIKI_PHYS]}),
        ("cosmology", "Dark flow", "Is there a non-spherically-symmetric gravitational pull from outside the observable universe?", {"sources": [WIKI_PHYS]}),
        ("cosmology", "Extra dimensions", "Does nature have more than four spacetime dimensions?", {"sources": [WIKI_PHYS]}),
        ("astrophysics", "Diffuse interstellar bands", "What molecules produce the numerous unidentified interstellar absorption lines?", {"sources": [WIKI_PHYS]}),
        ("astrophysics", "Kuiper cliff", "Why is there a sharp drop in Kuiper belt objects beyond 50 AU?", {"sources": [WIKI_PHYS]}),
        ("astrophysics", "Magnetar magnetic field origin", "How do magnetars acquire their exceptionally strong fields?", {"sources": [WIKI_PHYS]}),
        ("astrophysics", "Cosmic magnetic field origin", "How do large-scale cosmic magnetic fields arise?", {"sources": [WIKI_PHYS]}),
        ("plasma_physics", "H-mode origin", "What is the physical origin of H-mode plasma confinement?", {"sources": [WIKI_PHYS]}),
        ("quantum_computing", "Post-quantum cryptography", "Which cryptographic protocols are safe against quantum computers?", {"sources": [WIKI_PHYS]}),
        ("quantum_computing", "Topological qubits", "Can topological quantum computers be built using Majorana zero modes?", {"sources": [WIKI_PHYS]}),
    ])

    # ── Biology expansions ───────────────────────────────────────────
    WIKI_BIO = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_biology"
    add_to_domain("biology", "BIO", [
        ("evolution", "Maintenance of sexual reproduction", "What selective forces sustain sexual reproduction across species?", {"sources": [WIKI_BIO]}),
        ("evolution", "Development and evolution of the brain", "How and why did brains evolve?", {"sources": [WIKI_BIO]}),
        ("evolution", "The lipid divide", "Why do archaea and bacteria have membrane lipids of opposite chirality?", {"sources": [WIKI_BIO]}),
        ("pharmacology", "Drug mechanism of action", "How do medications like lithium, thalidomide, and ketamine function?", {"sources": [WIKI_BIO]}),
        ("cell_biology", "Mechanism of allosteric transitions", "Do concerted or sequential models explain protein allostery?", {"sources": [WIKI_BIO]}),
        ("developmental_biology", "Biological timekeeping", "Do developing systems possess mechanisms to measure time?", {"sources": [WIKI_BIO]}),
        ("human_biology", "Human sex pheromones", "Do human pheromones exist and influence behavior?", {"sources": [WIKI_BIO]}),
        ("human_biology", "Blood type purpose", "What is the evolutionary origin and biological purpose of blood types?", {"sources": [WIKI_BIO]}),
        ("human_biology", "Body temperature decline", "Why has average human body temperature decreased ~0.6C since the 19th century?", {"sources": [WIKI_BIO]}),
        ("paleontology", "Ediacaran biota classification", "What kingdom do Ediacaran organisms belong to?", {"sources": [WIKI_BIO]}),
        ("paleontology", "Origin of turtles", "Did turtles evolve from anapsids or diapsids?", {"sources": [WIKI_BIO]}),
        ("ecology", "Organism responses to novel environments", "How will organisms respond to complex novel environments under climate change?", {"sources": [WIKI_BIO]}),
        ("ecology", "Population density determinants", "Which mechanisms regulating population density are density-dependent vs independent?", {"sources": [WIKI_BIO]}),
        ("genetics", "Intragenotypic variability", "Why do identical genotypes in identical environments produce striking phenotypic differences?", {"sources": [WIKI_BIO]}),
        ("ethology", "Flocking coordination", "How do bird and bat flocks coordinate rapid movements?", {"sources": [WIKI_BIO]}),
    ])

    # ── Computer science expansions ──────────────────────────────────
    WIKI_CS = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_computer_science"
    add_to_domain("computer_science", "CS", [
        ("computational_complexity", "Strong exponential time hypothesis", "Does SAT require time 2^{(1-epsilon)n} for all epsilon?", {"sources": [WIKI_CS]}),
        ("computational_complexity", "PH = PSPACE", "Does the polynomial hierarchy equal polynomial space?", {"sources": [WIKI_CS]}),
        ("computational_complexity", "Log-rank conjecture", "Communication complexity relates polynomially to log of matrix rank.", {"sources": [WIKI_CS]}),
        ("graph_algorithms", "Clique-width recognition", "Can graphs of bounded clique-width be recognized in polynomial time?", {"sources": [WIKI_CS]}),
        ("parallel_algorithms", "DFS tree in NC", "Can a depth-first search tree be constructed in NC?", {"sources": [WIKI_CS]}),
        ("sorting_algorithms", "Shellsort gap sequence", "What is the lowest average-case complexity of Shellsort with a fixed gap sequence?", {"sources": [WIKI_CS]}),
        ("sorting_algorithms", "X + Y sorting", "Can X + Y be sorted in o(n^2 log n) time?", {"sources": [WIKI_CS]}),
        ("graph_algorithms", "Minimum spanning tree complexity", "What is the algorithmic complexity of the minimum spanning tree problem?", {"sources": [WIKI_CS]}),
        ("computational_geometry", "Gilbert-Pollak conjecture", "Is the Steiner ratio of the Euclidean plane exactly 2/sqrt(3)?", {"sources": [WIKI_CS]}),
        ("formal_languages", "Generalized star-height problem", "Can all regular languages be expressed with bounded star nesting depth?", {"sources": [WIKI_CS]}),
        ("cellular_automata", "Elementary CA Turing completeness", "Which elementary cellular automata are Turing complete?", {"sources": [WIKI_CS]}),
        ("randomized_algorithms", "Schwartz-Zippel derandomization", "Can polynomial identity testing be derandomized?", {"sources": [WIKI_CS]}),
    ])

    # ── Neuroscience expansions ──────────────────────────────────────
    WIKI_NEURO = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_neuroscience"
    add_to_domain("neuroscience", "NEURO", [
        ("consciousness", "Near-death experiences", "What is the mechanism behind near-death experiences?", {"sources": [WIKI_NEURO]}),
        ("consciousness", "Terminal lucidity", "How do patients with deteriorated brains regain consciousness before death?", {"sources": [WIKI_NEURO]}),
        ("consciousness", "Embodied cognition", "Is cognition shaped by the entire body and environment?", {"sources": [WIKI_NEURO]}),
        ("consciousness", "Extended mind thesis", "Does the mind extend into the environment using physical objects?", {"sources": [WIKI_NEURO]}),
        ("consciousness", "Modularity of mind", "Is the mind composed of distinct evolved modules?", {"sources": [WIKI_NEURO]}),
        ("memory", "Genetic vs environmental contributions", "What are the relative genetic and environmental contributions to brain function?", {"sources": [WIKI_NEURO]}),
        ("language", "Innate vs environmental language basis", "Is syntactic ability innate or emergent from environment?", {"sources": [WIKI_NEURO]}),
        ("language", "Second-language acquisition limitations", "Why do L2 learners typically underperform native speakers?", {"sources": [WIKI_NEURO]}),
        ("language", "Animal language capacity", "How much language can animals acquire?", {"sources": [WIKI_NEURO]}),
        ("computational_neuroscience", "Large neuronal circuit dynamics", "How is information processed by collective dynamics of large circuits?", {"sources": [WIKI_NEURO]}),
        ("computational_neuroscience", "Appropriate level of brain description", "What simplification level describes brain information processing?", {"sources": [WIKI_NEURO]}),
    ])

    # ── Astronomy expansions ─────────────────────────────────────────
    WIKI_ASTRO = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_astronomy"
    add_to_domain("astronomy", "ASTRO", [
        ("solar_system", "Iapetus equatorial ridge", "What is the origin of the equatorial mountain chain on Iapetus?", {"sources": [WIKI_ASTRO]}),
        ("solar_physics", "Magnetic reconnection speed", "Why is magnetic reconnection faster than MHD models predict?", {"sources": [WIKI_ASTRO]}),
        ("space_weather", "Space weather prediction", "How can we forecast solar super-storms?", {"sources": [WIKI_ASTRO]}),
        ("stellar_variability", "Tabby's Star", "What causes the unusual luminosity changes of KIC 8462852?", {"sources": [WIKI_ASTRO]}),
        ("galactic_center", "Galactic Center GeV excess", "What is the origin of the gamma-ray excess from the Galactic Center?", {"sources": [WIKI_ASTRO]}),
        ("high_energy_astrophysics", "Infrared/TeV crisis", "Why aren't very energetic gamma rays from distant sources attenuated by IR background?", {"sources": [WIKI_ASTRO]}),
        ("extragalactic", "Little red dots", "What is the nature of little red dots seen in JWST observations?", {"sources": [WIKI_ASTRO]}),
        ("black_holes", "Black hole firewalls", "Do firewalls exist at black hole event horizons?", {"sources": [WIKI_ASTRO]}),
        ("black_holes", "Naked singularity", "Is the cosmic censorship hypothesis correct?", {"sources": [WIKI_ASTRO]}),
        ("cosmology", "CMB dipole nature", "Is the CMB dipole purely kinematic or does it signal anisotropy?", {"sources": [WIKI_ASTRO]}),
        ("cosmology", "Axis of evil (cosmology)", "Why are large-scale CMB features aligned with the ecliptic?", {"sources": [WIKI_ASTRO]}),
        ("cosmology", "Multiverse testability", "Is the multiverse idea scientifically testable?", {"sources": [WIKI_ASTRO]}),
        ("astrobiology", "Wow! signal origin", "Was the 1977 Wow! signal of extraterrestrial origin?", {"sources": [WIKI_ASTRO]}),
        ("nuclear_astrophysics", "Lithium problem", "Why is observed lithium-7 in old stars below Big Bang nucleosynthesis predictions?", {"sources": [WIKI_ASTRO]}),
    ])

    # ── Geoscience expansions ────────────────────────────────────────
    WIKI_GEO = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_geoscience"
    add_to_domain("geoscience", "GEO", [
        ("atmospheric_phenomena", "Hessdalen lights", "What causes the Hessdalen lights?", {"sources": [WIKI_GEO]}),
        ("core_geochemistry", "Outer core light elements", "What are the light alloying elements in the outer core?", {"sources": [WIKI_GEO]}),
    ])


if __name__ == "__main__":
    main()
