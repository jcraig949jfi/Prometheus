"""WTP-LM01 launch gate + campaign/replication seed derivation.

AUTHORITY (operator ruling 2026-09-26 item 6, roles/Ensorain/prompts/2026-09-26_lm01_operator_rulings/): OPERATOR ONLY,
in direct chat. Aporia and Cyclops are removed from the launch-authority set; no second seat approves.
The operator's instruction is recorded VERBATIM as a committed prompt file with a verifying MANIFEST
(roles/Ensorain/prompts/<date>_lm01_launch/01_OPERATOR_LAUNCH_verbatim.md). It passes only if it contains
    LAUNCH WTP-LM01 using frozen prereg <hash>
where <hash> is hex (7-40 characters) and is a prefix of the FROZEN PREREG COMMIT SHA (the commit that froze
ensorain/PREREG_WTP_LM01.md; recorded in ensorain/lm01/FREEZE.json). A directive without the matching hash never launches.
Placeholder text such as "<hash>" fails, because it is not hex.
Seeds are derived only through campaign_seeds(directive_path, ...), which re-verifies the file, its MANIFEST and the hash.
The former comms-message gate (#699 pattern, RELEASERS) is RETIRED; the old checks are kept only as negative controls."""
import hashlib
import os
import re
import subprocess

PATTERN = re.compile(r"LAUNCH WTP-LM01 using frozen prereg ([0-9a-f]{7,40})\b")
CAMPAIGN_BASE, REPLICATION_BASE, SPAN = 10 ** 9, 2 * 10 ** 9, 4 * 10 ** 8   # disjoint by construction
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_operator_launch(text, freeze_commit):
    """True iff the text carries the exact instruction with a hash that is a prefix of the frozen prereg commit."""
    if not freeze_commit or not re.fullmatch(r"[0-9a-f]{40}", freeze_commit):
        return False
    hits = PATTERN.findall(text or "")
    return len(hits) >= 1 and all(freeze_commit.startswith(h) for h in hits)


def _verify_recorded(path):
    """The directive must be a committed file whose MANIFEST in the same directory verifies (LF-normalised sha256)."""
    from comms import manifest
    d = os.path.dirname(os.path.abspath(path))
    n, bad = manifest.verify(__import__("pathlib").Path(d))
    if bad:
        raise PermissionError(f"LM01: launch directive MANIFEST mismatch: {bad}")
    tracked = subprocess.run(["git", "-C", REPO, "ls-files", "--error-unmatch", os.path.relpath(path, REPO)],
                             capture_output=True).returncode == 0
    if not tracked:
        raise PermissionError("LM01: launch directive file is not committed")


def _seed(tag, freeze_commit, stratum, i, base):
    h = int(hashlib.sha256(f"{freeze_commit}|{tag}|{stratum}|{i}".encode()).hexdigest()[:12], 16) % SPAN
    return base + h


def campaign_seeds(directive_path, freeze_commit, strata, n):
    """Materialises campaign seeds ONLY after a recorded, verifying operator directive with the matching hash."""
    _verify_recorded(directive_path)
    text = open(directive_path, encoding="utf-8").read()
    if not is_operator_launch(text, freeze_commit):
        raise PermissionError("LM01: the directive lacks 'LAUNCH WTP-LM01 using frozen prereg <matching hash>'; closed")
    out = {s: [_seed("LM01-campaign", freeze_commit, s, i, CAMPAIGN_BASE) for i in range(n)] for s in strata}
    flat = [x for v in out.values() for x in v]
    if len(set(flat)) != len(flat):
        raise RuntimeError("LM01: campaign seed collision; the derivation must be amended before launch")
    return out


def replication_seeds(freeze_commit, stratum, n):
    """Held-out block (s6.7/s9). Called only for a firing stratum, after the campaign verdict is computed."""
    return [_seed("LM01-replication", freeze_commit, stratum, i, REPLICATION_BASE) for i in range(n)]


def negative_control_texts(freeze_commit):
    """Texts that MUST NOT pass. Includes the operator's own ruling text (placeholder '<hash>' and 'Do not launch')."""
    rulings = os.path.join(REPO, "roles", "Ensorain", "prompts", "2026-09-26_lm01_operator_rulings",
                           "01_OPERATOR_LM01_RULINGS_verbatim.md")
    wrong = "0" * 40 if not freeze_commit.startswith("0") else "f" * 40
    return {
        "operator_rulings_2026-09-26": open(rulings, encoding="utf-8").read() if os.path.exists(rulings) else "",
        "no_hash": "LAUNCH WTP-LM01 using frozen prereg",
        "placeholder": "LAUNCH WTP-LM01 using frozen prereg <hash>.",
        "wrong_hash": f"LAUNCH WTP-LM01 using frozen prereg {wrong[:12]}",
        "lowercase_token": f"launch wtp-lm01 using frozen prereg {freeze_commit[:12]}",
        "too_short_hash": f"LAUNCH WTP-LM01 using frozen prereg {freeze_commit[:6]}",
        "mixed_hashes": f"LAUNCH WTP-LM01 using frozen prereg {freeze_commit[:12]} / LAUNCH WTP-LM01 using frozen prereg {wrong[:12]}",
        "old_comms_token": f"WTP-LM01 LAUNCH: go {freeze_commit}",
    }
