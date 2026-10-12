import pytest

from prometheus.cosmos import lease


def test_second_instance_refused_until_expiry(tmp_path):
    lease.acquire("a", ttl=100, root=tmp_path, now=1000)
    with pytest.raises(lease.LeaseHeld):
        lease.acquire("b", ttl=100, root=tmp_path, now=1050)
    rec = lease.acquire("b", ttl=100, root=tmp_path, now=1101)
    assert rec["instance"] == "b"


def test_renew_keeps_acquired_and_extends(tmp_path):
    first = lease.acquire("a", ttl=100, root=tmp_path, now=1000)
    rec = lease.renew("a", root=tmp_path, now=1090)
    assert rec["acquired"] == first["acquired"] and rec["expires"] == 1190


def test_non_holder_cannot_renew_or_release(tmp_path):
    lease.acquire("a", ttl=100, root=tmp_path, now=1000)
    with pytest.raises(lease.LeaseHeld):
        lease.renew("b", root=tmp_path, now=1010)
    lease.release("b", root=tmp_path)
    assert lease.read(tmp_path)["instance"] == "a"
    lease.release("a", root=tmp_path)
    assert lease.read(tmp_path) is None
