# Human-In-The-Loop TODO
## Updated: 2026-04-05 (afternoon)

---

## COMPLETED BY JAMES
- [x] Materials Project API key (in DeepseekKey.txt) — DONE, 1000 materials ingested
- [ ] OEIS full dump — James registering

## STILL NEEDED

### 1. OEIS Full Metadata Dump (URGENT)
**What:** Full OEIS internal format with cross-references
**Where:** After registration, check https://oeis.org/wiki/Welcome
**Save to:** `F:\Prometheus\cartography\oeis\data\`
**Unblocks:** Cross-reference graph (most valuable OEIS structure)

### 2. GAP System Install
**How:** `conda install -c conda-forge gap-system`
**Unblocks:** Character table extraction from SmallGroups (97MB cloned)

### 3. Bilbao Crystallographic Server
**Issue:** SSL certificate error from Python. Works in browser.
**What:** Download space group tables from https://www.cryst.ehu.es/
**Save to:** `F:\Prometheus\cartography\physics\data\bilbao\`

### 4. MSC 2020 Taxonomy
**Issue:** No machine-readable download found automatically
**Where:** https://msc2020.org/ or AMS website
**What:** The ~6000 category taxonomy as structured data (JSON/CSV)
**Save to:** `F:\Prometheus\cartography\meta\msc_taxonomy.json`

---

## BLOCKED ON EXTERNAL APIs (not fixable by us)
- nLab: Cloudflare 403
- ProofWiki: Cloudflare 403
- House of Graphs: 401 auth needed
- PDG: API 500 error
- ATLAS representations: 404 on data files

## STATUS
| # | Item | Status |
|---|------|--------|
| 1 | OEIS full dump | James registering |
| 2 | Materials Project key | DONE |
| 3 | GAP install | PENDING |
| 4 | Bilbao data | PENDING (SSL) |
| 5 | FindStat | DONE (API works) |
| 6 | KnotInfo | IN PROGRESS (parsing) |
| 7 | DLMF | DONE (36 chapters mapped) |
| 8 | House of Graphs | BLOCKED (401) |
| 9 | MSC taxonomy | PENDING |
