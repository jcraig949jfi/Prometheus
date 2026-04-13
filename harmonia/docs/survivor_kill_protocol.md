# Survivor Kill Protocol
## 8 tests designed to break the last surviving signals
## Execute ONLY on signals that survive the decisive test

---

## The Claim to Kill

> Rank is encoded in the rate of convergence of a_p/sqrt(p) to the Sato-Tate distribution, visible in a finite conductor window, and destroyed by shuffling.

> The position of low-lying L-function zeros encodes isogeny class size, surviving conductor and rank controls.

---

## Test 1: Prime Reindexing (order vs arithmetic order)
Keep a_p values, reassign to different primes within log-bins of p.
Preserves distribution + scale, destroys prime identity.
- Signal survives → not about arithmetic ordering
- Signal dies → depends on true prime structure (very strong)

## Test 2: Low-Primes Ablation (prefix removal)
Remove first 10, 50, 100 primes. Recompute convergence rate.
- Collapses quickly → driven by tiny prefix (artifact)
- Degrades gradually → genuinely distributed (real)

## Test 3: Windowed Convergence Profile
Compute convergence over sliding windows in p.
Map: convergence(p_min, p_max) as a function.
- Signal concentrated in band → boundary layer effect
- Drifts with conductor → global dynamical bias

## Test 4: CM vs Non-CM Split
CM curves violate generic Sato-Tate.
- Signal only in non-CM → consistent with spectral theory
- Signal in both → something more basic (or a bug)

## Test 5: Twist Stability
Take curves and their quadratic twists. Twists can change rank.
- Convergence rate tracks rank within twist families → extremely strong
- Doesn't → family-level artifact

## Test 6: Explicit Low-Zero Coupling
Include first zero gamma_1 and low-zero spacing as controls.
Does convergence rate still predict rank AFTER conditioning on low zeros?
- Disappears → proxy for low-lying zeros (known structure)
- Survives → genuinely new information beyond standard spectral stats

## Test 7: Multiplicative Structure Destruction
Keep primes, randomize signs subject to same marginal distribution.
- Signal depends on multiplicative coherence → arithmetic
- Doesn't → generic

## Test 8: Asymptotic Scaling Law
Fit signal_strength ~ C^(-alpha). Compare exponent to RMT predictions.
- Exponent matches theory → huge credibility boost
- Doesn't → empirical anomaly or artifact

---

## Execution Order
1. Test 1 (prime reindexing) — kills "order artifact"
2. Test 2 (low-prime ablation) — kills "prefix artifact"
3. Test 6 (low-zero coupling) — kills "proxy for known spectral stats"
4. Test 4 (CM split) — kills "generic property"
5. Test 5 (twist stability) — if it survives, extremely strong
6. Test 8 (scaling law) — connects to theory
7. Tests 3, 7 — refinement

## Success Criteria
A signal survives this protocol if:
- Test 1: dies under prime reindexing
- Test 2: degrades gradually (not prefix-driven)
- Test 6: survives after conditioning on low zeros
- Test 4: present in non-CM only
- All with conductor-matched shuffled controls

If ALL pass: formal conjecture territory.
If ANY fail: kill and document.
