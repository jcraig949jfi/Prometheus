"""Independent, offline Review 03 necessary-invariant oracle; NOT production.

Input is a bounded, ordered trace from ONE uninterrupted reaper invocation,
including failed/in-flight rounds, not policy samples or cached verdicts.
Times are numeric UTC epoch seconds and same-process monotonic seconds.
Each round has utc, mono, list_complete, list_owned_ids, get_results. LIST
IDs include every exact-owned positive (including TERMINATED); GET results
map requested ID to MISSING (completed ambiguous 404), RUNNING, TERMINATED,
CONFLICT, or a failure label. Omitted GET means NOT sampled, never MISSING.
Known ownership conflicts must not be hidden by the caller's classification.

known_ids is the caller's complete union of controller/reaper/discovered IDs.
last_local_event is the maximum relevant controller evidence UTC, or None.
The caller MUST obtain current_state_hash from actual authoritative durable
state under the appropriate lock, with the same hashing convention as the
supplied report. This pure function cannot find unseen state, authenticate a
directory, acquire authority, or detect a caller supplying two stale hashes.

True means only these bounded necessary checks permit confirmation. It is NOT
a seal or proof of cleanup: no ACK/absence-witness replay, journal durability,
identity authentication, billing, or future-invisibility claim is attempted.
In particular, MISSING is not a deletion acknowledgement or absence witness.
"""

from math import isfinite


def _finite(value):
    return type(value) in (int, float) and isfinite(value)


def _ids(value):
    return (type(value) in (list, tuple, set, frozenset)
            and len(value) <= 10000
            and all(type(pid) is str and pid.strip() for pid in value)
            and len(set(value)) == len(value))


def _hash(value):
    return (type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def permits_confirmation(rounds, *, known_ids, horizon, cutoff, last_local_event,
                         supplied_state_hash, current_state_hash, now_utc):
    """Return bool, fail closed on malformed input; never read disk or mutate.

    Qualify only the healthy suffix after the last bad round or clock/gap
    boundary. The independent spec bounds are 60s gaps/freshness, 2s adjacent
    clock-delta disagreement, >=6 samples, and both clock spans >= horizon.
    Cutoff is inclusive; the latest controller evidence boundary is strict.
    """
    try:
        if (type(rounds) not in (list, tuple) or not 1 <= len(rounds) <= 10000
                or not _ids(known_ids) or not _finite(horizon) or horizon <= 0
                or not _finite(cutoff) or not _finite(now_utc)
                or (last_local_event is not None and not _finite(last_local_event))
                or not _hash(supplied_state_hash) or not _hash(current_state_hash)
                or supplied_state_hash != current_state_hash):
            return False
        ids = set(known_ids)
        last_bad, previous = -1, None
        for index, row in enumerate(rounds):
            utc, mono = row["utc"], row["mono"]
            owned, gets = row["list_owned_ids"], row["get_results"]
            if (not _finite(utc) or not _finite(mono) or mono < 0 or utc > now_utc
                    or not _ids(owned) or type(gets) is not dict
                    or not set(owned) <= ids or not set(gets) <= ids):
                return False
            bad = (row["list_complete"] is not True or bool(owned)
                   or set(gets) != ids or any(v != "MISSING" for v in gets.values())
                   or utc < cutoff
                   or (last_local_event is not None and utc <= last_local_event))
            if bad:
                last_bad, previous = index, None
                continue
            if previous is not None:
                wall_step, mono_step = utc - previous[0], mono - previous[1]
                if (not 0 <= wall_step <= 60 or not 0 <= mono_step <= 60
                        or abs(wall_step - mono_step) > 2):
                    last_bad = index - 1  # Current good round starts at zero.
            previous = utc, mono
        start = last_bad + 1
        if len(rounds) - start < 6:
            return False
        first, latest = rounds[start], rounds[-1]
        return (0 <= now_utc - latest["utc"] <= 60
                and latest["utc"] - first["utc"] >= horizon
                and latest["mono"] - first["mono"] >= horizon)
    except (KeyError, TypeError, ValueError, OverflowError):
        return False