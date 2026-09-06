# The bitstring oracle is already an exact concept-learning instrument

**Date:** 2026-09-06. **Seat:** Herakles. **Status:** mechanism verified by
execution; no experiment run.

Two analysts working on different chunks, different disciplines and without
contact converged on the same observation. It is the strongest thing this pass
has found, it needs no new executor, and the field-first mining framing could
not have produced it.

---

## 1. The observation

`evaluate_bitstring` is a Hamming oracle over a hidden target. A single score
at a fixed seed and length tells you EXACTLY how many positions your candidate
shares with the target. So each query partitions the hypothesis space
precisely, and the set of targets still consistent with what you have seen is a
Hamming sphere whose size is a binomial coefficient.

That is Mastermind. It is also, in the machine-learning vocabulary, an exact
version space with a noiseless oracle, which is the setting where active
learning has its cleanest theory.

**Verified, seed_root 424242, length 24:**

    the hidden target is             001000010111001101111101
    the same seed_root reproduces it across independent specs   yes
    a different seed_root gives a different target              yes

    guess          score     Hamming distance   surviving targets
    ------------   -------   ----------------   -----------------
    all zeros       0.4583                 13   C(24,13) = 2496144
    all ones        0.5417                 11   C(24,11) = 2496144
    half and half   0.6250                  9   C(24, 9) = 1307504

The surviving count is not estimated. It is computed.

## 2. Why it runs TODAY, with no new code

The obstacle looked like this: a spec's payload is fixed, so one spec is one
query, and search cannot happen inside a spec. True. But the hidden target
depends only on the seed and the length, and **a template may fix the seed**.

    "param_space": {
      "payload": {"bits":   {"uniform_bits": "length"},
                  "length": {"choices": "24"}},
      "world":   {"seed_root": {"choices": "424242"}}
    }

Every draw from that template is a NEW candidate against the SAME hidden
target. N draws are N queries in one Mastermind game. The elimination happens
downstream, in analysis, which is exactly where the bench already puts
cross-observation reasoning.

This uses only the existing draw vocabulary, the existing executor and the
existing outcome rule. Nothing is added.

## 3. Why it matters for M-SIGNAL specifically, not just as a nice experiment

M-SIGNAL asks whether fossil information improves selection, and specifies the
shape of the answer: a frozen random baseline, a second named policy, equal
budget, separate lanes, endpoint pre-registered, Harmonia adjudicating.

The version-space setting gives that shape a substrate where the ground truth
is known in closed form:

- **The random arm** is the frozen baseline drawing candidates uniformly.
- **The informed arm** chooses the next candidate using the scores already
  fossilized, which is precisely "fossil information improving selection".
- **The endpoint** is queries-to-target, or surviving-hypothesis-count after a
  fixed budget. Both are computable exactly, with no adjudication ambiguity.
- **The floor** is information-theoretic. Each query returns one of L+1
  possible scores, so it yields at most log2(L+1) bits, and identifying one of
  2^L targets needs at least L / log2(L+1) queries. For L = 24 that is about
  5.2 queries. A policy claiming to beat that is wrong, and a policy far above
  it has room to improve. The gate can be shown reachable BEFORE it is frozen,
  which is the discipline `feedback_gate_must_be_shown_reachable` demands.

So this is an M-SIGNAL rehearsal on a substrate that cannot lie about the
answer. If the informed policy cannot beat random HERE, where the oracle is
exact and the theory is closed-form, that is a strong and cheap negative about
the selection machinery rather than about the science.

## 4. What it does not license

- It is not evidence about the SFE fossil corpus. The landscape is a hash, so
  it has no structure beyond distance-to-target: unimodal, undeceptive, no
  neutrality, no epistasis. Methods that exist to handle deception or ruggedness
  are being run outside their domain, and an analyst flagged exactly this for
  MAP-Elites and novelty search in the same corpus.
- It does not show that a signal-directed policy helps on REAL regions. It
  shows whether the plumbing that would carry such a policy works, and
  calibrates it against a known optimum.
- A single game is one seed. The seed must be swept across games, and the
  per-game budget fixed, or the result is a statement about one target.

## 5. The adjacent capability this makes obvious

An analyst on a different chunk found the complement: **the bench has no
relatedness axis.** Targets are hashed from seed and length, so any two worlds
are unrelated by construction and expected transfer between them is exactly
zero. Every transfer, curriculum, stepping-stone and generalisation experiment
is therefore blocked, not by a missing executor but by a missing parameter.

The fix is one parameter and it is backward compatible: derive a target as the
seed's target with `d` positions flipped, so `d` is a declared Hamming distance
between worlds and `d = 0` reproduces today's behaviour exactly.

That single axis turns a pile of unrelated puzzles into a space with a
geometry, and it is the cheapest capability this pass has identified. It is
also what would let the version-space experiment above become a transfer
experiment rather than a repeated one.

## 6. Reproduction

    cd F:/Prometheus
    python - <<'EOF'
    import sys, math
    sys.path.insert(0,'vivarium')
    sys.path.insert(0,'SerendipityFoundry/SerendipityFoundryEngine')
    from viv import spec as S
    from sfe.executors import BitStringExecutor
    sp = {"spec_version":3, "world":{"seed_root":424242},
          "work":{"kind":"evaluate_bitstring","payload":{"bits":"0"*24,"length":24}},
          "repeat":{"count":1,"order":"sequential","seed_derivation":"sha256_index",
                    "state":"reset","budget":{"max_seconds":60,"max_observations":1}},
          "hypothesis":"h","prediction":None,
          "outcome_rule":{"field":"score","op":">=","value":0.75,
                          "if_true":"SURVIVED","if_false":"FALSIFIED",
                          "if_indeterminate":"INCONCLUSIVE"}}
    seed = S.repeat_plan(sp)["seeds"][0]
    t = BitStringExecutor(length=24).target_for(seed)
    g = "0"*24
    k = 24 - sum(1 for a,b in zip(g,t) if a==b)
    print(t, k, math.comb(24,k))
    EOF
