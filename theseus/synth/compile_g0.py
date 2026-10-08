"""G0 COMPILER: human concept prose -> structured primitive properties -> genome.

Source ore (charter: source "hephaestus"; historical artifacts are read, never
renamed or edited):
  - agents/nous/src/concepts.py CONCEPTS (95 entries: name, field, mechanism,
    short_description) -- the concept dictionary every Hephaestus/Nous triple
    was drawn from;
  - hecate/programs/HT-*/program.json passes[].concept_extractions (Hecate
    Pass-0 structured breakdowns, ~45 concepts) where present, as extra text.

The compiler is DETERMINISTIC and KEYWORD-BASED: no LLM reads a concept and
decides its mechanism. Each of the charter's 16 primitive properties has a
keyword table; the words that fired are stored as evidence beside the
property. Properties then map to substrate ops by a fixed table; parameters
come from a seed derived from the concept name. The output is a seed, not a
truth: a keyword compiler is crude and its crudeness is recorded, not hidden
(a property-shuffled G0 control tests whether concept identity matters at
all).
"""

from __future__ import annotations

import ast
import glob
import hashlib
import json
import re
import subprocess

import numpy as np

from . import substrate as sb

SOURCE_ARTIFACT = "agents/nous/src/concepts.py"

# property -> {value: [regex fragments]}; order inside a property = priority
PROPS = {
    "state_representation": {
        "discrete": [r"discrete", r"binary", r"\bbit", r"symbol", r"spin", r"boolean", r"digital", r"integer", r"categor"],
        "phase": [r"phase", r"angle", r"cycl", r"periodic", r"oscillat", r"rhythm"],
        "ordinal": [r"\brank", r"order", r"sort", r"hierarch", r"prefer"],
        "continuous": [r"continu", r"field", r"density", r"concentration", r"probabil", r"distribution", r"signal"],
    },
    "multiplicity": {
        "many": [r"species", r"population", r"agents", r"players", r"multiple", r"ensemble", r"many"],
        "two": [r"two ", r"pair", r"dual", r"predator", r"prey", r"opposing", r"bipartite", r"between"],
    },
    "transformations": {
        "spread": [r"diffus", r"spread", r"flow", r"transport", r"percolat", r"propagat"],
        "shift": [r"shift", r"wave", r"translat", r"travel", r"advect", r"drift"],
        "aggregate": [r"aggregat", r"average", r"coarse", r"renormal", r"project", r"compress", r"summar"],
    },
    "invariants": {
        "invariant": [r"invarian", r"preserv", r"unchang", r"constant", r"fixed point"],
    },
    "update_rules": {
        "threshold": [r"threshold", r"fire", r"spike", r"switch", r"trigger", r"tipping", r"bifurcat", r"critical"],
        "multiplicative": [r"multipl", r"product", r"react", r"catalys", r"interact", r"nonlinear"],
        "bounded": [r"saturat", r"bound", r"limit", r"capacity", r"cap\b", r"finite"],
    },
    "locality": {
        "network": [r"network", r"graph", r"node", r"edge", r"connect"],
        "hub": [r"hub", r"central", r"star", r"broadcast", r"leader", r"root"],
        "global": [r"global", r"mean.field", r"all.to.all", r"whole", r"universal"],
        "local": [r"local", r"neighbo", r"adjacen", r"nearby", r"spatial"],
    },
    "scale": {
        "multiscale": [r"scale", r"hierarch", r"level", r"fractal", r"self.similar", r"renormal", r"macro", r"micro"],
    },
    "memory": {
        "memory": [r"memory", r"histor", r"hysteres", r"accumul", r"integrat", r"learn", r"store", r"retain", r"past"],
    },
    "coupling": {
        "inhibitory": [r"inhibit", r"suppress", r"compet", r"antagon", r"negative feedback", r"repress"],
        "excitatory": [r"coupl", r"feedback", r"mutual", r"cooperat", r"reinforc", r"amplif", r"synerg"],
    },
    "failure_modes": {
        "collapse": [r"collaps", r"extinct", r"decay", r"dissipat", r"forget", r"death", r"loss"],
        "runaway": [r"explo", r"diverg", r"instab", r"runaway", r"chao", r"blow"],
    },
    "conservation": {
        "conserved": [r"conserv", r"balance", r"zero.sum", r"budget", r"equilibri", r"steady"],
    },
    "replication": {
        "replicates": [r"replicat", r"reproduc", r"copy", r"copies", r"inherit", r"offspring", r"self.assembl", r"heredit"],
    },
    "symmetry": {
        "symmetric": [r"symmetr", r"mirror", r"reflect", r"parity", r"duality", r"reversib"],
    },
    "topology": {
        "cyclic": [r"topolog", r"circle", r"loop", r"ring", r"torus", r"manifold", r"knot", r"winding", r"modul"],
    },
    "information_movement": {
        "routed": [r"signal", r"message", r"transmi", r"communicat", r"channel", r"rout", r"gate", r"encod"],
        "delayed": [r"delay", r"lag", r"latenc", r"time.delay", r"anticipat", r"predict"],
    },
    "boundary_conditions": {
        "driven": [r"forc", r"driv", r"external", r"stimul", r"input", r"perturb", r"environment"],
        "closed": [r"closed", r"isolat", r"wall", r"contain", r"boundar", r"membrane", r"absorb"],
    },
    "selection_dynamics": {
        "selective": [r"select", r"fitness", r"survival", r"winner", r"prun", r"elimina", r"filter", r"optim"],
    },
}


def load_concepts(ref="HEAD"):
    """Read CONCEPTS from the historical artifact at a git ref, without importing it."""
    src = subprocess.run(["git", "show", f"{ref}:{SOURCE_ARTIFACT}"], capture_output=True,
                         text=True, encoding="utf-8", check=True).stdout
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "CONCEPTS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("CONCEPTS not found")


def load_hecate_extractions():
    out = {}
    for f in sorted(glob.glob("hecate/programs/HT-*/program.json")):
        d = json.load(open(f, encoding="utf-8"))
        for p in d.get("passes", []):
            for ce in p.get("concept_extractions", []) or []:
                if isinstance(ce, dict) and ce.get("concept"):
                    out.setdefault(ce["concept"], []).append((f.replace("\\", "/"), ce))
    return out


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def extract_properties(text):
    t = text.lower()
    props = {}
    for prop, table in PROPS.items():
        for value, pats in table.items():
            hits = sorted({m.group(0) for p in pats for m in re.finditer(p, t)})
            if hits:
                props.setdefault(prop, []).append({"value": value, "evidence": hits[:6]})
    return props


def _has(props, prop, value=None):
    vs = props.get(prop, [])
    return any(v["value"] == value for v in vs) if value else bool(vs)


def properties_to_genome(props, name, readers=False):
    """readers=True (THESEUS-30e variant): memory concepts carry a WRITER only (remember, no
    recall); delayed/routed concepts carry inert-alone READERS (inject/modulate) instead of
    delay/gate -- writers and readers start in different concept lineages."""
    """Fixed property->op table; parameters from a name-derived seed."""
    seed = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    C = 1
    if _has(props, "multiplicity", "two") or _has(props, "coupling"):
        C = 2
    if _has(props, "multiplicity", "many"):
        C = 3
    topo = "ring"
    for v, k in (("network", "rrg"), ("hub", "star"), ("global", "mean"), ("local", "ring")):
        if _has(props, "locality", v):
            topo = k
            break
    if _has(props, "boundary_conditions", "closed") and topo == "ring":
        topo = "line"
    bc = "periodic" if topo != "line" else ("absorb" if _has(props, "failure_modes", "collapse") else "reflect")
    init = "spike"
    if _has(props, "state_representation", "discrete"):
        init = "alternate"
    elif _has(props, "state_representation", "continuous"):
        init = "random"
    elif _has(props, "scale"):
        init = "blocks"
    elif _has(props, "transformations", "shift"):
        init = "gradient"
    prov = f"G0:{slug(name)}"

    def R(op, arity=None):
        return sb.rand_rule(rng, C, op=op, prov=prov, arity=arity)

    rules = []
    if _has(props, "transformations", "spread") or topo in ("ring", "line", "rrg"):
        rules.append(R("diffuse"))
    if _has(props, "transformations", "shift"):
        rules.append(R("advect"))
    if _has(props, "update_rules", "multiplicative") or _has(props, "coupling"):
        r = R("react", arity=min(C, 2) if C > 1 else 1)
        if _has(props, "coupling", "inhibitory"):
            r["p"][0] = -abs(r["p"][0])
        if _has(props, "failure_modes", "runaway"):
            r["p"][0] = sb.clamp_param("react", 0, r["p"][0] * 2.0)
        rules.append(r)
    if _has(props, "update_rules", "threshold"):
        rules.append(R("threshold"))
    if _has(props, "memory"):
        rules.append(R("remember"))
        if not readers:
            rules.append(R("recall"))
    if _has(props, "information_movement", "delayed"):
        rules.append(R("inject" if readers else "delay"))
    if _has(props, "information_movement", "routed") and C > 1:
        rules.append(R("modulate" if readers else "gate"))
    if _has(props, "replication"):
        rules.append(R("replicate"))
    if _has(props, "selection_dynamics"):
        rules.append(R("select"))
    if _has(props, "scale") or _has(props, "transformations", "aggregate"):
        rules.append(R("coarse"))
    if _has(props, "symmetry"):
        rules.append(R("mirror"))
    if _has(props, "state_representation", "ordinal"):
        rules.append(R("rank"))
    if _has(props, "state_representation", "phase") or _has(props, "topology"):
        rules.append(R("wrap"))
    if _has(props, "boundary_conditions", "driven"):
        rules.append(R("drive"))
    if _has(props, "failure_modes", "collapse"):
        rules.append(R("decay"))
    if _has(props, "conservation") or _has(props, "invariants"):
        rules.append(R("conserve"))
    if _has(props, "update_rules", "bounded") or not any(r["op"] in ("saturate", "wrap") for r in rules):
        rules.append(R("saturate"))  # every G0 seed is bounded; unbounded matter is a collision product
    defaulted = len(rules) <= 1
    if defaulted:
        rules.insert(0, R("diffuse"))
        rules.insert(1, R("decay"))
    if readers:
        # strict split: a concept holds at most ONE part. If both a writer and a reader fired,
        # keep one by a name-hash parity (deterministic, independent of the concept's meaning).
        has_w = any(r["op"] == "remember" for r in rules)
        has_r = any(r["op"] in ("inject", "modulate") for r in rules)
        if has_w and has_r:
            keep_writer = int(hashlib.sha256(("split:" + name).encode()).hexdigest(), 16) % 2 == 0
            drop = ("inject", "modulate") if keep_writer else ("remember",)
            rules = [r for r in rules if r["op"] not in drop]
    rules = rules[: sb.MAXRULES]
    g = {"C": C, "topo": {"kind": topo, "seed": int(rng.integers(1 << 16))}, "bc": bc,
         "init": {"kind": init, "amp": 1.0}, "rules": rules}
    assert not sb.validate(g), sb.validate(g)
    return g, defaulted


def compile_corpus(ref="HEAD", readers=False):
    concepts = load_concepts(ref)
    art_sha = subprocess.run(["git", "log", "-1", "--format=%H", ref, "--", SOURCE_ARTIFACT],
                             capture_output=True, text=True, check=True).stdout.strip()
    hec = load_hecate_extractions()
    out = []
    for c in concepts:
        name = c["name"]
        text = " ".join([name, c.get("field", ""), c.get("mechanism", ""), c.get("short_description", "")])
        hec_paths = []
        for path, ce in hec.get(name, []):
            hec_paths.append(path)
            text += " " + " ".join(" ".join(v) if isinstance(v, list) else str(v)
                                   for k, v in ce.items() if k != "concept")
        props = extract_properties(text)
        g, defaulted = properties_to_genome(props, name, readers=readers)
        out.append({
            "id": f"G0-{slug(name)}",
            "generation": 0,
            "origin": "human",
            "genome": g,
            "metadata": {
                "source": "hephaestus",
                "sourceArtifact": SOURCE_ARTIFACT,
                "sourceArtifactSha": art_sha,
                "historicalId": name,
                "field": c.get("field"),
                "mechanism": c.get("mechanism"),
                "short_description": c.get("short_description"),
                "hecate_extractions": sorted(set(hec_paths)),
                "properties": props,
                "compile_defaulted": defaulted,
                "compiler": "theseus.synth.compile_g0 (keyword, deterministic)",
            },
        })
    return out
