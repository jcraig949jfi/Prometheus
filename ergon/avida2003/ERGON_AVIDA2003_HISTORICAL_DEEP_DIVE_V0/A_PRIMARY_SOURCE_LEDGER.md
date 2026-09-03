# A - PRIMARY SOURCE LEDGER

Every row states what was actually touched. Nothing is promoted to
PRIMARY_SOURCE_READ without an exact locator (gate P3).

## READ

| Source | Locator | Class | What it established |
|---|---|---|---|
| Supplementary Information to Lenski, Ofria, Pennock & Adami, "The evolutionary origin of complex features", Nature 423:139-144 (2003) | doi:10.1038/nature01568 ; ESM file `41586_2003_BFnature01568_MOESM1_ESM.pdf` ; sha256 970b2711762cf61fa87f4a226f46a32f213d06ddad33361e9284fe79a5939e7a | PRIMARY_SOURCE_READ + ARTIFACT_IN_HAND | 26-instruction table; 1- and 2-input logic truth tables with minimum-NAND counts; 32-bit credit rule; shortest hand-written EQU program; COMPLETE line of descent, pd 0-111, with genomes |
| Avida 2.2 `source/support/environment.cfg` | inside avida-src-devel-2.2.tar.gz, sha256 2e5384147bec575602c6b3a271a3d020ee6a9af1a082d2dc578fc0a0cfee960d | ARTIFACT_IN_HAND | nine REACTION lines, reward exponents, type=pow, max_count=1 |
| Avida 2.2 `source/support/inst_set.default` | same tarball | ARTIFACT_IN_HAND | 26 instructions, order identical to the supplementary |
| Avida 2.2 `source/main/landscape.hh` and `landscape.cc` | same tarball | ARTIFACT_IN_HAND | the HISTORICAL mutational-landscape analyzer. Decisive for D. |
| Nature article landing page | https://www.nature.com/articles/nature01568 | ARTIFACT_IN_HAND (landing page only) | title, DOI, supplementary locator, and confirmation that the full text is paywalled |

## NOT READ - and it matters

| Source | Status | Consequence |
|---|---|---|
| Main paper full text (Methods) | PAYWALLED. Landing page carries institutional-access and purchase markers. | Population size, world geometry, mutation rates, replicate count and seeds are all UNSPECIFIED. See E. |
| `myxo.css.msu.edu/papers/nature2003/` - the paper's OWN data repository, named in the supplementary | DEAD. http returns 404, https returns 501. | The line of descent as distributed (345 genotypes), the functional-genomic arrays, the configuration files and any population dumps are not directly retrievable. |
| Wayback snapshot of that repository | EXISTS AND CONFIRMED AVAILABLE: the availability API returns status 200 for timestamp 20211122232656. Retrieval BLOCKED this session by HTTP 429 rate limiting after repeated CDX queries. | This is the single highest-value unblocking action. It is a throttling problem, not an absence. |
| SourceForge CVS repository (`cvs.sourceforge.net:/cvsroot/avida`, tool live at https://sourceforge.net/p/avida/cvs/) | NOT EXPLORED | The only plausible route to 2003-era source revisions. The 2.2 tarball's own `CVS/Root` file names this server, so the linkage is verified, not guessed. |

## Negative results of the artifact hunt - recorded because they bound the specimen

- **GitHub `devosoft/avida` does not contain the 2003 source.** Repository created 2010-11-05; earliest commit 2010-12-22; only tags are 2.12.4 and 2.14.0. It is a later lineage of the same software, not the specimen.
- **SourceForge holds no pre-2005 release.** The project was created 2002-02-15, but the oldest surviving file release is `avida-src-devel-2.2.tar.gz` dated 2005-02-14 - roughly 21 months AFTER the experiment.
- **Software Heritage origin search for "avida" returned unrelated repositories.** No archived 2003-era Avida origin was found by name search.

Consequence: **no artifact recovered in this pass is contemporaneous with the
experiment.** The supplementary is the only primary source, and it is a
description of the experiment rather than the software that ran it.
