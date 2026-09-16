"""Proteus #287 round trip: one minted-shaped player row through the client
as agent Proteus, read back by player_id, compared column by column.

    positive   every mapped column reads back equal; producer.mint_id equal
    idempotent the identical re-registration is duplicate_identical
    cheat 1    the Proteus token with a wrong X-Prometheus-Agent header is 401
    cheat 2    a re-registration that differs in one stored value is 409 and
               the stored row is unchanged
    cheat 3    an unknown field (a typo of mate_player) is 422, not silently
               dropped into the row

Namespace 'test'. Needs the Proteus token out of band on this host
(~/.prometheus/ew_agent_tokens.json). Run from a task worktree:
    python integration/minted_player_check.py --machine M2
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew.client import EvidenceWiki, _token_for  # noqa: E402

R = []


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return bool(ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--machine", default="M2")
    a = ap.parse_args()
    base = f"http://{a.host}:{a.port}"
    cli = EvidenceWiki(base=base, machine=a.machine, agent="Proteus")
    stamp = int(time.time())
    pid = "evca:r3:" + hashlib.sha256(f"mintcheck-{stamp}".encode()).hexdigest()[:32]
    parent = "evca:r3:" + "a" * 32
    mate = "evca:r3:" + "b" * 32
    row = dict(
        genome_hash="sha256:" + hashlib.sha256(f"org-{stamp}".encode()).hexdigest(),
        parent_player=parent, mate_player=mate,
        mutation_ref=f"herakles-derivation-{stamp}",
        family="rule_table",
        representation_version="herakles.evca.rule_hex.r3.v1",
        semantic_version="herakles.evca.core.v1",
        producer={"component": "proteus.rule_table_mint", "version": "v1",
                  "mint_id": f"mint-{stamp}", "operator": "crossover",
                  "params": {"cut": 7}, "verified": True},
        namespace="test")

    try:
        w = cli.register_fossil_player(pid, **row)
        gate("W_written_as_Proteus", w.get("status") == "inserted", json.dumps(w))
    except Exception as e:
        gate("W_written_as_Proteus", False, str(e)[:200])
        return finish(pid)

    back = cli.get_fossil_player(pid)
    mapped = ["genome_hash", "parent_player", "mate_player", "mutation_ref", "family",
              "representation_version", "semantic_version", "namespace"]
    diffs = [f"{k}: sent {row[k]!r} stored {back.get(k)!r}" for k in mapped if back.get(k) != row[k]]
    prod_ok = (back.get("producer") or {}).get("mint_id") == row["producer"]["mint_id"]
    gate("P_every_mapped_column_reads_back", not diffs and prod_ok and back.get("player_id") == pid,
         f"diffs={diffs} mint_id_equal={prod_ok} nulls={[k for k in ('runtime_hash','lineage_id','generation') if back.get(k) is None]}")

    again = cli.register_fossil_player(pid, **row)
    gate("I_identical_rereg_is_duplicate", again.get("status") == "duplicate_identical", json.dumps(again))

    # cheat 1: same token, wrong agent header
    tok = _token_for("Proteus")
    r = requests.get(f"{base}/api/v1/fossil/players/{pid}",
                     headers={"Authorization": f"Bearer {tok}", "X-Prometheus-Machine": a.machine,
                              "X-Prometheus-Agent": "NotProteus"}, timeout=30)
    gate("C1_wrong_agent_header_401", r.status_code == 401, f"{r.status_code} {r.text[:80]}")

    # cheat 2: one stored value differs -> 409, row unchanged
    try:
        cli.register_fossil_player(pid, **{**row, "mate_player": "evca:r3:" + "c" * 32})
        gate("C2_differing_rereg_409", False, "accepted")
    except ValueError as e:
        gate("C2_differing_rereg_409", "rejected 409" in str(e) and "mate_player" in str(e), str(e)[:160])
    back2 = cli.get_fossil_player(pid)
    gate("C2b_row_unchanged_after_409", back2.get("mate_player") == mate, f"stored mate_player={back2.get('mate_player')}")

    # cheat 3: unknown field is refused, not dropped
    try:
        cli.register_fossil_player(pid + "x", **{**row, "mate_playr": mate})
        gate("C3_unknown_field_422", False, "accepted")
    except ValueError as e:
        gate("C3_unknown_field_422", "rejected 422" in str(e), str(e)[:160])
    return finish(pid)


def finish(pid):
    ok = all(r["pass"] for r in R)
    out = {"all_pass": ok, "player_id": pid, "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "gates": R}
    (HERE / "integration" / "minted_player_results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"all_pass": ok, "n_gates": len(R)}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
