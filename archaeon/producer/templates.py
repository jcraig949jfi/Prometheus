"""The experiment template registry: the MENU that random science draws from.

A template is DATA -- a JSON file under ``archaeon/templates/`` -- declaring a
Vivarium-implemented kind, a parameter space, where the idea came from, and
whether a human has admitted it. The tick selects a template and draws
parameters from its space; both draws are seeded and recorded.

Three rules, each the mechanical form of a charter line:

* **Admission is a human act.** A template is drawn from only when its status
  is ADMITTED, and only the operator sets that. Anything an LLM, a literature
  miner, another seat, or the CHAOS operator produces lands in
  ``archaeon/templates/inbox/`` as PROPOSED and is never drawn from. This is
  the line that keeps the tick path model-free while letting the menu grow
  from every source.
* **A template whose kind Vivarium does not implement is an expansion
  request**, by construction. It may be PROPOSED; it cannot be ADMITTED.
  ``check()`` says so, naming the lane.
* **Templates are frozen once admitted.** The file's content hash is recorded
  at admission and compared on every load; a template that changed after it
  was admitted is refused, because a drawn experiment must be re-derivable
  from the template id alone. Growth is a NEW template, not an edit.

The first template, ``bitstring.uniform.v0``, is the previous random generator
ported verbatim, and it is the FROZEN RANDOM BASELINE for M-SIGNAL. It must
never change; a better random policy is a second template.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
INBOX_DIR = TEMPLATES_DIR / "inbox"

STATUSES = ("PROPOSED", "ADMITTED", "RETIRED")
ORIGINS = ("RNG", "HUMAN", "LLM", "LITERATURE", "CHAOS")
REGISTRY_VERSION = "archaeon.template.v0"


class TemplateError(Exception):
    pass


WORLD_PARAMS = ("seed_root",)


def normalize_param_space(ps: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Accept both shapes, return the nested one and which was given.

    The registry nests parameters under ``world`` and ``payload``. The
    roadmap's illustrative example did not show the nesting, and Herakles
    wrote 69 templates FLAT against it; against the real loader all 69 loaded
    and zero were runnable (Herakles, expansion-design pass, 2026-09-06). The
    inconsistency was Archaeon's. The mapping from flat to nested is fixed by
    NAME, not inferred: ``seed_root`` is the only world parameter Vivarium's
    kinds accept; everything else is payload.
    """
    if not isinstance(ps, dict):
        raise TemplateError("param_space must be an object")
    if {"world", "payload"} & set(ps):
        extra = set(ps) - {"world", "payload"}
        if extra:
            raise TemplateError("nested param_space has unknown sections {}"
                                .format(sorted(extra)))
        return ({"world": dict(ps.get("world", {})),
                 "payload": dict(ps.get("payload", {}))}, "nested")
    world = {k: v for k, v in ps.items() if k in WORLD_PARAMS}
    payload = {k: v for k, v in ps.items() if k not in WORLD_PARAMS}
    return ({"world": world, "payload": payload}, "flat")


def _content_hash(t: Dict[str, Any]) -> str:
    """Hash of the SCIENTIFIC content: kind + param_space + version. Not of
    status/admission fields, which are allowed to change exactly once."""
    ps, _form = normalize_param_space(t["param_space"])   # hash the canonical form
    body = {"template_id": t["template_id"], "kind": t["kind"],
            "param_space": ps,
            "registry_version": t.get("registry_version")}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def load(path: Path) -> Dict[str, Any]:
    t = json.loads(Path(path).read_text(encoding="utf-8"))
    for k in ("template_id", "kind", "param_space", "origin", "status"):
        if k not in t:
            raise TemplateError("{}: missing {!r}".format(path.name, k))
    if t["status"] not in STATUSES:
        raise TemplateError("{}: bad status {!r}".format(path.name, t["status"]))
    if t["origin"].get("source") not in ORIGINS:
        raise TemplateError("{}: origin.source must be one of {}"
                            .format(path.name, ORIGINS))
    t["_path"] = str(path)
    t["param_space"], t["_param_space_form"] = normalize_param_space(t["param_space"])
    t["_content_hash"] = _content_hash(t)
    if t["status"] == "ADMITTED":
        if t.get("admitted_content_hash") != t["_content_hash"]:
            raise TemplateError(
                "{}: ADMITTED template's content changed after admission "
                "(admitted {} != current {}). Growth is a NEW template, not an "
                "edit; an admitted template is frozen so every experiment "
                "drawn from it stays re-derivable from its id."
                .format(path.name, t.get("admitted_content_hash"),
                        t["_content_hash"]))
        if not t.get("admitted_by"):
            raise TemplateError("{}: ADMITTED without admitted_by".format(path.name))
    return t


def load_all(directory: Optional[Path] = None) -> List[Dict[str, Any]]:
    d = Path(directory or TEMPLATES_DIR)
    out = []
    for p in sorted(d.glob("*.json")):
        out.append(load(p))
    return out


def admitted(directory: Optional[Path] = None,
             region_directed: bool = False) -> List[Dict[str, Any]]:
    """The menu. Only ADMITTED templates whose kind Vivarium implements.

    Two menus, never mixed: the RANDOM menu (default) holds templates whose
    every parameter is drawn; the REGION-DIRECTED menu holds templates with a
    `from_region` parameter. The baseline policy draws only from the first,
    so a directed template can never leak into the random control.
    """
    menu = []
    for t in load_all(directory):
        if t["status"] != "ADMITTED":
            continue
        if is_region_directed(t) != region_directed:
            continue
        c = check(t)
        if c["runnable"] and c["drawable"] and c["buildable"]:
            menu.append(t)
    return menu


_NOT_RUNNABLE = {"runnable": False, "drawable": False, "buildable": False,
                 "lane": None, "reason": None}


def check(t: Dict[str, Any]) -> Dict[str, Any]:
    """Can this template be run? If not, which lane does the gap belong to?

    Three facts, in order, each only asked if the previous held:
      runnable   the kind is implemented and the payload NAMES match
      drawable   a fixed-seed draw succeeds (F-2: names are not drawability)
      buildable  the drawn parameters build a valid spec (C-6: cross-axis
                 coherence is enforced by the builder, not by the template)
    """
    from .contract import ensure_viv_importable
    ensure_viv_importable()
    try:
        from viv import kinds as vk
    except Exception as exc:                       # pragma: no cover
        return dict(_NOT_RUNNABLE, lane="vivarium",
                    reason="registry unavailable: {}".format(exc))
    k = vk.get(t["kind"])
    if k is None:
        return dict(_NOT_RUNNABLE, lane="vivarium",
                    reason="kind {!r} is not registered; this template is an "
                           "expansion request".format(t["kind"]))
    if not k.implemented:
        return dict(_NOT_RUNNABLE, lane="vivarium",
                    reason="kind {!r} is registered but has no executor"
                           .format(t["kind"]))
    declared = set(t["param_space"].get("payload", {}))
    base = dict(_NOT_RUNNABLE)
    if declared != set(k.params):
        return dict(base, lane="archaeon",
                    reason="template payload params {} != kind params {}"
                           .format(sorted(declared), sorted(k.params)))
    base["runnable"] = True
    # F-2 (Herakles): validating NAMES let templates with destroyed ranges
    # pass check() and raise inside the scheduled producer. A template is
    # admissible only if a draw with a fixed seed succeeds ...
    region = (PROBE_REGION if is_region_directed(t) else None)
    try:
        params = draw_params(t, seed=0, region_params=region)
    except TemplateError as exc:
        return dict(base, lane="archaeon", reason="not drawable: {}".format(exc))
    except Exception as exc:
        return dict(base, lane="archaeon",
                    reason="not drawable: {}: {}".format(type(exc).__name__, exc))
    base["drawable"] = True
    # ... and (C-6) if the drawn parameters build a spec the kind accepts,
    # which is where cross-axis coherence (len(bits) == length) is enforced.
    from . import specbuild
    if t["kind"] != specbuild.KIND:
        return dict(base, lane="archaeon",
                    reason="spec builder supports only {!r}; a template on "
                           "{!r} needs the kind-generic builder with a "
                           "template-declared outcome_rule (E18)"
                           .format(specbuild.KIND, t["kind"]))
    try:
        specbuild.build_validated(dict(params))
    except Exception as exc:
        return dict(base, lane="archaeon",
                    reason="drawn parameters do not build a valid spec: {}"
                           .format(str(exc)[:200]))
    base["buildable"] = True
    return base


# A synthetic region so a region-directed template can be dry-drawn at check
# time. It is never published: check() builds and discards.
PROBE_REGION = {"world_id": "probe", "seed_root": 1, "length": 16}


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------
def _draw_value(spec: Dict[str, Any], rng: random.Random,
                already: Dict[str, Any]) -> Any:
    """One parameter from its declared space. The vocabulary is closed."""
    if "constant" in spec:
        # C-0 (Herakles): pin a value and every draw is a new query against
        # the SAME hidden target -- a series of specs becomes one game.
        return spec["constant"]
    if "choices" in spec:
        if not spec["choices"]:
            raise TemplateError("choices is empty; a REPAIRED axis with no "
                                "value must be supplied at admission")
        return rng.choice(list(spec["choices"]))
    if "int_range" in spec:
        if spec["int_range"] is None:
            raise TemplateError("int_range is null: the value was destroyed "
                                "in the source and left null on purpose; it "
                                "must be supplied at admission, never guessed")
        lo, hi = spec["int_range"]
        return rng.randint(int(lo), int(hi))
    if "uniform_bits" in spec:
        n = int(already[spec["uniform_bits"]])
        return "".join(rng.choice("01") for _ in range(n))
    if "from_region" in spec:
        # TAKEN FROM THE DETECTED REGION, not drawn. This is what makes a
        # template region-directed: its parameters change with the region a
        # detector fired on. Drawable only with region context; without it the
        # draw refuses rather than inventing a value (see draw_params).
        return already["__region__"][spec["from_region"]]
    raise TemplateError("unknown parameter space form: {}".format(sorted(spec)))


def is_region_directed(t: Dict[str, Any]) -> bool:
    """True iff any parameter is taken from the region rather than drawn."""
    return any("from_region" in spec
               for section in t["param_space"].values()
               for spec in section.values())


def required_region_fields(t: Dict[str, Any]) -> List[str]:
    return sorted({spec["from_region"]
                   for section in t["param_space"].values()
                   for spec in section.values() if "from_region" in spec})


def draw_params(t: Dict[str, Any], seed: int,
                region_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Deterministic draw, INDEPENDENT of key order.

    A parameter that references another (uniform_bits -> length) is drawn
    after every independent one. The first version trusted declared key
    order; the shipped baseline was written with sort_keys=True, which puts
    `bits` before `length`, and the draw raised KeyError on the very template
    the loop runs. Template files must be re-derivable and hashable, which
    means sorted keys, which means order carries no meaning here.

    Draw order is fixed by NAME (sorted) within each pass so the seed maps to
    the same parameters regardless of how the file was written.
    """
    rng = random.Random(seed)
    out: Dict[str, Any] = {}
    need = required_region_fields(t)
    if need:
        missing = [f for f in need if not region_params or f not in region_params]
        if missing:
            raise TemplateError(
                "template {} is region-directed and needs region fields {} "
                "but none were supplied; a region-directed draw without a "
                "region would be a random draw wearing a directed label"
                .format(t["template_id"], missing))
        out["__region__"] = dict(region_params)
    items = []
    for section in ("world", "payload"):
        for k, spec in t["param_space"].get(section, {}).items():
            items.append((k, spec))
    # region-taken first (they are inputs), then independent draws, then
    # dependent ones -- all in name order so key order in the file is moot
    region = sorted((k, s) for k, s in items if "from_region" in s)
    independent = sorted((k, s) for k, s in items
                         if "from_region" not in s and "uniform_bits" not in s)
    dependent = sorted((k, s) for k, s in items if "uniform_bits" in s)
    for k, spec in region + independent + dependent:
        out[k] = _draw_value(spec, rng, out)
    out.pop("__region__", None)
    return out


def derive_seed(lane: str, day: str, template_id: str, nonce: str = "") -> int:
    blob = "|".join([REGISTRY_VERSION, lane, day, template_id, nonce]).encode()
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "big")


def choose_template(menu: List[Dict[str, Any]], lane: str, day: str,
                    nonce: str = "") -> Dict[str, Any]:
    """Uniform over the admitted menu. Coverage weighting is a later, named
    policy; uniform is the baseline and is recorded as such."""
    if not menu:
        raise TemplateError("the admitted menu is empty")
    seed = derive_seed(lane, day, "<menu>", nonce)
    idx = random.Random(seed).randrange(len(menu))
    return menu[idx]


def draw(lane: str, day: str, nonce: str = "",
         directory: Optional[Path] = None,
         region: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """One (template, params) draw with full provenance.

    With ``region`` supplied, draws from the REGION-DIRECTED menu under policy
    menu.region_directed.v0 and the `from_region` parameters are taken from
    it. Without, the uniform baseline over the random menu. Two named
    policies, never mixed in one draw.
    """
    menu = admitted(directory, region_directed=region is not None)
    t = choose_template(menu, lane, day, nonce)
    seed = derive_seed(lane, day, t["template_id"], nonce)
    params = draw_params(t, seed, region_params=region)
    return {
        "policy": ("menu.region_directed.v0" if region is not None
                   else "menu.uniform.v0"),
        "region": (dict(region) if region is not None else None),
        "template_id": t["template_id"],
        "template_content_hash": t["_content_hash"],
        "kind": t["kind"],
        "seed": seed,
        "seed_inputs": {"lane": lane, "day": day, "nonce": nonce,
                        "template_id": t["template_id"]},
        "menu": sorted(m["template_id"] for m in menu),
        "menu_size": len(menu),
        "space": t["param_space"],
        "params": params,
    }


# --------------------------------------------------------------------------
# Proposing (never admitting)
# --------------------------------------------------------------------------
def propose(t: Dict[str, Any], *, directory: Optional[Path] = None) -> Path:
    """Write a PROPOSED template into the inbox. Nothing here can admit."""
    d = Path(directory or INBOX_DIR)
    d.mkdir(parents=True, exist_ok=True)
    t = dict(t)
    t["status"] = "PROPOSED"
    t.pop("admitted_by", None)
    t.pop("admitted_at", None)
    t.pop("admitted_content_hash", None)
    t["registry_version"] = REGISTRY_VERSION
    path = d / "{}.json".format(t["template_id"])
    if path.exists():
        raise TemplateError("{} already proposed".format(t["template_id"]))
    path.write_text(json.dumps(t, indent=2, sort_keys=True), encoding="utf-8")
    return path


def menu_growth(directory: Optional[Path] = None) -> Dict[str, Any]:
    """The metric Challenge 2 is judged by: is the menu growing?"""
    ts = load_all(directory)
    inbox = list((Path(directory or TEMPLATES_DIR) / "inbox").glob("*.json")) \
        if (Path(directory or TEMPLATES_DIR) / "inbox").exists() else []
    adm = [t for t in ts if t["status"] == "ADMITTED"]
    by_origin: Dict[str, int] = {}
    for t in adm:
        by_origin[t["origin"]["source"]] = by_origin.get(t["origin"]["source"], 0) + 1
    return {"admitted": len(adm), "proposed_in_inbox": len(inbox),
            "retired": sum(1 for t in ts if t["status"] == "RETIRED"),
            "admitted_by_origin": by_origin,
            "admitted_at": sorted(t.get("admitted_at") or "" for t in adm)}


# --------------------------------------------------------------------------
# Coverage-weighted choice: a NAMED policy, not the baseline
# --------------------------------------------------------------------------
def usage_counts(conn, lane: str, limit: int = 2000) -> Dict[str, int]:
    """How often each template has been published in this lane. Read from the
    queue's source_evidence -- a publication fact, not an execution one."""
    from .. import vivqueue as vq
    cur = conn.cursor()
    cur.execute("SELECT source_evidence->>'template_id' FROM {q} "
                " WHERE cadence_lane = %s AND cadence_day_ordinal IS NOT NULL "
                " ORDER BY created_at DESC LIMIT %s".format(q=str(vq.QUEUE)),
                (lane, int(limit)))
    out: Dict[str, int] = {}
    for (tid,) in cur.fetchall():
        if tid:
            out[tid] = out.get(tid, 0) + 1
    return out


def choose_template_coverage(menu: List[Dict[str, Any]],
                             counts: Dict[str, int], lane: str, day: str,
                             nonce: str = "") -> Dict[str, Any]:
    """Weight each admitted template by 1/(1+uses). Seeded; recorded as
    policy menu.coverage.v0. A less-used template is preferred, a never-used
    one most of all -- the same bias the exploration fallback used for cells,
    applied to the menu. Not switched on in tick(); it is available as a
    second named policy so it can be compared against the uniform baseline
    rather than silently replacing it."""
    if not menu:
        raise TemplateError("the admitted menu is empty")
    weights = [1.0 / (1.0 + counts.get(t["template_id"], 0)) for t in menu]
    seed = derive_seed(lane, day, "<menu-coverage>", nonce)
    rng = random.Random(seed)
    r = rng.random() * sum(weights)
    acc = 0.0
    for t, w in zip(menu, weights):
        acc += w
        if r <= acc:
            return t
    return menu[-1]
