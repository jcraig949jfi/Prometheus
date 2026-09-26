"""WTP-LM01 launch gate + campaign/replication seed derivation (directive s12/s13; #699/#700 exact-token pattern; G1).

A campaign row may exist only after a comms message that passes is_release():
  - subject starts EXACTLY with TOKEN;
  - kind == "ruling";
  - sender is Cyclops (the M2 steward who issues the launch prompt, directive s12) or the operator seat;
  - "Ensorain" is among the recipients;
  - created_at is later than the prereg freeze commit time;
  - the prereg freeze SHA (the full 40 hex, or its first 9) appears in the body.
Seeds are derived only through campaign_seeds(), which refuses to run without a passing release message id.
NEGATIVE CONTROLS (#699): real past Cyclops messages containing "launch" (e.g. #592, #610, #698) must FAIL.
POSITIVE CONTROL: a synthetic well-formed dict must PASS. check_controls() runs both against the live DB."""
import hashlib
from datetime import datetime, timezone

TOKEN = "WTP-LM01 LAUNCH:"
RELEASERS = ("Cyclops", "operator")
CAMPAIGN_BASE, REPLICATION_BASE, SPAN = 10 ** 9, 2 * 10 ** 9, 4 * 10 ** 8   # disjoint by construction


def is_release(msg, freeze_sha, freeze_time):
    subj = msg.get("subject") or ""
    body = msg.get("body") or ""
    t = msg.get("created_at")
    if isinstance(t, str):
        t = datetime.fromisoformat(t)
    return (subj.startswith(TOKEN) and msg.get("kind") == "ruling"
            and (msg.get("sender") or "").split("[")[0] in RELEASERS
            and "Ensorain" in (msg.get("recipients") or [])
            and t is not None and t > freeze_time
            and (freeze_sha in body or freeze_sha[:9] in body))


def _fetch(ids):
    from comms import api
    c = api.connect()
    cur = c.cursor()
    cur.execute("select id, sender, recipients, kind, subject, body, created_at from " + api.schema()
                + ".messages where id = any(%s)", (list(ids),))
    return {r[0]: dict(id=r[0], sender=r[1], recipients=r[2], kind=r[3], subject=r[4], body=r[5], created_at=r[6])
            for r in cur.fetchall()}


def check_controls(freeze_sha, freeze_time, negative_ids=(592, 610, 698, 699, 701)):
    msgs = _fetch(negative_ids)
    neg = {i: is_release(m, freeze_sha, freeze_time) for i, m in msgs.items()}
    pos = is_release(dict(sender="Cyclops[m2-e8056938]", recipients=["Ensorain", "Aporia"], kind="ruling",
                          subject=TOKEN + " go", body=f"freeze {freeze_sha}",
                          created_at=datetime(2100, 1, 1, tzinfo=timezone.utc)), freeze_sha, freeze_time)
    return dict(negatives=neg, positive=pos, PASS=pos and not any(neg.values()) and len(msgs) == len(negative_ids))


def _seed(tag, freeze_sha, stratum, i, base):
    h = int(hashlib.sha256(f"{freeze_sha}|{tag}|{stratum}|{i}".encode()).hexdigest()[:12], 16) % SPAN
    return base + h


def campaign_seeds(release_id, freeze_sha, freeze_time, strata, n):
    """Materialises campaign seeds ONLY after a passing release message (checked against the live DB)."""
    m = _fetch([release_id]).get(release_id)
    if m is None or not is_release(m, freeze_sha, freeze_time):
        raise PermissionError(f"LM01: message #{release_id} is not a valid launch release; no campaign seed derived")
    out = {s: [_seed("LM01-campaign", freeze_sha, s, i, CAMPAIGN_BASE) for i in range(n)] for s in strata}
    flat = [x for v in out.values() for x in v]
    if len(set(flat)) != len(flat):
        raise RuntimeError("LM01: campaign seed collision; the derivation must be amended before launch")
    return out


def replication_seeds(freeze_sha, stratum, n):
    """Held-out block (s9). Called only for a firing stratum, after the campaign verdict is computed."""
    return [_seed("LM01-replication", freeze_sha, stratum, i, REPLICATION_BASE) for i in range(n)]
