"""Eos intake gate -- the terminal-state mechanism (EOS-01 ACTIVE, 2026-09-11).

The old scorer read the ITEM and nothing else: it added points for substrings
and called the sum relevance. Nothing about that number could be checked, so
nothing about it could be wrong. This module replaces the number with a
CLAIM that has to resolve against the repository or against a measurement
this seat made itself.

Terminal states, as ruled by the operator:

    ANCHOR    exposes a weakness, blind spot or calibration opportunity in
              the CURRENT substrate
    ACQUIRE   a primitive, benchmark, environment, instrument, dataset,
              technique or mechanism worth absorbing into infrastructure
    RESOURCE  measured usable compute, API capacity, tooling or other
              external capability
    REFUSED   rejected, with the reason preserved

THE GATE CAN ONLY REFUSE. It assigns NO terminal state except REFUSED.
Admission is a human act (base role s2). An item that survives every check
leaves the gate as PENDING_ADMISSION and waits for a person.

RESOURCE USED TO BE THE ONE EXCEPTION and the exception was wrong. The
docstring here used to say the gate could settle it "because its evidence is
a measurement this seat took". Nemesis (NEMESIS-01, 2026-09-11) showed that
the evidence the measurement was taken is the string
`observed_by == "eos-intake"` carried in the claim, and settled 30 of 30
fabricated observations pointing at a host that was never called. That is
the base role's first rule -- verify the property, never the label -- failing
inside a gate built to enforce it. The exception is removed rather than
patched: an observation is now read from a committed probe ARTIFACT on disk,
and even then the state is PENDING_ADMISSION, because certifying external
capacity is not something this seat may do alone.

WHAT THE GATE DOES NOT DO, stated here so no reader has to discover it:
it verifies that a referent EXISTS, not that the referent is the RIGHT one.
A claim naming a real file and a real token in it passes even when the item
has nothing to do with either. That hole is measured, not hidden -- see the
CHEAT control in agents/eos/tests/test_intake.py and the numbers in
roles/Eos/CALIBRATION.md. The gate's contribution is that it converts an
unfalsifiable score into a claim a human can check in one command; closing
the semantic gap is the human admission step, not more machinery.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[3]

#: The four terminal states the operator ruled, plus the waiting room.
TERMINALS = ("ANCHOR", "ACQUIRE", "RESOURCE", "REFUSED")
PENDING = "PENDING_ADMISSION"
#: Not a terminal state and not a refusal: the gate could not decide because
#: one of its own instruments did not answer. Kept separate so instrument
#: error is never banked as a fact about the world (the program's standing
#: rule; the first season produced one of these and it would otherwise have
#: been reported as a refusal on evidence).
INDETERMINATE = "INDETERMINATE"
#: Also not a terminal state and NOT a refusal: the claim handed to the gate
#: never named a real place, because nothing tried to find one. Nemesis
#: (NEMESIS-01b, 2026-09-11) measured that 49 of the first season's 51
#: "refusals" were of this kind -- an auto-generated referent pointing into a
#: directory that has never existed -- and were banked as 49 decisions about
#: the frontier. They were decisions about a claim constructor. A refusal
#: that would be identical whatever the item said is not evidence about the
#: item, and calling it one is the same error as banking instrument failure.
NOT_EXAMINED = "NOT_EXAMINED"
#: Claims whose proposer marks them auto-generated are eligible for it.
AUTO_PROPOSER_MARKERS = ("auto", "constructor", "generated")

#: A RESOURCE observation older than this is not evidence of capacity, it is
#: a claim about a day in the past (charter constraint 7, decay windows).
RESOURCE_DECAY_DAYS = 30

#: Only this seat's own probes satisfy a RESOURCE claim. A provider's pricing
#: page is a label; base role: verify the property, never the label.
OBSERVER = "eos-intake"

#: Words that are not admissible as a reason for anything (operator ruling).
INADMISSIBLE_RATIONALE = (
    "interesting", "relevant", "promising", "exciting", "cutting edge",
    "cutting-edge", "state of the art", "state-of-the-art", "sota",
    "novel", "groundbreaking", "breakthrough", "must read", "must-read",
    "worth watching", "game changer", "game-changing", "impressive",
)


@dataclass
class Item:
    """One surfaced thing. Provenance is mandatory: an item with no source
    and no fetch time cannot be re-checked later, so it cannot be evidence."""
    id: str
    title: str
    source: str
    url: str = ""
    abstract: str = ""
    fetched_at: str = ""
    provenance: str = ""

    def text(self) -> str:
        return "{} {}".format(self.title, self.abstract)


@dataclass
class Claim:
    """A PROPOSAL that an item deserves a terminal state. Whoever or whatever
    writes this -- a person, a model, a script -- is proposing, not deciding.

    referent           "<repo-relative path>#<token>" for ANCHOR
    falsifier          what result would show the anchor was useless
    destination        repo-relative path an ACQUIRE would land at
    capability_markers symbols/packages proving the program lacks it already
    consumer           repo-relative path of the lane that would use it
    observation        a measurement record for RESOURCE
    """
    sought: str
    rationale: str = ""
    referent: str = ""
    falsifier: str = ""
    destination: str = ""
    capability_markers: List[str] = field(default_factory=list)
    consumer: str = ""
    #: RETAINED FOR THE RECORD ONLY. Never trusted since NEMESIS-01: a caller
    #: can write anything here, including observed_by="eos-intake".
    observation: Dict[str, Any] = field(default_factory=dict)
    #: "<repo-relative probe artifact>#<record index>". The gate opens this
    #: file itself; this is the only thing a RESOURCE claim is believed on.
    observation_ref: str = ""
    proposed_by: str = "unattributed"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""
    #: True when the check DID NOT ANSWER (the instrument failed, timed out,
    #: or had nothing to read). An indeterminate check is not a failed check:
    #: it must never be recorded as evidence about the item. "Nothing fired"
    #: and "nothing could have fired" are different facts (base s2).
    indeterminate: bool = False


@dataclass
class Verdict:
    item_id: str
    state: str
    reason: str
    sought: str
    checks: List[Check] = field(default_factory=list)
    claim: Optional[Claim] = None

    @property
    def refused(self) -> bool:
        return self.state == "REFUSED"

    def to_row(self) -> Dict[str, Any]:
        d = asdict(self)
        d["checks"] = [asdict(c) for c in self.checks]
        if self.claim is not None:
            d["claim"] = asdict(self.claim)
        return d


# ---------------------------------------------------------------------------
# Predicates. Each answers one question and says what it looked at.
# ---------------------------------------------------------------------------

def _repo_path(rel: str) -> Optional[Path]:
    """Resolve a repo-relative path, refusing anything that escapes the tree."""
    if not rel:
        return None
    try:
        p = (REPO / rel).resolve()
    except (OSError, ValueError):
        return None
    try:
        p.relative_to(REPO.resolve())
    except ValueError:
        return None
    return p


def check_rationale_admissible(claim: Claim) -> Check:
    """'Interesting', 'relevant', 'promising' and model enthusiasm are not
    admissible terminal reasons (operator ruling 2026-09-11)."""
    r = (claim.rationale or "").strip()
    if not r:
        return Check("rationale_present", False, "no rationale given")
    low = r.lower()
    hits = sorted({w for w in INADMISSIBLE_RATIONALE if w in low})
    if hits:
        return Check("rationale_admissible", False,
                     "rationale rests on inadmissible words: {}".format(", ".join(hits)))
    return Check("rationale_admissible", True, "{} chars, no inadmissible words".format(len(r)))


def check_provenance(item: Item) -> Check:
    if not item.source or not item.fetched_at:
        return Check("provenance", False, "item lacks source or fetched_at; it cannot be re-checked")
    return Check("provenance", True, "{} at {}".format(item.source, item.fetched_at))


def check_referent_resolves(claim: Claim) -> Check:
    """ANCHOR: '<path>#<token>' must name a real file containing a real token.

    This is the check the old scorer had no equivalent of. A claim that
    cannot name a place in this repository that the item bears on is not a
    claim about this program.
    """
    ref = (claim.referent or "").strip()
    if "#" not in ref:
        return Check("referent_form", False,
                     "referent must be '<repo-relative path>#<token>', got {!r}".format(ref))
    rel, token = ref.split("#", 1)
    p = _repo_path(rel.strip())
    if p is None or not p.is_file():
        return Check("referent_resolves", False, "no such file in the repository: {}".format(rel))
    token = token.strip()
    if not token:
        return Check("referent_resolves", False, "empty token after '#'")
    try:
        body = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return Check("referent_resolves", False, "unreadable: {}".format(e))
    if token not in body:
        return Check("referent_resolves", False,
                     "token {!r} does not occur in {}".format(token, rel))
    return Check("referent_resolves", True, "{} contains {!r}".format(rel, token))


def check_not_already_absorbed(item: Item, claim: Claim) -> Check:
    """If the referent file already cites the item, the program has it; an
    item cannot expose a weakness in a file that already accounts for it."""
    ref = (claim.referent or "")
    if "#" not in ref:
        return Check("not_already_absorbed", False, "no referent to check")
    rel = ref.split("#", 1)[0].strip()
    p = _repo_path(rel)
    if p is None or not p.is_file():
        return Check("not_already_absorbed", False, "no such file: {}".format(rel))
    body = p.read_text(encoding="utf-8", errors="replace")
    for needle in (item.url, item.id):
        if needle and needle in body:
            return Check("not_already_absorbed", False,
                         "{} already cites {}".format(rel, needle))
    return Check("not_already_absorbed", True, "{} does not yet cite this item".format(rel))


def check_falsifier(claim: Claim) -> Check:
    """An anchor with no way to be useless is not an anchor, it is a hope.
    Presence is checkable here; adequacy is the human admitter's job."""
    f = (claim.falsifier or "").strip()
    if len(f) < 20:
        return Check("falsifier", False,
                     "no falsifier, or too short to name a result ({} chars)".format(len(f)))
    return Check("falsifier", True, "{} chars".format(len(f)))


#: Paths the dedup search MUST NOT read. Eos's own intake artifacts quote
#: every item they record, so a search over the whole tree finds an item in
#: Eos's own ledger and concludes the program already has it. Measured on the
#: first season: "Microcosmos" returned 2 hits, both of them this seat's probe
#: and sample files. An instrument whose output contaminates its next input is
#: not measuring the program, it is measuring itself.
#: Found again on the re-run, one level deeper: after excluding this seat's
#: records the search STILL reported a hit, and the hit was this module --
#: the comment above documents the defect by naming a real item, so the
#: documentation of the contamination contaminated the instrument. The rule
#: that survives both rounds is simpler than either patch: the dedup search
#: asks what THE PROGRAM has, and Eos is not the program. Everything this
#: seat writes -- its records, its archive AND its own source -- is excluded.
SELF_PATHS = (":(exclude)roles/Eos/", ":(exclude)agents/eos/")

#: git grep over this tree is slow (measured 2026-09-11: >120 s for one
#: literal over 39,284 files). The budget is generous and a timeout is
#: reported as INDETERMINATE, never as absence.
GREP_TIMEOUT_S = 240


def _git_grep_count(marker: str, timeout: int = GREP_TIMEOUT_S) -> int:
    """Files in the TRACKED tree containing `marker`, excluding this seat's own
    intake artifacts. Returns -1 for INDETERMINATE (the search did not answer)."""
    try:
        # --cached searches the INDEX, not the working tree. Nemesis measured
        # 43 vs 97 files for one literal in a sparse worktree -- the gate was
        # reporting "0 hits in the tracked tree" after searching 44 per cent
        # of it. It is also markedly faster.
        r = subprocess.run(["git", "grep", "--cached", "-l", "-F", "--", marker, *SELF_PATHS],
                           cwd=str(REPO), capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return -1
    if r.returncode not in (0, 1):
        return -1
    return len([l for l in r.stdout.splitlines() if l.strip()])


def check_capability_absent(claim: Claim) -> Check:
    """ACQUIRE: the program must not already have the thing. Every marker is
    searched over the TRACKED tree minus this seat's own records; one hit is
    enough to refuse.

    A search that does not answer yields INDETERMINATE, which is NOT absence
    and NOT presence. "Nothing was found" and "nothing could have been found"
    are different facts (base s2) and this check never merges them.
    """
    markers = [m for m in (claim.capability_markers or []) if m and m.strip()]
    if not markers:
        return Check("capability_absent", False,
                     "no capability markers given; absence cannot be established")
    present, unknown = [], []
    for m in markers:
        n = _git_grep_count(m)
        if n < 0:
            unknown.append(m)
        elif n > 0:
            present.append("{} ({} files)".format(m, n))
    if unknown:
        return Check("capability_absent", False,
                     "INSTRUMENT: search did not answer for {} within {} s -- "
                     "INDETERMINATE, not absent".format(", ".join(unknown), GREP_TIMEOUT_S),
                     indeterminate=True)
    if present:
        return Check("capability_absent", False,
                     "the program already has: {}".format("; ".join(present)))
    return Check("capability_absent", True,
                 "{} markers, 0 hits in the tracked tree (excluding this seat's own records)"
                 .format(len(markers)))


def check_destination(claim: Claim) -> Check:
    d = (claim.destination or "").strip()
    if not d:
        return Check("destination", False, "no destination path given")
    p = _repo_path(d)
    if p is None:
        return Check("destination", False, "destination escapes the repository: {}".format(d))
    if not p.parent.is_dir():
        return Check("destination", False, "parent directory does not exist: {}".format(d))
    return Check("destination", True, "parent of {} exists".format(d))


def check_consumer(claim: Claim) -> Check:
    """Absorbing something nothing will use is how this program accumulated
    2,200 artifacts with 0 consumers. Name the lane or be refused."""
    c = (claim.consumer or "").strip()
    if not c:
        return Check("consumer", False, "no consumer named")
    p = _repo_path(c)
    if p is None or not p.exists():
        return Check("consumer", False, "named consumer does not exist: {}".format(c))
    return Check("consumer", True, "consumer exists: {}".format(c))


def check_observation(claim: Claim, now: Optional[datetime] = None) -> Check:
    """RESOURCE: the observation must be READ FROM A COMMITTED PROBE ARTIFACT,
    not asserted in the claim.

    The claim supplies `observation_ref` = "<repo-relative probe artifact>#<n>",
    naming the artifact and the index of the record inside it. The gate opens
    that file itself. A proposer can still commit a fabricated artifact, but
    it is then a file in the repository with a diff and an author, which is a
    different thing from a string nobody can see.

    Before NEMESIS-01 this check read `claim.observation` directly and
    accepted `observed_by == "eos-intake"` as proof that a call happened. 30
    of 30 fabricated observations passed. The lesson is the base role's own:
    a field a caller writes is a label, not the property.
    """
    now = now or datetime.now(timezone.utc)
    ref = (claim.observation_ref or "").strip()
    if "#" not in ref:
        return Check("observation_ref_form", False,
                     "RESOURCE needs observation_ref '<probe artifact path>#<record index>'; "
                     "a self-asserted observation dict is no longer accepted (NEMESIS-01)")
    rel, _, idx = ref.partition("#")
    p = _repo_path(rel.strip())
    if p is None or not p.is_file():
        return Check("observation_artifact_exists", False,
                     "no probe artifact at {}".format(rel))
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
        rec = payload["records"][int(idx)]
    except (ValueError, KeyError, IndexError, TypeError) as e:
        return Check("observation_artifact_readable", False,
                     "cannot read record {} of {}: {}".format(idx, rel, type(e).__name__))
    if payload.get("observer") != OBSERVER:
        return Check("observation_artifact_is_ours", False,
                     "artifact observer is {!r}, not {!r}".format(payload.get("observer"), OBSERVER))
    missing = [k for k in ("endpoint", "observed_at", "status") if not rec.get(k)]
    if missing:
        return Check("observation_complete", False, "record missing: {}".format(", ".join(missing)))
    # Something only a real request produces. A fabricated record can carry
    # these too, but it has to carry them, and they are on disk to be read.
    if not isinstance(rec.get("latency_ms"), int) or rec.get("bytes") in (None, 0):
        return Check("observation_response_derived", False,
                     "record carries no response-derived evidence (latency_ms and bytes); "
                     "a status code alone can be typed by anyone")
    try:
        ts = datetime.fromisoformat(str(rec["observed_at"]).replace("Z", "+00:00"))
    except ValueError:
        return Check("observation_fresh", False, "unparseable observed_at")
    if ts.tzinfo is None:
        return Check("observation_fresh", False, "observed_at has no timezone")
    age = now - ts
    if age > timedelta(days=RESOURCE_DECAY_DAYS):
        return Check("observation_fresh", False,
                     "measurement is {} days old, decay window is {}".format(age.days, RESOURCE_DECAY_DAYS))
    if age < timedelta(0):
        return Check("observation_fresh", False, "observed_at is in the future")
    return Check("observation_fresh", True,
                 "{} at {} ({} d old), status={}, {} bytes in {} ms, from committed artifact {}"
                 .format(rec["endpoint"], rec["observed_at"], age.days, rec["status"],
                         rec.get("bytes"), rec.get("latency_ms"), rel))


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------

CHECKS_BY_TYPE = {
    "ANCHOR": ("provenance", "rationale", "referent", "not_absorbed", "falsifier"),
    "ACQUIRE": ("provenance", "rationale", "capability_absent", "destination", "consumer"),
    "RESOURCE": ("provenance", "rationale", "observation"),
}


def classify(item: Item, claim: Claim, now: Optional[datetime] = None) -> Verdict:
    """Run every check the sought state requires. Any failure is REFUSED.

    Returns PENDING_ADMISSION for a surviving ANCHOR or ACQUIRE -- the gate
    does not admit. Returns RESOURCE for a surviving resource claim, which is
    settled by measurement rather than judgement.
    """
    sought = (claim.sought or "").upper().strip()
    if sought == "REFUSED":
        return Verdict(item.id, "REFUSED", claim.rationale or "refused on proposal", sought,
                       [Check("proposed_refusal", True, "refused by the proposer")], claim)
    if sought not in CHECKS_BY_TYPE:
        return Verdict(item.id, "REFUSED",
                       "sought state {!r} is not one of {}".format(sought, TERMINALS),
                       sought, [Check("sought_valid", False, repr(sought))], claim)

    runners = {
        "provenance": lambda: check_provenance(item),
        "rationale": lambda: check_rationale_admissible(claim),
        "referent": lambda: check_referent_resolves(claim),
        "not_absorbed": lambda: check_not_already_absorbed(item, claim),
        "falsifier": lambda: check_falsifier(claim),
        "capability_absent": lambda: check_capability_absent(claim),
        "destination": lambda: check_destination(claim),
        "consumer": lambda: check_consumer(claim),
        "observation": lambda: check_observation(claim, now),
    }
    checks = [runners[name]() for name in CHECKS_BY_TYPE[sought]]
    undecided = [c for c in checks if c.indeterminate]
    if undecided:
        # An instrument that did not answer cannot refuse anything. The item
        # goes back in the queue with the instrument named, and the seat owes
        # a fix -- not a verdict.
        return Verdict(item.id, INDETERMINATE,
                       "; ".join("{}: {}".format(c.name, c.detail) for c in undecided),
                       sought, checks, claim)
    failed = [c for c in checks if not c.passed]
    auto = any(m in (claim.proposed_by or "").lower() for m in AUTO_PROPOSER_MARKERS)
    if auto and failed and all(c.name in ("referent_resolves", "referent_form",
                                          "not_already_absorbed") for c in failed):
        return Verdict(item.id, NOT_EXAMINED,
                       "the claim's referent was auto-generated and names no real place, so this "
                       "verdict would be identical whatever the item said: " +
                       "; ".join("{}: {}".format(c.name, c.detail) for c in failed),
                       sought, checks, claim)
    if failed:
        return Verdict(item.id, "REFUSED",
                       "; ".join("{}: {}".format(c.name, c.detail) for c in failed),
                       sought, checks, claim)
    return Verdict(item.id, PENDING,
                   "every check passed; {} requires human admission (the gate settles no "
                   "terminal state but REFUSED)".format(sought),
                   sought, checks, claim)


def season(pairs: Sequence[Any], now: Optional[datetime] = None) -> List[Verdict]:
    return [classify(i, c, now) for i, c in pairs]


def summarise(verdicts: Sequence[Verdict]) -> Dict[str, int]:
    out = {k: 0 for k in ("ANCHOR", "ACQUIRE", "RESOURCE", "REFUSED", PENDING,
                          INDETERMINATE, NOT_EXAMINED)}
    for v in verdicts:
        out[v.state] = out.get(v.state, 0) + 1
    return out


def write_ledger(verdicts: Sequence[Verdict], path: Path, note: str = "") -> Path:
    """Every verdict, refusals included. The refusal corpus is the record of
    the boundary Prometheus chose not to cross (operator ruling)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "written_at": datetime.now(timezone.utc).isoformat(),
        "note": note,
        "counts": summarise(verdicts),
        "verdicts": [v.to_row() for v in verdicts],
    }
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.flush()
    return path
