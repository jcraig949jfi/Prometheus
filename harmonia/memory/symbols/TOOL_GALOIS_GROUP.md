---
name: TOOL_GALOIS_GROUP
type: tool
version: 1
tier: 1
language: python
interface: galois_group(polynomial) -> dict
also:
  - is_abelian(polynomial) -> bool
  - disc_is_square(polynomial) -> bool
dependencies: [cypari]
complexity: polynomial in degree; constant-factor large for deg > 5
tested_against: S_n/A_n/D_n witnesses, cyclotomics, Frobenius F(5); 17 assertions
failure_modes:
  - Degree > 11 raises ValueError (PARI polgalois limit without galdata pkg).
  - Input must be irreducible over Q; PARI raises PariError otherwise.
  - is_abelian heuristic-by-name plus order==degree guard. Pathological names may misreport; check order field if suspicious.
requested_by: Harmonia
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P02, P09]
references:
  - REQ-011
  - Report #18 (Chebotarev density, Bartel-Lenstra bins)
---

# TOOL_GALOIS_GROUP — Galois group of an irreducible polynomial over Q

```python
from techne.lib.galois_group import galois_group, is_abelian, disc_is_square

galois_group('x^3-2')
# {'name': 'S3', 'order': 6, 'transitive_id': (3, 2),
#  'parity': -1, 'is_abelian': False, 'degree': 3}

galois_group('x^3-3*x-1')      # cyclic cubic (disc = 9^2)
# {'name': 'A3', 'order': 3, 'transitive_id': (3, 1),
#  'parity': 1, 'is_abelian': True, 'degree': 3}

is_abelian('polcyclo(8)')       # True  (Gal = (Z/8)^* = V4)
disc_is_square('x^4-10*x^2+1')  # True  (Gal = V4 ⊆ A_4)
```

## When to use

- **Chebotarev density tests**: bin NFs by Galois group to check splitting-type
  frequencies match |C|/|G| for conjugacy classes C.
- **Bartel-Lenstra screening** (Report #18): stratify by G and look for conjectural
  rank/class-number distributions within each stratum.
- **Universal stratifier for NFs**: (degree, galois_group.order, parity) gives
  a 3-tuple that separates most fields of interest.

## When NOT to use

- Degree > 11: not supported without galdata.
- Polynomial is reducible: factor first, call per irreducible factor.
- You need the Galois group AS A CONCRETE GROUP (with multiplication table):
  this returns the transitive-group identifier, not the abstract group object.
