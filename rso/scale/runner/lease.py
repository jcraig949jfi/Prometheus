"""Per-partition execution lease (C-013-T022). One live worker per chain: the local analogue of Fabric's
one-live-attempt-per-task invariant (moonshot/nf/INTERFACE_CONTRACT.md:21-22). A canonical Fabric lease is
OPTIONAL for this packet (escalation response) and not taken: this lease is host-local and fences publication.

A lease is live while its holder renews it within ttl_s and, on this host, while its holder process exists. A
killed worker therefore frees its partition at once on the same host, and after ttl_s anywhere else.
"""
import os
import time
import uuid

from rso.scale.runner import store as S

DEFAULT_TTL_S = 30


def _dir(run_dir, chain_id):
    return os.path.join(run_dir, "partitions", chain_id)


def _path(run_dir, chain_id):
    return os.path.join(_dir(run_dir, chain_id), "LEASE.json")


def _lock(run_dir, chain_id):
    return S.FileLock(os.path.join(_dir(run_dir, chain_id), ".lease.lock"))


def _read(run_dir, chain_id):
    p = _path(run_dir, chain_id)
    return S.read_json(p) if os.path.exists(p) else None


def is_live(lease, now=None):
    if not lease:
        return False
    now = time.time() if now is None else now
    if lease["renewed_at"] + lease["ttl_s"] < now:
        return False
    if lease["host"] == S.HOST and not S.pid_alive(lease["pid"], lease.get("create_time")):
        return False
    return True


def acquire(run_dir, chain_id, ttl_s=DEFAULT_TTL_S):
    """A new token, or None while another live holder (this process included) has the partition."""
    with _lock(run_dir, chain_id):
        cur = _read(run_dir, chain_id)
        if is_live(cur):
            return None
        me = S.my_identity()
        now = time.time()
        lease = dict(me, token=uuid.uuid4().hex, ttl_s=ttl_s, acquired_at=now, renewed_at=now,
                     previous=cur and {k: cur.get(k) for k in ("token", "pid", "host")})
        S.atomic_write_json(_path(run_dir, chain_id), lease)
        return lease["token"]


def renew(run_dir, chain_id, token):
    with _lock(run_dir, chain_id):
        cur = _read(run_dir, chain_id)
        if not cur or cur["token"] != token:
            return False
        cur["renewed_at"] = time.time()
        S.atomic_write_json(_path(run_dir, chain_id), cur)
        return True


def release(run_dir, chain_id, token):
    with _lock(run_dir, chain_id):
        cur = _read(run_dir, chain_id)
        if cur and cur["token"] == token:
            os.remove(_path(run_dir, chain_id))
            return True
        return False


def is_holder(run_dir, chain_id, token):
    """Publication fence: the caller still holds the lease (no one has taken it over)."""
    cur = _read(run_dir, chain_id)
    return bool(cur) and cur["token"] == token


def live_holder(run_dir, chain_id):
    cur = _read(run_dir, chain_id)
    return cur if is_live(cur) else None


def force_expire(run_dir, chain_id):
    """Tests: age the lease past its TTL, as wall time would for a killed holder on another host."""
    with _lock(run_dir, chain_id):
        cur = _read(run_dir, chain_id)
        if cur:
            cur["renewed_at"] = 0.0
            S.atomic_write_json(_path(run_dir, chain_id), cur)


def force_dead_holder(run_dir, chain_id):
    """Tests: make the holder a pid that no longer exists (a killed worker on this host)."""
    with _lock(run_dir, chain_id):
        cur = _read(run_dir, chain_id)
        if cur:
            cur["pid"], cur["create_time"] = 2 ** 31 - 3, 0.0
            S.atomic_write_json(_path(run_dir, chain_id), cur)
