"""A3 unit controls for the durable writer (no Redis needed)."""
from __future__ import annotations

from primordial.fabric import ledger as L


def ev(prod, q, worlds=3):
    return (f"1-{q}", {b"producer": prod.encode(), b"pseq": str(q).encode(),
                       b"world": f"w{q % worlds}".encode(), b"etype": b"OBS",
                       b"payload": L.payload_for(prod, q)})


def test_redelivery_is_counted_duplicate_not_row(tmp_path):
    cx = L.open_db(str(tmp_path / "l.db"))
    assert L.write_batch(cx, [ev("p", q) for q in range(10)]) == (10, 0)
    # POSITIVE control for dedupe: the same batch redelivered (crash between COMMIT and XACK)
    assert L.write_batch(cx, [ev("p", q) for q in range(10)]) == (0, 10)
    # duplicate inside one batch (producer retried after a lost reply)
    assert L.write_batch(cx, [ev("p", 10), ev("p", 10), ev("p", 11)]) == (2, 1)
    v = L.verify(cx)
    assert v["ok"] and v["rows"] == 12


def test_verify_catches_tampered_payload_and_broken_link(tmp_path):
    cx = L.open_db(str(tmp_path / "l.db"))
    L.write_batch(cx, [ev("p", q) for q in range(30)])
    assert L.verify(cx)["ok"]
    # CHEAT control for the verifier: edit one payload byte in place
    cx.execute("UPDATE events SET payload=? WHERE producer='p' AND pseq=7",
               (b"X" + L.payload_for("p", 7)[1:],))
    v = L.verify(cx)
    assert not v["ok"] and v["bad_hash"] == 1 and v["bad_payload"] == 1
    # delete a row mid-chain: gap + broken link must appear
    cx2 = L.open_db(str(tmp_path / "m.db"))
    L.write_batch(cx2, [ev("p", q) for q in range(30)])
    cx2.execute("DELETE FROM events WHERE producer='p' AND pseq=9")
    v2 = L.verify(cx2)
    assert not v2["ok"] and v2["gaps"] >= 1 and v2["bad_link"] >= 1


def test_chain_survives_batch_boundaries(tmp_path):
    cx = L.open_db(str(tmp_path / "l.db"))
    for b in range(5):
        L.write_batch(cx, [ev("p", q) for q in range(b * 7, b * 7 + 7)])
    assert L.verify(cx)["ok"]
