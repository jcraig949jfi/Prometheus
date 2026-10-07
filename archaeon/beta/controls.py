"""One-call competence audit for an organism on a composed world or a WSE event world (Archaeon Beta instrument).

Built from the controls that killed or confirmed every positive in the 2026-10-07 Beta campaign:
  composed worlds (archaeon.campaign6.worlds.runtime.ComposedWorld, optionally NoClock-wrapped):
    constant twin   best fixed-output program (B23b)            -- weak: open-loop patterns beat it (B26)
    blind twin      every observation word zeroed (B26)          -- PRIMARY control
    echo twins      output input word j of channel 0 (B23c)       -- pass-through worlds
    word ablation   zero one observation word at a time (B26)     -- WHAT is sensed
    persist=none    state reset every tick (B30)                 -- does it carry state
  WSE event worlds (archaeon.wse.worlds.WorldSpec episodes):
    wide jitter     0-7 NOISE ticks before each ask (B08K)        -- delay lines / lag-window exploits

audit_composed(manifest, world, seed) and audit_wse(manifest, episodes) return a dict with every number and a
verdict list. A competence claim should quote the verdicts, not the raw reward.
"""
from __future__ import annotations

from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest, score
from archaeon.beta.b23c_attack_artifacts import echo_manifest
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.wse.evolve import evaluate

MARGIN = 0.05


def audit_composed(manifest: dict, world, seed: int) -> dict:
    base = score(manifest, world, seed)
    n_words = len(world.observe(world.reset(seed, 0, None))[0])
    const = max(score(constant_manifest(c, world.K), world, seed) for c in CONSTS)
    blind = score(manifest, Ablate(world, "all"), seed)
    echo = max(score(echo_manifest(0, j, world.K), world, seed) for j in range(min(8, n_words)))
    drops = {i: round(base - score(manifest, Ablate(world, i), seed), 4) for i in range(n_words)}
    nop = score(dict(manifest, persist="none"), world, seed) if "persist" in manifest else None
    verdicts = []
    verdicts.append("BEATS_CONSTANT" if base - const >= MARGIN else "NOT_ABOVE_CONSTANT")
    verdicts.append("INPUT_USING" if base - blind >= MARGIN else "BLIND_POLICY")
    verdicts.append("BEATS_ECHO" if base - echo >= MARGIN else "ECHO_EXPLAINS")
    if nop is not None:
        verdicts.append("CARRIES_STATE" if base - nop >= MARGIN else "REACTIVE")
    return {"reward": round(base, 4), "constant": round(const, 4), "blind": round(blind, 4), "echo": round(echo, 4),
            "persist_none": None if nop is None else round(nop, 4), "word_drops": drops,
            "sensed_words": [i for i, d in drops.items() if d >= MARGIN], "verdicts": verdicts}


def audit_wse(manifest: dict, episodes: list, key=("controls",)) -> dict:
    plain = evaluate(manifest, episodes, rng_seed=7)["reward"]
    jit = evaluate(manifest, wide(episodes, key), rng_seed=7)["reward"]
    return {"reward": round(plain, 4), "wide_jitter": round(jit, 4),
            "verdicts": ["TIMING_EXPLOIT" if plain - jit >= .15 else ("GENUINE_STATE" if jit >= .9 else "PARTIAL")]}


def _self_test() -> int:
    """Known answers: the hand content policy senses pools and beats constant/blind/echo on NoClock P-boom; the
    evolved clock-sweep elite is BLIND to content and loses its reward without the clock; the hand slot solver is
    GENUINE_STATE under wide jitter and a known delay-line elite is a TIMING_EXPLOIT."""
    import json
    from pathlib import Path
    from archaeon.beta.b25_noclock_world import NoClock, content_manifest, load
    from archaeon.beta.b01_w2k2_existence import SOLVER, manifest as v0m
    from archaeon.beta.b08_primitive_ladder import eps_for as plain_eps
    world, seed, sweep = load()
    a = audit_composed(content_manifest(), NoClock(world), seed)
    assert "INPUT_USING" in a["verdicts"] and "BEATS_CONSTANT" in a["verdicts"] and a["sensed_words"], a
    b = audit_composed(sweep, NoClock(world), seed)
    assert "NOT_ABOVE_CONSTANT" in b["verdicts"], b
    eps = plain_eps("L4_order", "heldout", 7, 48)
    assert audit_wse(v0m(SOLVER), eps)["verdicts"] == ["GENUINE_STATE"]
    d = json.loads((Path(__file__).resolve().parent / "results" / "B08_result.json").read_text(encoding="utf-8"))
    delay = [r["elite_manifest"] for r in d["rows"] if r["rung"] == "L4_order" and r["solved_gen"] is not None][0]
    assert audit_wse(delay, eps)["verdicts"] == ["TIMING_EXPLOIT"]
    print("controls self-test: 4/4 known answers")
    return 0


if __name__ == "__main__":
    raise SystemExit(_self_test())
