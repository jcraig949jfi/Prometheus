"""P-7: immutable verification bundles. The unit of adjudication in Cycle 9.

THE DEFECT THIS REPAIRS. The predecessor scheduler kept a mutable record per family:

    rec = self.families.setdefault(fam, {... "control_summary": None,
                                          "sibling_atomic": None, ...})

and fired its special flags at the instant a treatment run completed, reading that slot:

    ctrl = rec.get("control_summary")
    if summary.get("crossed") and d["endogenous"] and ctrl is not None \
            and not ctrl.get("crossed") and rec.get("control_axis") == "reproduction":
        out.append({"flag": "REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION", ...})

Three consequences, all of them order dependence rather than science:

  1. If the control had not completed yet, `ctrl is None`, the flag did not fire, and
     nothing ever re-evaluated it. The same experiment with the same numbers produced a
     flag or no flag depending purely on which worker finished first.
  2. `control_summary` is a single slot. A family with several controls kept whichever
     one landed last, so the comparison silently changed identity over the campaign.
  3. On resume, `load_state` restored the family records and re-queued in-flight runs.
     Completion order after a restart differs from the order before it, so a restart
     could change which flags exist.

WHAT REPLACES IT. A bundle is a frozen, content-addressed DEFINITION of one comparison,
plus an accumulated set of results keyed by arm name. Nothing about it depends on when a
result arrived:

  * `bundle_id` is sha256 over the canonical definition, so the same scientific question
    always has the same identity, computed before any run executes.
  * `BundleSpec` is immutable - assignment after construction raises.
  * `BundleState.add_result` is keyed by arm. Re-adding identical content is idempotent,
    which is what a re-run after a kill needs; re-adding DIFFERENT content for an arm
    already present raises, because that is a determinism violation and must be loud.
  * `adjudicate()` refuses to return a verdict at all until the bundle is complete. There
    is no "evaluate what we have so far" path, so there is nothing for arrival order to
    influence.
  * `BundleStore` writes one file per bundle atomically (temp then os.replace), so a kill
    mid-write leaves either the old file or the new one, never a torn one. State is
    rebuilt from disk, so resume carries no in-memory residue.
  * `scientific_content()` strips VOLATILE_KEYS - timestamps, wall clock, paths, host,
    pid, completion ordering - leaving the bytes that must be identical no matter how the
    campaign was scheduled, interrupted or resumed.

Nothing here decides science. The default adjudication rule is a thin margin comparison
over the P-3 fields; the point of this module is that WHEN a verdict is computed cannot
change WHAT it is.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import tempfile

PROTOCOL_VERSION = "z80atlas-verify-1"

# Fields that may legitimately differ between two executions of the same bundle. They are
# excluded from every byte-equality comparison and from scientific content. Named as a
# module constant so the test and the review packet refer to the same list rather than
# each keeping its own copy.
VOLATILE_KEYS = frozenset({
    # wall clock and scheduling
    "ts", "timestamp", "started_at", "completed_at", "wall_s", "wall_seconds", "duration_s",
    # execution environment
    "host", "hostname", "pid", "worker", "worker_id",
    # filesystem location
    "path", "paths", "dir", "run_dir", "observatory_dir", "root", "source_root",
    # completion ordering - the defect this module exists to remove
    "completion_order", "arrival_index", "arrival_rank", "order",
})

ROLES = ("TREATMENT", "CONTROL", "INTERVENTION")

# Declared here, not inherited implicitly, so the bundle layer's rule is auditable in one
# place. These mirror adjudicate.py; if they ever diverge the campaign gate says so.
CROSS = 0.90
MARGIN = 0.25

VERDICT_INCOMPLETE = "INCOMPLETE"


class BundleError(Exception):
    """A structural violation: a conflicting result, an unknown arm, a broken spec."""


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, default=str)


def _scrub(obj):
    """Recursively drop VOLATILE_KEYS and canonicalise ordering."""
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in sorted(obj.items()) if k not in VOLATILE_KEYS}
    if isinstance(obj, (list, tuple)):
        return [_scrub(v) for v in obj]
    return obj


class ArmSpec:
    """One leg of a comparison. Frozen once built."""

    __slots__ = ("name", "role", "cell", "seed", "tier", "_frozen")

    def __init__(self, name, role, cell, seed, tier="S"):
        if role not in ROLES:
            raise BundleError("unknown arm role %r (expected one of %s)" % (role, ", ".join(ROLES)))
        object.__setattr__(self, "name", str(name))
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "cell", dict(cell))
        object.__setattr__(self, "seed", int(seed))
        object.__setattr__(self, "tier", str(tier))
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, k, v):
        raise BundleError("ArmSpec is immutable; attempted to set %r" % k)

    def canonical(self):
        return {"name": self.name, "role": self.role, "cell": self.cell,
                "seed": self.seed, "tier": self.tier}

    @staticmethod
    def from_dict(d):
        return ArmSpec(d["name"], d["role"], d["cell"], d["seed"], d.get("tier", "S"))


class BundleSpec:
    """The frozen definition of one comparison. Content-addressed.

    `bundle_id` is computed from the definition alone, so it exists before any run does
    and cannot drift as results arrive.
    """

    __slots__ = ("hypothesis_id", "pair_seed", "arms", "factor_deltas",
                 "expected_cardinality", "protocol_version", "bundle_id", "_frozen")

    def __init__(self, hypothesis_id, pair_seed, arms, factor_deltas,
                 expected_cardinality=None, protocol_version=PROTOCOL_VERSION):
        arms = list(arms)
        if not arms:
            raise BundleError("a bundle needs at least one arm")
        names = [a.name for a in arms]
        if len(set(names)) != len(names):
            raise BundleError("duplicate arm names: %s" % sorted(names))
        if not any(a.role == "TREATMENT" for a in arms):
            raise BundleError("a bundle needs a TREATMENT arm")
        card = len(arms) if expected_cardinality is None else int(expected_cardinality)
        if card != len(arms):
            # A manifest that declares a cardinality its own arm list contradicts is a
            # manifest bug, and it must fail at construction rather than at adjudication.
            raise BundleError("expected_cardinality %d does not match %d declared arms"
                              % (card, len(arms)))
        object.__setattr__(self, "hypothesis_id", str(hypothesis_id))
        object.__setattr__(self, "pair_seed", int(pair_seed))
        object.__setattr__(self, "arms", tuple(sorted(arms, key=lambda a: a.name)))
        object.__setattr__(self, "factor_deltas", dict(factor_deltas))
        object.__setattr__(self, "expected_cardinality", card)
        object.__setattr__(self, "protocol_version", str(protocol_version))
        object.__setattr__(self, "bundle_id",
                           hashlib.sha256(_canon(self.canonical()).encode("ascii")).hexdigest())
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, k, v):
        raise BundleError("BundleSpec is immutable; attempted to set %r" % k)

    def canonical(self):
        """Everything the identity depends on. Arms are sorted, so definition order
        cannot change the id."""
        return {"hypothesis_id": self.hypothesis_id,
                "pair_seed": self.pair_seed,
                "arms": [a.canonical() for a in self.arms],
                "factor_deltas": self.factor_deltas,
                "expected_cardinality": self.expected_cardinality,
                "protocol_version": self.protocol_version}

    def protocol_hash(self):
        """Hash of the protocol alone: roles, deltas, cardinality, version - but not the
        particular seed. Two bundles asking the same question of different seeds share
        this."""
        body = {"hypothesis_id": self.hypothesis_id,
                "roles": sorted((a.name, a.role) for a in self.arms),
                "factor_deltas": self.factor_deltas,
                "expected_cardinality": self.expected_cardinality,
                "protocol_version": self.protocol_version}
        return hashlib.sha256(_canon(body).encode("ascii")).hexdigest()

    def arm(self, name):
        for a in self.arms:
            if a.name == name:
                return a
        return None

    def required_arms(self):
        return frozenset(a.name for a in self.arms)

    @staticmethod
    def from_dict(d):
        return BundleSpec(d["hypothesis_id"], d["pair_seed"],
                          [ArmSpec.from_dict(a) for a in d["arms"]],
                          d["factor_deltas"], d["expected_cardinality"],
                          d.get("protocol_version", PROTOCOL_VERSION))


class BundleState:
    """A spec plus whatever results have landed. Order of landing is not recorded."""

    __slots__ = ("spec", "results")

    def __init__(self, spec, results=None):
        self.spec = spec
        self.results = dict(results or {})

    def add_result(self, arm_name, result):
        """Idempotent for identical content; loud for conflicting content.

        A re-run after a kill legitimately re-delivers the same arm, so that must not be
        an error. A re-run that delivers DIFFERENT numbers for the same arm means the
        substrate is not deterministic, which would silently corrupt every downstream
        comparison, so it raises here rather than overwriting.
        """
        if self.spec.arm(arm_name) is None:
            raise BundleError("arm %r is not declared in bundle %s"
                              % (arm_name, self.spec.bundle_id[:12]))
        scrubbed = _scrub(result)
        if arm_name in self.results:
            if _canon(self.results[arm_name]) != _canon(scrubbed):
                raise BundleError(
                    "arm %r already has a different result in bundle %s: a re-run "
                    "produced different numbers, which is a determinism violation"
                    % (arm_name, self.spec.bundle_id[:12]))
            return False
        self.results[arm_name] = scrubbed
        return True

    def missing_arms(self):
        return sorted(self.spec.required_arms() - set(self.results))

    def is_complete(self):
        return (set(self.results) == self.spec.required_arms()
                and len(self.results) == self.spec.expected_cardinality)

    def adjudicate(self, rule=None):
        """No verdict until the bundle is complete. This is the whole point.

        The predecessor evaluated at each completion against whatever had landed, so the
        answer depended on scheduling. Here an incomplete bundle yields a structured
        INCOMPLETE that names what is missing, and never a verdict.
        """
        if not self.is_complete():
            return {"bundle_id": self.spec.bundle_id,
                    "hypothesis_id": self.spec.hypothesis_id,
                    "verdict": VERDICT_INCOMPLETE,
                    "why": "bundle incomplete: %d of %d arms present"
                           % (len(self.results), self.spec.expected_cardinality),
                    "missing_arms": self.missing_arms(),
                    "numbers": {}}
        return (rule or default_rule)(self.spec, self.results)

    def to_dict(self):
        return {"spec": self.spec.canonical(),
                "bundle_id": self.spec.bundle_id,
                "protocol_hash": self.spec.protocol_hash(),
                "results": self.results}

    @staticmethod
    def from_dict(d):
        return BundleState(BundleSpec.from_dict(d["spec"]), d.get("results"))


def scientific_content(state):
    """The canonical dict that must be byte-identical across executions.

    Excludes VOLATILE_KEYS at every level and records no arrival order. Two runs of the
    same bundle that differ only in scheduling produce identical bytes here; two that
    differ in any measured quantity do not.
    """
    adj = state.adjudicate()
    return _scrub({"bundle_id": state.spec.bundle_id,
                   "protocol_hash": state.spec.protocol_hash(),
                   "spec": state.spec.canonical(),
                   "results": state.results,
                   "complete": state.is_complete(),
                   "adjudication": adj})


def content_bytes(state):
    return json.dumps(scientific_content(state), sort_keys=True, default=str).encode("ascii")


def default_rule(spec, results):
    """Treatment against its best control, on the P-3 fields.

    P-3 keeps `crossed_ever` (historical) apart from `crossed_at_final` (final state).
    This rule uses the final-state pair for the verdict and reports the historical one
    beside it, never as a substitute - mixing them is exactly defect Z80A-D01.
    """
    treat = [a for a in spec.arms if a.role == "TREATMENT"][0]
    ctrls = [a for a in spec.arms if a.role == "CONTROL"]
    tr = results[treat.name]
    t_final = tr.get("held_max_final") or 0.0
    t_ever = tr.get("held_max_ever") or 0.0
    c_final = max([(results[a.name].get("held_max_final") or 0.0) for a in ctrls], default=0.0)
    margin = round(t_final - c_final, 4)
    nums = {"treatment_held_final": t_final, "treatment_held_ever": t_ever,
            "control_held_final": c_final, "margin": margin,
            "treatment_crossed_ever": bool(tr.get("crossed_ever")),
            "treatment_crossed_at_final": bool(tr.get("crossed_at_final"))}
    if not tr.get("crossed_at_final"):
        if tr.get("crossed_ever"):
            v, why = "WEAK", "crossed historically but not at final state (P-3 separation)"
        else:
            v, why = "INADMISSIBLE", "the treatment never reached the threshold"
    elif margin < 0:
        v, why = "INADMISSIBLE", "the control finished ahead of the treatment"
    elif margin < MARGIN:
        v, why = "WEAK", "margin below %.2f: the control is not separated" % MARGIN
    else:
        v, why = "ADMISSIBLE", "at threshold at final state, control below it, margin >= %.2f" % MARGIN
    return {"bundle_id": spec.bundle_id, "hypothesis_id": spec.hypothesis_id,
            "verdict": v, "why": why, "numbers": nums}


class BundleStore:
    """One JSON file per bundle, written atomically, rebuildable from disk alone."""

    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, bundle_id):
        return self.root / ("%s.json" % bundle_id)

    def put(self, state):
        """Atomic: a kill mid-write leaves the previous file intact, never a torn one."""
        p = self.path_for(state.spec.bundle_id)
        payload = json.dumps(state.to_dict(), sort_keys=True, indent=1,
                             ensure_ascii=True, default=str)
        fd, tmp = tempfile.mkstemp(dir=str(self.root), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="ascii") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, p)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        return p

    def get(self, bundle_id):
        p = self.path_for(bundle_id)
        if not p.exists():
            return None
        return BundleState.from_dict(json.loads(p.read_text(encoding="ascii")))

    def open(self, spec):
        """The resume entry point: whatever is on disk for this spec, else a fresh state.

        Because `bundle_id` is content-addressed, a restarted process computing the same
        spec finds the same file without needing to have remembered anything.
        """
        return self.get(spec.bundle_id) or BundleState(spec)

    def all_ids(self):
        return sorted(p.stem for p in self.root.glob("*.json"))

    def complete_bundles(self):
        out = []
        for bid in self.all_ids():
            st = self.get(bid)
            if st is not None and st.is_complete():
                out.append(st)
        return out
