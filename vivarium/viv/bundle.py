"""The start bundle: content-addressed start conditions (point release, MUST SHIP).

roles/Vivarium/point_release/START_BUNDLE_SCHEMA.md is the contract; this is
its code. A bundle is a CLOSED key set per bundle_version; every key is
present; a value the producer cannot know is the literal "UNKNOWN" (never
absent, never null); four sub-keys are FILLED by Vivarium at claim (engine,
executor, initial_artifacts, rng.seed_root / seed_derivation); everything
else is verbatim from the enqueue. Vivarium reads nothing inside the
producer's values.

    design_digest = "sha256:" + sha256(spec_hash + "|" + bundle_hash)

Canonicalisation is viv.spec.canonical_bytes (sorted keys, no whitespace,
UTF-8), the same function that seals the spec; the golden fixture in
tests/test_bundle.py pins that two encodings of one semantic bundle hash
identically and that the four filled keys are the only ones Vivarium writes.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from . import spec as _spec

BUNDLE_VERSION = "viv.start_bundle.v1"
UNKNOWN = "UNKNOWN"

#: The closed key set. Extension = a new BUNDLE_VERSION, never a free key.
#: Proteus #338: no top-level foundry_profile -- it lives INSIDE population
#: (one owner, one place); population carries population_schema so a
#: pre-manifest bundle says "UNKNOWN" rather than looking like a manifest.
KEYS = ("bundle_version", "spec_hash", "engine", "executor", "world_manifest",
        "evaluator", "schedule", "population",
        "initial_artifacts", "interventions_declared", "gates", "rng", "budget",
        "external", "factors")

#: Keys Vivarium fills at claim; the producer's values for them are ignored
#: and REPLACED (recorded as bundle_hash_declared vs bundle_hash).
FILLED_BY_VIVARIUM = ("engine", "executor", "initial_artifacts")
FILLED_RNG = ("seed_root", "seed_derivation")

SCALAR = (str, int, float, bool)


class BundleError(ValueError):
    def __init__(self, reasons):
        self.reasons = list(reasons)
        super().__init__("; ".join(self.reasons))


def problems(bundle: Any, *, spec: Optional[dict] = None) -> List[str]:
    """Every reason `bundle` is not a valid declared bundle. Empty = ok.
    Structural only: values are never interpreted."""
    r: List[str] = []
    if not isinstance(bundle, dict):
        return ["bundle must be an object"]
    extra = sorted(set(bundle) - set(KEYS))
    if extra:
        r.append("bundle has unknown key(s) %s; the key set is closed per bundle_version "
                 "(extend by a new version, never a free key)" % extra)
    missing = sorted(set(KEYS) - set(bundle))
    if missing:
        r.append("bundle is missing key(s) %s; an unknown value is the literal \"UNKNOWN\", "
                 "never an absent key" % missing)
    if bundle.get("bundle_version") != BUNDLE_VERSION:
        r.append("bundle_version must be %r" % BUNDLE_VERSION)
    for k in KEYS:
        if k in bundle and bundle[k] is None:
            r.append("bundle.%s is null; use \"UNKNOWN\"" % k)
    for k in ("initial_artifacts", "interventions_declared", "gates", "external"):
        v = bundle.get(k)
        if v is not None and not isinstance(v, list):
            r.append("bundle.%s must be a list (empty when none)" % k)
    f = bundle.get("factors")
    if isinstance(f, dict):
        for name, v in f.items():
            if not isinstance(v, SCALAR) or isinstance(v, float) and v != v:
                r.append("bundle.factors[%r] must be a scalar (string/number/bool); a stratum label "
                         "is a label" % name)
    elif f is not None and f != UNKNOWN:
        r.append("bundle.factors must be an object of scalars")
    if spec is not None and bundle.get("spec_hash") not in (UNKNOWN, _spec.spec_hash(spec)):
        r.append("bundle.spec_hash does not name the spec it accompanies")
    return r


def canonical(bundle: dict) -> bytes:
    return _spec.canonical_bytes(bundle)


def bundle_hash(bundle: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical(bundle)).hexdigest()


def design_digest(spec_hash: str, bhash: Optional[str]) -> str:
    """design := spec x bundle. With no bundle (pre-release rows) the design
    IS the spec, which is what those rows always meant."""
    if bhash is None:
        return spec_hash
    return "sha256:" + hashlib.sha256(("%s|%s" % (spec_hash, bhash)).encode("utf-8")).hexdigest()


def declared_skeleton(spec: dict) -> dict:
    """A bundle with every key UNKNOWN except what the spec itself fixes --
    what an enqueue with no producer bundle means. Vivarium fills the rest."""
    return {
        "bundle_version": BUNDLE_VERSION,
        "spec_hash": _spec.spec_hash(spec),
        "engine": UNKNOWN, "executor": UNKNOWN, "world_manifest": UNKNOWN,
        "evaluator": UNKNOWN, "schedule": UNKNOWN,
        # Proteus #338: {manifest_hash, manifest_ref, population_schema} until
        # proteus.population_manifest.v1 exists; foundry profile inside it,
        # string form "pfp1:<16 hex>" once minted, else Archaeon's
        # "instr<lo>-<hi>:<8 hex>" VERBATIM (scheme archaeon.wse.reachability.foundry_id.v1)
        "population": {"population_schema": UNKNOWN, "manifest_hash": UNKNOWN, "manifest_ref": UNKNOWN,
                       "foundry_profile": UNKNOWN},
        "initial_artifacts": [], "interventions_declared": [], "gates": [],
        "rng": {"seed_root": spec["world"]["seed_root"],
                "seed_derivation": (spec.get("repeat") or {}).get("seed_derivation", UNKNOWN),
                "campaign_seed": UNKNOWN, "rng_label": UNKNOWN},
        "budget": dict((spec.get("repeat") or {}).get("budget") or {}),
        "external": [], "factors": {},
    }


def fill(declared: dict, *, spec: dict, engine: dict, executor: dict,
         initial_artifacts: list) -> dict:
    """The claim-time bundle: the producer's declaration with Vivarium's four
    facts written over their slots. Returns a NEW dict; `declared` is not
    mutated (it is what bundle_hash_declared hashes)."""
    b = json.loads(json.dumps(declared))
    b["engine"] = {k: engine.get(k, UNKNOWN) for k in
                   ("engine_instance_id", "engine_source_hash", "schema_version", "contract_hash")}
    b["executor"] = {k: executor.get(k, UNKNOWN) for k in
                     ("kind", "kind_contract_digest", "viv_version", "viv_base_sha")}
    b["initial_artifacts"] = list(initial_artifacts)
    rng = dict(b.get("rng") or {}) if isinstance(b.get("rng"), dict) else {}
    rng["seed_root"] = spec["world"]["seed_root"]
    rng["seed_derivation"] = (spec.get("repeat") or {}).get("seed_derivation", UNKNOWN)
    rng.setdefault("campaign_seed", UNKNOWN)
    rng.setdefault("rng_label", UNKNOWN)
    b["rng"] = rng
    return b


def diff(a: dict, b: dict, prefix: str = "") -> List[str]:
    """Key paths that differ. Never says which difference matters."""
    out: List[str] = []
    keys = sorted(set(a) | set(b)) if isinstance(a, dict) and isinstance(b, dict) else None
    if keys is None:
        return [prefix or "<root>"] if a != b else []
    for k in keys:
        p = "%s.%s" % (prefix, k) if prefix else k
        if k not in a or k not in b:
            out.append(p)
        elif isinstance(a[k], dict) and isinstance(b[k], dict):
            out.extend(diff(a[k], b[k], p))
        elif a[k] != b[k]:
            out.append(p)
    return out


def kind_contract_digest(kind) -> str:
    """sha over the registry entry's contract-bearing fields, so a changed
    contract is visible in the bundle."""
    body: Dict[str, Any] = {
        "kind": kind.kind, "params": sorted(kind.params),
        "result_schema": {n: {"type": f.type, "required": f.required, "bounds": list(f.bounds) if f.bounds else None,
                              "element": f.element, "reductions": list(f.reductions)}
                          for n, f in sorted(kind.result_schema.items())},
        "value_checker": kind.value_checker, "axes": dict(sorted(kind.axes.items())),
        "artifact_slots": sorted(kind.artifact_slots),
        "optional_artifact_slots": sorted(kind.optional_artifact_slots),
        "stateful": kind.stateful,
    }
    return "sha256:" + hashlib.sha256(_spec.canonical_bytes(body)).hexdigest()
