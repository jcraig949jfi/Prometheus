# U - ARCHIVE SEARCH-COVERAGE MAP

Purpose: make the archaeology boundary explicit so that
`KNOWN_GENERATED_BUT_NOT_ARCHIVED` is never confused with `SEARCH_INCOMPLETE`.

## URL spaces checked

| Space | Method | Result |
|---|---|---|
| `myxo.css.msu.edu/papers/nature2003/` | live HTTP | DEAD (404 http / 501 https) |
| same, Wayback snapshot `20211122232656` | availability API + `id_` fetch | RECOVERED (index, 9015 B) |
| child objects of that index | direct `id_` fetches | paper, software.html, both config tarballs RECOVERED; `case-study/lineage.html` and `pivotal_arrays/index.html` returned archive 404 (linked but not captured) |
| `dllab.caltech.edu/avida/` (the Avida 1.6 distribution pointer) | Wayback `id_` at 2003, 20030401, 20030801; availability API | **ALL HTTP 429.** NOT retrieved, NOT shown absent |
| `sourceforge.net/projects/avida` | REST + RSS, 5 path roots | project created 2002-02-15 but ONLY `avida-stable` exists; oldest release 2.2 (2005-02-14). **No 1.6.** |
| `sourceforge.net/p/avida/cvs/` | HTTP | page exists (200); legacy `avida.cvs.sourceforge.net` viewvc host does not resolve; no `cvs` client available locally |
| `github.com/devosoft/avida` | GitHub API | repo created 2010-11-05, earliest commit 2010-12-22, tags 2.12.4 / 2.14.0. Not the specimen. |
| Software Heritage | origin search "avida" | only unrelated repositories returned |

## Timestamp windows checked

Only the single snapshot `20211122232656` was successfully queried. **Adjacent
captures were NOT enumerated**: the CDX index returned HTTP 429 on every
attempt across this session. That is the largest single gap in coverage.

## Object naming patterns checked

Every href on the recovered index. No population, `.spop`, `detail`, or dump
object appears anywhere in it.

## Known-but-not-retrieved

- `Supp1.pdf/html`, `Supp2.pdf/html`, `Supp3.pdf/html`, `Supp4.pdf`,
  `glossary.html`, `logic_programs.html` -- listed on the index, never fetched
- Avida 1.6 source at `dllab.caltech.edu/avida/` -- throttled, not absent
- adjacent Wayback captures of the myxo tree -- CDX throttled

## Definite archived misses

`case-study/lineage.html` and `pivotal_arrays/index.html` were linked from the
2021 index but return archive 404 at that timestamp. They may exist at other
timestamps; that is untested (CDX throttled).

## Verdict on coverage

    archive search coverage closed?   NO

The population-dump question is **NOT** settled. The event_list proves the
dumps were written (`u 50:50 detail_pop`). The 2021 index does not list them.
Neither fact establishes that no capture anywhere holds them, because the
timestamp axis was never enumerated.

Declaring `HISTORICAL_CONTROLS_LIKELY_UNRECOVERABLE` on this evidence would be
premature, and the directive explicitly forbids it: *"Do not declare historical
controls unrecoverable merely because another finite set of HTTP requests
failed."*

## Cheapest next actions

1. Retry the CDX index from a different network path or after a long cooling
   period, and enumerate every capture of `myxo.css.msu.edu/papers/nature2003*`.
2. Retry `dllab.caltech.edu/avida/` for 1.6.
3. Fetch Supp1-4 and `logic_programs.html`, which may name further objects.
