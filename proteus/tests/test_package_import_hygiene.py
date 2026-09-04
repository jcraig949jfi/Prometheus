"""Enforce the no-forbidden-imports property across the WHOLE proteus package.

WHY THIS EXISTS. `proteus/contracts/SFE_INTEGRATION.md` states that "the quarantine audit forbids
any network import in proteus/". That was an OVER-CLAIM: `quarantine.py` scopes its import
allowlist to `proteus/foundry` only (see its FOUNDRY constant), so every other subpackage --
including `proteus/integration`, which is precisely what Harmonia imports -- was unenforced. The
property happened to hold; nothing checked it. A property enforced by nobody is a property that
will quietly stop holding.

This test closes that gap WITHOUT touching `quarantine.py` or `audit_identity.py`, both of which
are inside the V0.6 audit identity: adding to them would force an audit transition, and this is a
new check rather than a change to the audited runtime. The forbidden vocabulary is IMPORTED from
quarantine so there is no second source of truth.

EXEMPTIONS ARE RECORDED, NOT HIDDEN. Two files currently import something on the forbidden list.
Both are listed below with a reason. One of them is a genuine defect, and it is written down as a
defect rather than blessed.
"""
from __future__ import annotations

import ast
import os

from proteus.audits.quarantine import FORBIDDEN_ANYWHERE, _imports

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG = os.path.join(ROOT, "proteus")

#: (relative path, module) -> why it is tolerated. Anything not listed here is a hard failure.
EXEMPTIONS = {
    ("proteus/audits/audit_identity.py", "subprocess"): (
        "LEGITIMATE. The auditor shells out to git to record repository identity alongside the "
        "audit stamp. It is tooling that inspects the tree; it is not player-facing, is never "
        "imported by vm.py, generate.py or any runtime path, and cannot execute inside a player."),
    ("proteus/tests/test_pre_t1_gates.py", "subprocess"): (
        "LEGITIMATE, same class as the auditor above. Gate G4 must distinguish TRACKED files from "
        "files merely present on disk, which only git can answer, and .pyc files regenerate "
        "constantly so a filesystem check would be meaningless. Test-only, never imported by any "
        "runtime or consumer path."),
    ("proteus/v0_6/equilibrium.py", "random"): (
        "RECORDED DEFECT, not an endorsement. equilibrium.py imports the stdlib `random` and uses "
        "random.Random(seed) in stationary_empirical() only. Proteus policy is that `random` is "
        "used NOWHERE, because its float and choice paths are not something we want to depend on "
        "for bit-exact replay -- SplitMix64 exists for exactly this reason. BLAST RADIUS, "
        "measured: stationary_empirical is called from two places in v0_6/run_full.py, feeding "
        "(a) the empirical-occupancy cross-check and (b) the matched-trajectory arm. Both were "
        "reported in the V0.6 packet as NON-ADJUDICATED -- the empirical arm is an external check "
        "by preregistration, and the trajectory arm was explicitly discounted as under-converged. "
        "The numerical replay contract calls stationary_power and NEVER stationary_empirical, so "
        "the cross-runtime byte-identity result is unaffected. No adjudicated V0.6 number depends "
        "on this import. It should be replaced with SplitMix64, which would change those two "
        "non-adjudicated numbers and therefore belongs in a pass authorised to re-run them."),
}


def _scan():
    hits = []
    for dirpath, dirnames, filenames in os.walk(PKG):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for mod, line in _imports(tree):
                if mod in FORBIDDEN_ANYWHERE:
                    hits.append((rel, mod, line))
    return hits


def test_no_unexempted_forbidden_imports_anywhere_in_proteus():
    unexpected = [(rel, mod, line) for rel, mod, line in _scan()
                  if (rel, mod) not in EXEMPTIONS]
    assert not unexpected, (
        "forbidden import(s) outside the recorded exemption list: "
        + "; ".join(f"{r}:{n} imports {m}" for r, m, n in unexpected))


def test_the_consumer_facing_package_is_clean():
    """proteus/integration is what Harmonia imports. It must have NO exemptions at all."""
    hits = [(rel, mod, line) for rel, mod, line in _scan()
            if rel.startswith("proteus/integration/")]
    assert not hits, f"the consumer-facing package must stay clean, found: {hits}"


def test_every_exemption_is_still_real():
    """A stale exemption is a lie. If a defect gets fixed, this fails until the entry is removed."""
    live = {(rel, mod) for rel, mod, _ in _scan()}
    stale = sorted(set(EXEMPTIONS) - live)
    assert not stale, (f"exemption(s) recorded for imports that no longer exist: {stale}. "
                       f"Remove the entry rather than leaving a false record.")


def test_exemptions_carry_reasons():
    for key, reason in EXEMPTIONS.items():
        assert isinstance(reason, str) and len(reason) > 80, f"{key} needs a real reason"
