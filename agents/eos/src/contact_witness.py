"""EOS-31 / Season II Mission 3: is there a deterministic CONTACT witness?

The gate currently checks that a referent EXISTS. The preregistered Test 4
attack showed that existence can launder an unrelated claim. The operator
asked whether the repository already contains stronger, machine-checkable
relationship evidence -- import/call edges, opcodes, schema ownership,
backlog identifiers, test ownership, producer/consumer edges, file/token
references, provenance links -- and explicitly forbade closing the hole
with embeddings, an LLM relevance score, or another phrase list.

This module MEASURES candidate witnesses. It does not change the gate and
is not wired into it. Under the operator's directive Eos may not optimise
against the six live examples before the independent attackers answer.

THE WITNESSES SPLIT INTO TWO KINDS, and the split is the result:

  REFERENT-SIDE  a function of the internal referent alone
                 (specificity, inbound edges, ownership, liveness)
  PAIR-SIDE      a function of (external object, internal referent)

Only a PAIR-SIDE witness can possibly separate a true claim from a
laundered one, because a laundered claim names a perfectly good referent.
Proof by the sample Eos already has: the Test 4 bait and live item 5 name
THE SAME referent. Every referent-side witness is identical for them by
construction. No amount of referent-side evidence can tell them apart.

The repository contains exactly one deterministic pair-side witness: does
it already reference the external object (arXiv id, DOI, URL, title)?
That detects DUPLICATION, not contact. Contact would require an edge from
a repository object to an external object, and the repository has none
except citations of things it has already metabolised.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[3]

#: Path prefixes that mean "this is not live": archived, superseded,
#: vendored, or a dated record rather than a working object.
DEAD_PREFIXES = ("archive/", "/archive/", "/v1/", "pivot/")


def _git(*args: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True,
                          text=True, timeout=timeout)


def _count_files_containing(literal: str, *pathspecs: str) -> int:
    """Tracked files containing `literal`. -1 means the search did not
    answer -- INDETERMINATE, never 0."""
    r = _git("grep", "-l", "-F", "--", literal, *pathspecs)
    if r.returncode not in (0, 1):
        return -1
    return len([l for l in r.stdout.splitlines() if l.strip()])


# ---------------------------------------------------------------------------
# Referent-side witnesses
# ---------------------------------------------------------------------------

@dataclass
class ReferentWitness:
    referent: str
    path: str
    token: str
    exists: bool
    #: W1 how many tracked files contain the token. A token in 500 files is
    #: a word, not a referent.
    token_specificity: int
    #: W2 how many tracked files name the referent FILE. Zero inbound
    #: references means nothing depends on the place the item would change.
    inbound_references: int
    #: W3 the seat that owns the path, by prefix. No owner means the
    #: interruption cannot be delivered to anyone.
    owner: Optional[str]
    #: W4 liveness: last commit date of the file, and whether its path
    #: marks it archived or superseded.
    last_commit: str
    looks_archived: bool


def _owner_of(path: str) -> Optional[str]:
    parts = path.split("/")
    if parts[0] == "roles" and len(parts) > 1:
        return parts[1]
    if parts[0] == "agents" and len(parts) > 1:
        return parts[1]
    known = {"apollo": "Apollo", "vivarium": "Vivarium", "harmonia": "Harmonia",
             "ergon": "Ergon", "charon": "Charon", "techne": "Techne",
             "archaeon": "Archaeon", "aporia": "Aporia", "forge": "Hephaestus",
             "evidence_wiki": "Mnemosyne", "comms": "Archaeon"}
    return known.get(parts[0])


def referent_witness(referent: str) -> ReferentWitness:
    path, _, token = referent.partition("#")
    p = REPO / path
    exists = p.is_file() and token and token in p.read_text(encoding="utf-8", errors="replace")
    last = _git("log", "-1", "--format=%ad", "--date=short", "--", path).stdout.strip()
    return ReferentWitness(
        referent=referent, path=path, token=token, exists=bool(exists),
        token_specificity=_count_files_containing(token),
        inbound_references=_count_files_containing(path),
        owner=_owner_of(path),
        last_commit=last or "UNKNOWN",
        looks_archived=any(d in "/" + path for d in DEAD_PREFIXES),
    )


# ---------------------------------------------------------------------------
# The only pair-side witness the repository can supply
# ---------------------------------------------------------------------------

@dataclass
class PairWitness:
    item_id: str
    referent: str
    #: Does the repository ALREADY cite this external object? Detects
    #: duplication (already metabolised), not contact.
    already_cited_files: int
    already_cited_where: List[str]
    #: Does the referent FILE itself cite it? The strongest form: the place
    #: the item claims to bear on already knows about it.
    cited_by_the_referent_itself: bool


def pair_witness(item_id: str, referent: str, identifiers: List[str],
                 exclude: tuple = (":(exclude)roles/Eos/", ":(exclude)agents/eos/")) -> PairWitness:
    path = referent.partition("#")[0]
    where: List[str] = []
    for ident in identifiers:
        if not ident:
            continue
        r = _git("grep", "-l", "-F", "--", ident, *exclude)
        if r.returncode == 0:
            where.extend(l.strip() for l in r.stdout.splitlines() if l.strip())
    where = sorted(set(where))
    p = REPO / path
    body = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
    return PairWitness(item_id=item_id, referent=referent,
                       already_cited_files=len(where), already_cited_where=where[:10],
                       cited_by_the_referent_itself=any(i and i in body for i in identifiers))


def main() -> int:
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from archaeon.workspace import assert_not_canonical
    ws = assert_not_canonical("the contact-witness measurement", allow_override=False)

    ledger = json.loads((REPO / "roles/Eos/intake/ledger_2026-09-11.json").read_text(encoding="utf-8"))
    sample = json.loads((REPO / "roles/Eos/intake/sample_2026-09-11.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in sample["POP_B"] + sample["POP_C"]}

    subjects = []
    for v in ledger["verdicts"]:
        if v["state"] == "PENDING_ADMISSION" and v.get("claim", {}).get("referent"):
            subjects.append((v["item_id"], v["claim"]["referent"]))
    # The Test 4 attack, added by hand because it is not in the season ledger.
    subjects.append(("bait-003-attack", "roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates"))

    refs: Dict[str, Any] = {}
    pairs = []
    for item_id, referent in subjects:
        if referent not in refs:
            refs[referent] = asdict(referent_witness(referent))
        row = by_id.get(item_id) or by_id.get(item_id.replace("-attack", ""))
        idents = []
        if row:
            url = row.get("url") or ""
            if url:
                idents.append(url)
                m = re.search(r"(\d{4}\.\d{4,5})", url)
                if m:
                    idents.append(m.group(1))
            idents.append(row.get("title", "")[:60])
        pairs.append(asdict(pair_witness(item_id, referent, idents)))

    out = {"measured_at": "2026-09-11", "workspace": ws,
           "note": ("Measurement only. The gate is UNCHANGED and no witness is wired into it. "
                    "Under the operator's Season II directive Eos may not optimise against the "
                    "six live examples before the independent attackers answer."),
           "referent_side": refs, "pair_side": pairs}
    p = REPO / "roles/Eos/intake/contact_witnesses_2026-09-11.json"
    with p.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2)
        fh.flush()

    print("REFERENT-SIDE WITNESSES")
    print("{:<58} {:>5} {:>6} {:>4} {:<12} {}".format(
        "referent", "spec", "inb", "ex", "last commit", "owner"))
    for r, w in refs.items():
        print("{:<58} {:>5} {:>6} {:>4} {:<12} {}".format(
            r[:58], w["token_specificity"], w["inbound_references"],
            "yes" if w["exists"] else "NO", w["last_commit"], w["owner"]))
    print()
    print("PAIR-SIDE WITNESS (already cited in the repository?)")
    for pw in pairs:
        print("  {:<28} cited in {} files; referent itself cites it: {}".format(
            pw["item_id"][:28], pw["already_cited_files"], pw["cited_by_the_referent_itself"]))
    print()
    print("wrote", p.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
