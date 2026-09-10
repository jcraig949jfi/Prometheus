# Licences and costs — where to get them, what they cost

Techne, 2026-09-10, for the operator. Prices were fetched today, not recalled; every figure
carries its source and I say plainly where a vendor does not publish one. Currencies are as
the vendor quotes them.

Three groups, because they need three different actions: **nothing to do**, **something to
fix that costs nothing**, and **something to buy**.

---

## 1. In use now — nothing to buy, nothing to obtain

Machine-readable evidence: `techne/acquisition/LICENSE_EVIDENCE.json`, produced by
`python -m techne.scripts.license_audit`. Every notice is stored beside its copy in the tool
cache under `notices/`.

| tool | version | licence, read from the artifact | cost |
|---|---|---|---|
| hypothesis | 6.165.10 | `MPL-2.0` SPDX in the wheel; notice shipped | $0 |
| ribs (pyribs) | 0.12.0 | `MIT` SPDX in the wheel; notice shipped | $0 |
| pytest | 9.1.1 | `MIT` SPDX in the wheel; notice shipped | $0 |
| z3-solver | 5.0.0.0 | free-text "MIT License", **no notice in the wheel** | $0 |

**z3 is the one with a small chore.** The wheel declares MIT as free text with no SPDX
expression and ships no notice file; the sdist ships `core/LICENSE.txt`, and the repository
carries `LICENSE.txt` at tag `z3-5.0.0` — *Copyright (c) Microsoft Corporation*. The audit has
copied that notice into the cache beside the wheel, so the licence travels with the copy. No
money, no application: MIT is granted in the file.

**MPL-2.0 on hypothesis is file-level copyleft.** It obliges us only if we modify hypothesis's
own source files and distribute them. We use it as a test dependency and modify nothing, so
there is no obligation beyond keeping the notice.

---

## 2. Needs an action, costs nothing

### stitch_core 0.1.29 — a packaging omission, not a missing licence. **I had this narrower than the truth yesterday.**

Yesterday I recorded it as `UNRESOLVED_NO_LICENSE_IN_ANY_DISTRIBUTED_ARTIFACT` on the grounds
that the wheel and sdist carry nothing and that a GitHub API classifier must never be used as
evidence. The rule was right; my application of it was incomplete. I checked the API
classifier and stopped, and never read the repository's own licence *document*.

There is one, at the pinned revision `350804b7b358`:

```
MIT License
Copyright (c) 2021 Matthew Bowers
```

The root `Cargo.toml` also declares `license = "MIT"`. So the grant exists and is named. A
licence document in the source tree is not a classifier — a classifier is GitHub's heuristic
guess, this is the instrument that grants the rights. The status is now
`ARTIFACT_CARRIES_NO_NOTICE_BUT_SOURCE_GRANT_EXISTS`, and `license_audit` reads it as a third,
separately-graded evidence source.

**Where to get it:** nowhere — it is already granted, free, by that file.

**Cost:** $0.

**What is actually wrong,** and it matters because MIT has exactly one condition: *"The above
copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software."* The wheel we installed contains no such notice. So redistributing
that wheel **as shipped** would fail the grant's own condition; redistributing it **with the
notice attached** satisfies it. That is a packaging bug upstream, and our side of it is a
two-line fix already done: the audit stores the repository notice beside the copy.

**The residual gap is the one that keeps D-17 open**, and it is not the licence. `mlb2251/stitch`
publishes exactly one tag (`v0.1.0`) and none corresponds to `stitch_core` 0.1.29, so the
revision carrying that MIT file is **not provably the revision that built the wheel**. The
grant is attached by an inference about provenance rather than by the artifact itself. That is
precisely why D-17 asks for a pinned *source revision* as well as a licence — and on the
current evidence the source revision, not the licence, is the harder half.

**Suggested action, operator's call:**
1. Open an issue on `mlb2251/stitch` asking that `LICENSE` be included in the sdist and wheel
   and that `license` metadata be set in the Python packaging config. Zero issues currently
   mention licensing, so we would be first. Maintainer: Matthew Bowers, `mlbowers@mit.edu`,
   per `Cargo.toml`.
2. Ask the same issue which commit built 0.1.29, or for a tag. That closes the provenance half.
3. Until both land, D-17's stricter reading is the right posture and I am not asking to relax
   it — the change here narrows *why* it is blocked, not *whether*.

### DreamCoder (`ellisk42/ec`) — licensing genuinely unresolved

Its only notice file is a `LICENSE` whose text is the **AngularJS** MIT licence,
*"Copyright (c) 2010-2020 Google LLC. http://angularjs.org"*. That is a copy-paste artifact,
not a statement about DreamCoder, and GitHub's API reporting "MIT" for the repository is
derived from exactly that file — so the classifier inherits the mistake.

**Where to get it:** ask the authors. **Cost:** $0. **Status:** genuinely unresolved, and
unlike stitch there is no correct grant to fall back on. It is moot today because DreamCoder
cannot be built on this host at all (four measured blockers), so nothing derived from it
exists to redistribute.

### GPL-family dependencies — free, but they constrain *distribution*

Nothing to buy; the cost is an obligation if Prometheus ever ships a binary or a bundle.

- **gudhi** — its own code is MIT, but modules depend on CGAL, Miniball and PyKeOps, which are
  GPLv3/LGPL. Upstream's own package list writes this as "MIT (GPL v3)", and for a user it is
  effectively GPLv3.
- **PARI/GP** (behind `class_number`, `galois_group`, `conductor`, `root_number`, LLL) — GPL.
- **SnapPy** (behind `hyperbolic_volume`) — GPL.
- **SageMath**, where used — GPL.

None of this affects internal use. It matters the first time something is distributed, and
that is a decision, not an accident, so it is worth having on record now.

---

## 3. Would cost money — the paywalled targets

These are the Tier 7 "reverse-engineer paywalled functionality" entries in
`techne/ARSENAL_ROADMAP.md`, plus the SDP upgrade path already named in REQ-029. **None is
required for anything running today**; each is an alternative to work the roadmap currently
plans to reimplement.

### MOSEK — the only one with published prices

Named in REQ-029 as the upgrade path from SCS for `pm.optimization.solve_sdp`. Prices
effective 1 September 2025, USD, perpetual with **optional** maintenance for upgrades:

- Floating, base system (PTS): **$2,250** perpetual, **$562.50/yr** maintenance
- Floating, nonlinear & conic extension (PTON): **$2,050** perpetual, **$512.50/yr**
- Node-locked server, base (PTS-NODE): **$9,000** perpetual, **$2,250/yr**
- Node-locked server, nonlinear & conic (PTON-NODE): **$8,200** perpetual, **$2,050/yr**

A useful conic SDP setup is PTS + PTON: **$4,300** perpetual floating, $1,075/yr to stay
current. Group licences are quote-only via `sales@mosek.com`.

**Free route:** academic licences are free — personal (365 days, renewable) or institutional
(2 years, renewable). Eligibility is verbatim *"can only be used for research or educational
purposes at degree-granting academic institutions"*, and requests must use an academic email
address. **Prometheus does not qualify** on that wording as a private research project, so
this is a real $4,300 if we ever want it. Get it at <https://www.mosek.com/buy/>.

### Magma — cheap if we can reach the Simons route, otherwise a subscription

Three roadmap gaps ride on it: `IsogenyClass`, `pAdicLfunction`, and `SelmerGroup` for p > 2.

- Listed price: **AU$2,580** for a three-year subscription, machines with at most 15 cores,
  *at an educational institution*; increases at least yearly; multi-machine discounts.
- **Free route:** since 2013 the Simons Foundation underwrites Magma for *"all U.S. nonprofit,
  non-governmental scientific research or educational institutions"*, and everyone associated
  with a participating institution gets it free through that institution. Again, a private
  project is unlikely to qualify.
- Ordering is via the Computational Algebra Group at Sydney,
  <https://magma.maths.usyd.edu.au/magma/faq/costs> — note that page returned **HTTP 401** to
  me today, so the AU$2,580 figure is from search-result text and the Wikipedia entry rather
  than from the price list itself. **Treat it as indicative and get a quote.**

### Wolfram Mathematica — vendor publishes no fetchable price

Two low-to-medium roadmap gaps (integration quality, special functions). Wolfram's pricing
pages render prices client-side; every one I fetched returned tier names with the amounts
absent. Third-party aggregators disagree with each other — one gives **$2,200 perpetual /
$880 per year** for a standard individual licence, another around **$3,445** perpetual — so I
will not present either as the price. Get a quote at
<https://www.wolfram.com/mathematica/pricing/commercial/>. Each licence covers up to two
machines or one dual-boot system.

### Maple — quote only

One low-priority roadmap gap (ODE classifier). Maplesoft's store did not return prices to a
fetch; the pricing page routes to the web store for single-user and to a quote form for
multi-user. <https://www.maplesoft.com/pricing/>.

### Gurobi — not in the arsenal, listed because it is the obvious MIP alternative

We use `highspy` (MIT, free) for MIP. Gurobi is free for academics — a full-year renewable
licence, named-user or WLS, *"may be used only for research and educational purposes"*, with
commercial use explicitly forbidden — and commercial licences are quote-only and reported as
running to tens of thousands of dollars a year. Unless a specific model defeats HiGHS, this is
not worth opening.

---

## What I would actually spend

**Nothing, today.** Every tool the H0–H5 program runs on is permissively licensed and free,
and the one blocker in the way of an export is a $0 packaging fix plus a provenance question.

If a specific experiment later hits a wall, the order I would rank the spends:

1. **MOSEK PTS+PTON, $4,300 perpetual** — the only one with a published price, a named
   consumer already in the queue (REQ-029), and a clean fallback (SCS) if it disappoints. It is
   also the only purchase here that would be exercised by code that already exists.
2. **Magma, ~AU$2,580/3yr if a route exists** — three roadmap gaps at once, and OSCAR.jl is
   the free substitute the roadmap is already tracking for exactly this. Check whether any
   affiliation opens the Simons route before paying.
3. **Mathematica / Maple — no.** Both back low-priority gaps against mpmath and sympy, neither
   publishes a price, and neither has a consumer.

The honest summary: nothing in this program is gated on a purchase. It is gated on one
upstream packaging fix and one unanswered provenance question, both of which cost an email.

---

## Sources

- MOSEK commercial pricing — <https://www.mosek.com/sales/commercial-pricing/>
- MOSEK academic licences — <https://www.mosek.com/products/academic-licenses/>
- MOSEK purchasing — <https://www.mosek.com/buy/>
- Magma ordering (returned HTTP 401 today) — <https://magma.maths.usyd.edu.au/magma/faq/costs>
- Magma / Simons Foundation — <https://en.wikipedia.org/wiki/Magma_(computer_algebra_system)>
- Mathematica commercial — <https://www.wolfram.com/mathematica/pricing/commercial/>
- Maplesoft pricing — <https://www.maplesoft.com/pricing/>
- Gurobi academic — <https://www.gurobi.com/academics>
- GUDHI licensing — <https://gudhi.inria.fr/licensing/>
- stitch licence and packaging metadata — `mlb2251/stitch` at `350804b7b358`, read through the
  GitHub contents API and recorded in `techne/acquisition/LICENSE_EVIDENCE.json`
