"""Batch 09 of the fossil harvest (2026-09-13): LOSERS -- failed / superseded / displaced machinery.

Charter 2026-09-13: only 15/109 specimens carried a failed-or-superseded disposition, making it the
emptiest first-class axis. This batch acquires machinery whose historical importance INCLUDES its
defeat, and -- where practical -- the rival that beat it plus the shared problem, so the comparison
can be made later without Techne deciding why one won.

EVERY disposition here is a factual claim backed by a citation in historical_disposition.evidence
(record.validate REFUSES a non-ACTIVE state with no evidence). Nothing is called a loser because it
looks old. Techne records the human record's verdict and the reason the human record gives; it does
not rank the machinery.
"""
from __future__ import annotations

from .. import record

S = []
NETLIB = "https://www.netlib.org"


def spec(sid, **kw):
    S.append(record.skeleton(sid, **kw))


def url(u, fn):
    return {"kind": "url", "url": u, "filename": fn, "extract": False}


# ===================== PAIR 1: dense linear algebra -- LINPACK (loser) vs LAPACK (winner) =====
spec("linpack-netlib-1979",
    canonical_name="LINPACK (1979) -- the Fortran dense linear algebra library, superseded by LAPACK",
    aliases=["LINPACK", "dgefa", "linpack benchmark"],
    lineage="LINPACK (Dongarra, Bunch, Moler, Stewart, 1979) organised dense linear algebra around COLUMN operations expressed in Level-1 BLAS (vector-vector: daxpy, dscal, ddot, idamax). It defined the field and gave the world the LINPACK benchmark still used for the TOP500. It was superseded by LAPACK, which solves the SAME problems restructured around blocked Level-3 BLAS. The loser and the winner compute the same LU factorisation; only the memory-access structure differs.",
    domain=["numerical-linear-algebra", "scientific-computing", "dense-linear-algebra", "benchmark", "loser"],
    era="1979 (LINPACK); superseded from 1992 (LAPACK)",
    version="netlib linpack routines + the linpackd benchmark, as served by netlib 2026-09-13",
    source_origin={"artifacts": [
        url(NETLIB + "/benchmark/linpackd", "linpackd.f"),
        url(NETLIB + "/linpack/dgefa.f", "dgefa.f"),
        url(NETLIB + "/linpack/dgesl.f", "dgesl.f"),
        url(NETLIB + "/blas/daxpy.f", "daxpy.f"),
        url(NETLIB + "/blas/dscal.f", "dscal.f"),
        url(NETLIB + "/blas/ddot.f", "ddot.f"),
        url(NETLIB + "/blas/idamax.f", "idamax.f")]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"archive": "netlib.org/linpack, netlib.org/blas, netlib.org/benchmark"},
    license={"spdx": "NOASSERTION", "status": "public-domain-style (netlib)", "evidence": "netlib distribution terms; LINPACK routines are freely redistributable"},
    language=["Fortran 77"], build_system="gfortran -std=legacy",
    compiler_or_interpreter="gfortran (docker prometheus-fossil-c:bookworm)",
    dependencies=["a Fortran compiler"],
    entry_points=["linpackd -- the 100x100 LU benchmark, reports MFLOPS and a residual check",
                  "dgefa/dgesl -- LU factorise and solve, Level-1 BLAS inner loops"],
    example={"command": "gfortran -std=legacy -O2 -o linpackd linpackd.f && ./linpackd",
             "input": "the benchmark's own generated 100x100 system",
             "output": "MFLOPS plus a residual/norm check the benchmark grades itself against (the ORACLE)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Dongarra, Bunch, Moler, Stewart, LINPACK Users' Guide, SIAM 1979",
                   "Anderson et al., LAPACK Users' Guide, SIAM (3rd ed. 1999) -- supersession + the reason"],
    human_capability_summary={"built_to": "solve dense linear systems and least-squares problems portably and reliably in Fortran, on the vector machines of the late 1970s",
                              "pressure": "limited memory and the arithmetic cost of O(n^3) factorisation on machines whose fast path was long vector operations",
                              "success_means": "an accurate factorisation and solution, with a small residual, at the machine's peak vector rate"},
    known_human_problem_solved="dense linear systems (LU, QR, SVD) in portable Fortran",
    human_environmental_pressure="expensive arithmetic on vector hardware; portability across wildly different machines",
    human_failure_condition="on cache-based machines the Level-1 BLAS inner loops move O(n^3) words through memory and the factorisation becomes MEMORY-bound, running far below peak",
    behavioral_entry_point="factor matrices of growing n with LINPACK dgefa and LAPACK dgetrf in the same process and compare time/MFLOPS as n crosses cache sizes",
    acquisition_tags=["batch09", "loser", "superseded_design", "predecessor", "numerical", "pair_linear_algebra"],
    historical_disposition={
        "state": "SUPERSEDED", "failure_reasons": ["poor_scaling", "superior_rival"],
        "superseded_by": "lapack-reference", "rival_of": "lapack-reference",
        "evidence": [
            {"kind": "successor_documentation", "ref": "LAPACK Users' Guide (SIAM), 'LAPACK supersedes LINPACK and EISPACK'",
             "says": "LAPACK was written to supersede LINPACK and EISPACK, providing the same functionality with better performance."},
            {"kind": "successor_documentation", "ref": "LAPACK Users' Guide, design rationale / netlib LAPACK FAQ",
             "says": "LINPACK and EISPACK are based on vector (Level-1 BLAS) operations whose memory-reference pattern performs poorly on machines with cache and multi-level memory hierarchies; LAPACK restructures the algorithms to use blocked Level-3 BLAS so that data is reused in cache."}]},
    lineage_relations=[{"relation": "superseded", "to": "lapack-reference", "note": "same problems, restructured for memory hierarchy; the human record states the reason"},
                       {"relation": "shares_ancestor_with", "to": "fftpack-netlib", "note": "both netlib Fortran numerical libraries of the same era"}])

spec("lapack-reference",
    canonical_name="LAPACK (reference) -- the blocked successor that superseded LINPACK and EISPACK",
    aliases=["LAPACK", "dgetrf", "Reference-LAPACK"],
    lineage="LAPACK (Anderson et al., 1992-) rewrote the LINPACK/EISPACK functionality around BLOCKED algorithms expressed in Level-3 BLAS (matrix-matrix), so that data loaded into cache is reused O(block) times. It is the WINNER of this pair: same mathematics, different memory-access structure. Kept here as the rival, so the loser can be compared on a shared problem without Techne deciding why it won.",
    domain=["numerical-linear-algebra", "scientific-computing", "dense-linear-algebra", "successor"],
    era="1992- (LAPACK); this checkout modern",
    version="github.com/Reference-LAPACK/lapack as of 2026-09-13 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/Reference-LAPACK/lapack", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/Reference-LAPACK/lapack"},
    license={"spdx": "BSD-3-Clause", "status": "permissive", "evidence": "LICENSE in the tree"},
    language=["Fortran 90", "C"], build_system="cmake or make (reference BLAS + LAPACK)",
    compiler_or_interpreter="gfortran (docker prometheus-fossil-c:bookworm)",
    dependencies=["a Fortran compiler"],
    entry_points=["dgetrf -- blocked LU factorisation (the Level-3 answer to LINPACK's dgefa)"],
    example={"command": "build reference BLAS+LAPACK, call dgetrf on the same matrices given to dgefa",
             "input": "the shared LU problem", "output": "the same factorisation; time/MFLOPS is the comparable quantity"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Anderson et al., LAPACK Users' Guide, SIAM"],
    human_capability_summary={"built_to": "provide LINPACK/EISPACK functionality at high performance on machines with memory hierarchies, by blocking the algorithms onto Level-3 BLAS",
                              "pressure": "the same O(n^3) arithmetic, but on machines where memory bandwidth, not flops, is the binding constraint",
                              "success_means": "the same numerical answer at a large multiple of the unblocked rate"},
    known_human_problem_solved="high-performance dense linear algebra on cache-based machines",
    human_environmental_pressure="memory hierarchy: data movement costs more than arithmetic",
    human_failure_condition="with a badly chosen block size or an unoptimised BLAS it degenerates toward the unblocked rate",
    behavioral_entry_point="vary the block size (ILAENV) and matrix size and watch the rate move",
    acquisition_tags=["batch09", "successor", "winner_of_pair", "numerical", "pair_linear_algebra"],
    historical_disposition={"state": "ACTIVE", "failure_reasons": [], "superseded_by": "", "rival_of": "linpack-netlib-1979", "evidence": []},
    lineage_relations=[{"relation": "rewrote", "to": "linpack-netlib-1979", "note": "same functionality, blocked for cache"},
                       {"relation": "rewrote", "to": "eispack-netlib-1976", "note": "same functionality, blocked for cache"}])

# ===================== PAIR 1b: EISPACK -- the other half LAPACK replaced ======================
spec("eispack-netlib-1976",
    canonical_name="EISPACK (1976) -- the Fortran eigenvalue package, superseded by LAPACK",
    aliases=["EISPACK", "rs", "tred2", "tql2"],
    lineage="EISPACK (Smith, Boyle, Dongarra, Garbow, Ikebe, Klema, Moler; 1974-1976) was the standard eigenproblem library, itself a Fortran translation of the ALGOL procedures in Wilkinson & Reinsch's Handbook for Automatic Computation. Superseded by LAPACK for the same documented reason as LINPACK: Level-1 BLAS structure performs poorly on memory-hierarchy machines. Its ALGOL ancestry makes it a second, older lineage layer.",
    domain=["numerical-linear-algebra", "eigenproblem", "scientific-computing", "loser"],
    era="1974-1976 (EISPACK); ALGOL originals 1971; superseded from 1992",
    version="netlib eispack routines as served 2026-09-13",
    source_origin={"artifacts": [
        url(NETLIB + "/eispack/rs.f", "rs.f"),
        url(NETLIB + "/eispack/tred2.f", "tred2.f"),
        url(NETLIB + "/eispack/tql2.f", "tql2.f"),
        url(NETLIB + "/eispack/tred1.f", "tred1.f"),
        url(NETLIB + "/eispack/tqlrat.f", "tqlrat.f"),
        url(NETLIB + "/eispack/pythag.f", "pythag.f"),
        url(NETLIB + "/eispack/epslon.f", "epslon.f"),
        url(NETLIB + "/eispack/tql1.f", "tql1.f")]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"archive": "netlib.org/eispack"},
    license={"spdx": "NOASSERTION", "status": "public-domain-style (netlib)", "evidence": "netlib distribution terms"},
    language=["Fortran 77"], build_system="gfortran -std=legacy",
    compiler_or_interpreter="gfortran (docker prometheus-fossil-c:bookworm)",
    dependencies=["a Fortran compiler"],
    entry_points=["rs -- all eigenvalues/eigenvectors of a real symmetric matrix (via tred2 + tql2)"],
    example={"command": "gfortran -std=legacy rs.f tred2.f tql2.f driver.f && ./a.out",
             "input": "a small real symmetric matrix with known spectrum",
             "output": "its eigenvalues, checkable against the known values (the ORACLE)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Smith et al., Matrix Eigensystem Routines -- EISPACK Guide, Springer 1976",
                   "Wilkinson & Reinsch, Handbook for Automatic Computation Vol II, 1971 (the ALGOL originals)",
                   "Anderson et al., LAPACK Users' Guide (supersession)"],
    human_capability_summary={"built_to": "compute eigenvalues and eigenvectors of real and complex matrices reliably, as portable Fortran translations of the certified ALGOL procedures",
                              "pressure": "eigenproblems are iterative and numerically delicate; the algorithms had to be stable across very different floating-point hardware",
                              "success_means": "eigenvalues accurate to working precision with orthogonal eigenvectors"},
    known_human_problem_solved="the symmetric and unsymmetric eigenproblem in portable Fortran",
    human_environmental_pressure="numerical delicacy of iterative eigen-solvers; heterogeneous floating point",
    human_failure_condition="same as LINPACK's: vector-oriented inner loops become memory-bound on cache machines",
    behavioral_entry_point="feed matrices with clustered or degenerate eigenvalues and watch convergence; compare rs against LAPACK dsyev on the same matrix",
    acquisition_tags=["batch09", "loser", "superseded_design", "predecessor", "numerical", "pair_linear_algebra"],
    historical_disposition={
        "state": "SUPERSEDED", "failure_reasons": ["poor_scaling", "superior_rival"],
        "superseded_by": "lapack-reference", "rival_of": "lapack-reference",
        "evidence": [
            {"kind": "successor_documentation", "ref": "LAPACK Users' Guide (SIAM)",
             "says": "LAPACK was designed to supersede LINPACK and EISPACK, providing the same functionality with better performance on modern machines."},
            {"kind": "original_paper", "ref": "Wilkinson & Reinsch, Handbook for Automatic Computation Vol II (1971); EISPACK Guide (1976)",
             "says": "EISPACK routines are Fortran translations of the Handbook's ALGOL eigenvalue procedures."}]},
    lineage_relations=[{"relation": "port_of", "to": "Wilkinson & Reinsch ALGOL procedures (1971)", "note": "Fortran translation of the Handbook"},
                       {"relation": "superseded", "to": "lapack-reference", "note": ""}])

# ===================== PAIR 2: block cipher -- DES (loser) vs AES (winner) =====================
spec("des-reference",
    canonical_name="DES -- the Data Encryption Standard, withdrawn after its key length became breakable",
    aliases=["DES", "FIPS 46", "Data Encryption Standard"],
    lineage="DES (IBM/NSA, adopted as FIPS 46 in 1977) was THE block cipher of the era: 64-bit blocks, a 56-bit key, 16 Feistel rounds. Its structure was never broken in practice; its KEY LENGTH was. The EFF built Deep Crack in 1998 and exhausted the keyspace in days, and NIST ran a public competition whose winner, Rijndael, became AES. Preserved as archival/defensive reference material only -- the fossil is the cipher, not an attack.",
    domain=["cryptography", "block-cipher", "feistel-network", "security", "loser"],
    era="1977 (FIPS 46); broken in practice 1998; withdrawn 2005",
    version="a reference DES implementation (see source_identity)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/tarequeh/DES", "commit": "HEAD"}]},
    source_type="PSEUDOCODE_PLUS_REFERENCE_IMPL",
    source_identity={"repo": "github.com/tarequeh/DES", "specifies": "FIPS 46 DES (tables and rounds as published in the standard)"},
    license={"spdx": "NOASSERTION", "status": "see repo", "evidence": "repository terms"},
    language=["C"], build_system="cc", compiler_or_interpreter="gcc (docker prometheus-fossil-c:bookworm)",
    dependencies=["a C compiler"],
    entry_points=["DES encrypt/decrypt of a 64-bit block under a 56-bit key"],
    example={"command": "encrypt a known plaintext under a known key",
             "input": "a FIPS/standard known-answer test vector",
             "output": "the published ciphertext for that vector (the ORACLE: a known-answer test)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["FIPS PUB 46-3, Data Encryption Standard (withdrawn 2005)",
                   "Electronic Frontier Foundation, Cracking DES, O'Reilly 1998",
                   "FIPS PUB 197, Advanced Encryption Standard (2001)"],
    human_capability_summary={"built_to": "provide a single standard, hardware-friendly block cipher for unclassified US government data",
                              "pressure": "a cipher cheap enough for 1970s hardware yet strong enough to resist analysis, standardised so that different systems could interoperate",
                              "success_means": "ciphertext that only the key holder can invert, and identical output across every conforming implementation"},
    known_human_problem_solved="standardised symmetric encryption",
    human_environmental_pressure="an adversary with growing compute; a key length fixed in 1977 against hardware that kept getting cheaper",
    human_failure_condition="the 56-bit keyspace became exhaustively searchable -- EFF's Deep Crack recovered keys in days in 1998, and the standard was withdrawn",
    behavioral_entry_point="run the known-answer vectors; vary rounds to watch avalanche; the failure is economic (keyspace size), not structural",
    acquisition_tags=["batch09", "loser", "superseded_design", "security", "archival_only", "pair_cipher"],
    historical_disposition={
        "state": "OBSOLETED_BY_ENVIRONMENT", "failure_reasons": ["security_weakness"],
        "superseded_by": "tiny-aes-c", "rival_of": "tiny-aes-c",
        "evidence": [
            {"kind": "standards_history", "ref": "NIST FIPS 46-3 withdrawal (2005); FIPS 197 (AES, 2001)",
             "says": "NIST withdrew the DES standard and replaced it with AES, selected through a public competition."},
            {"kind": "retrospective", "ref": "Electronic Frontier Foundation, Cracking DES (O'Reilly, 1998)",
             "says": "EFF's purpose-built Deep Crack machine recovered DES keys by exhaustive search in days, demonstrating the 56-bit key was too short."}]},
    lineage_relations=[{"relation": "superseded", "to": "tiny-aes-c", "note": "AES (Rijndael) replaced DES by NIST competition"}])

spec("tiny-aes-c",
    canonical_name="AES (tiny-AES-c) -- the Rijndael successor that replaced DES",
    aliases=["AES", "Rijndael", "tiny-AES"],
    lineage="Rijndael (Daemen & Rijmen) won the NIST AES competition and became FIPS 197 in 2001, replacing DES. Not a Feistel network but a substitution-permutation network over GF(2^8), with 128/192/256-bit keys. Kept as the WINNER of the cipher pair so the loser can be compared on shared test vectors.",
    domain=["cryptography", "block-cipher", "substitution-permutation-network", "security", "successor"],
    era="1998 (Rijndael); FIPS 197 in 2001",
    version="github.com/kokke/tiny-AES-c as of 2026-09-13 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/kokke/tiny-AES-c", "commit": "HEAD"}]},
    source_type="PSEUDOCODE_PLUS_REFERENCE_IMPL",
    source_identity={"repo": "github.com/kokke/tiny-AES-c", "specifies": "FIPS 197 AES"},
    license={"spdx": "Unlicense", "status": "public-domain", "evidence": "unlicense.txt in the tree"},
    language=["C"], build_system="make / cc", compiler_or_interpreter="gcc (docker prometheus-fossil-c:bookworm)",
    dependencies=["a C compiler"],
    entry_points=["AES-128/192/256 ECB/CBC/CTR encrypt and decrypt; the repo ships FIPS-197 self-tests"],
    example={"command": "make test", "input": "the FIPS-197 / NIST known-answer vectors",
             "output": "the published ciphertexts (the ORACLE)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["FIPS PUB 197 (AES)", "Daemen & Rijmen, The Design of Rijndael"],
    human_capability_summary={"built_to": "replace DES with a cipher whose key length and structure resist foreseeable attack, efficient in both hardware and software",
                              "pressure": "the same adversary that killed DES, plus a public competition demanding analysable security margins",
                              "success_means": "matching the FIPS-197 vectors with no practical attack better than brute force on a 128-bit key"},
    known_human_problem_solved="standardised symmetric encryption after DES",
    human_environmental_pressure="adversarial cryptanalysis; an open selection process",
    human_failure_condition="implementation-level leakage (timing/cache side channels) rather than a break of the cipher",
    behavioral_entry_point="run the FIPS vectors; compare structure against DES on the same plaintext/key sizes",
    acquisition_tags=["batch09", "successor", "winner_of_pair", "security", "pair_cipher"],
    historical_disposition={"state": "ACTIVE", "failure_reasons": [], "superseded_by": "", "rival_of": "des-reference", "evidence": []},
    lineage_relations=[{"relation": "superseded", "to": "des-reference", "note": "AES replaced DES as the US standard"}])

# ===================== SOLO: MD5 -- a hash whose security claim was broken ====================
spec("md5-rfc1321",
    canonical_name="MD5 (RFC 1321 reference implementation) -- a hash function whose collision resistance was broken",
    aliases=["MD5", "RFC 1321"],
    lineage="MD5 (Rivest, 1992, RFC 1321) was the default cryptographic hash for a decade: 128-bit digest, Merkle-Damgard over a 512-bit block compression function. Wang et al. published practical collisions in 2004-2005, and RFC 6151 records that MD5 is no longer acceptable where collision resistance is required. The fossil is the RFC's own reference C code -- the standard and its implementation in one artifact.",
    domain=["cryptography", "hash-function", "merkle-damgard", "security", "loser"],
    era="1992 (RFC 1321); collisions demonstrated 2004-2005; deprecated by RFC 6151 (2011)",
    version="RFC 1321 text including the reference implementation (appendix)",
    source_origin={"artifacts": [url("https://www.ietf.org/rfc/rfc1321.txt", "rfc1321.txt")]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"archive": "ietf.org/rfc/rfc1321.txt", "note": "the RFC carries the reference implementation in its appendix"},
    license={"spdx": "NOASSERTION", "status": "RSA Data Security reference-implementation licence in the RFC", "evidence": "RFC 1321 appendix header"},
    language=["C", "RFC text"], build_system="cc (extract the appendix sources)",
    compiler_or_interpreter="gcc (docker prometheus-fossil-c:bookworm)",
    dependencies=["a C compiler"],
    entry_points=["MD5 of a byte string; the RFC ships its own test suite of known digests"],
    example={"command": "compile the appendix reference code and run its test driver",
             "input": "the RFC 1321 test suite strings (\"\", \"a\", \"abc\", ...)",
             "output": "the digests printed IN the RFC (the ORACLE: the standard grades itself)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["RFC 1321, The MD5 Message-Digest Algorithm",
                   "RFC 6151, Updated Security Considerations for MD5 and HMAC-MD5",
                   "Wang & Yu, How to Break MD5 and Other Hash Functions, EUROCRYPT 2005"],
    human_capability_summary={"built_to": "produce a short fixed-length fingerprint of a message that is infeasible to forge or collide",
                              "pressure": "fingerprints had to be cheap enough to hash whole files while resisting an adversary searching for two messages with one digest",
                              "success_means": "matching the RFC's published digests, and no feasible way to find two messages sharing one"},
    known_human_problem_solved="message fingerprinting / integrity checking",
    human_environmental_pressure="an adversary free to choose both messages (collision), with growing compute and improving differential cryptanalysis",
    human_failure_condition="collision resistance fell -- Wang et al. produced colliding pairs; MD5 is now unsuitable for signatures or certificates while remaining a correct checksum",
    behavioral_entry_point="run the RFC's own test vectors; the failure is not visible in them at all, which is itself the point -- a broken hash still passes its published tests",
    acquisition_tags=["batch09", "loser", "security", "archival_only", "standard_and_impl"],
    historical_disposition={
        "state": "SUPERSEDED", "failure_reasons": ["security_weakness", "incorrect_assumptions"],
        "superseded_by": "SHA-2 family", "rival_of": "",
        "evidence": [
            {"kind": "standards_history", "ref": "RFC 6151 (2011), Updated Security Considerations for MD5 and HMAC-MD5",
             "says": "MD5 is no longer acceptable where collision resistance is required, and new protocol designs should not use it."},
            {"kind": "original_paper", "ref": "Wang & Yu, How to Break MD5 and Other Hash Functions, EUROCRYPT 2005",
             "says": "Practical collisions for MD5 can be constructed, breaking its collision resistance."}]},
    lineage_relations=[{"relation": "superseded", "to": "the SHA-2 family", "note": "deployment moved to SHA-256 after the collision results"}])

# ===================== SOLO: SPDY -- superseded by the standard it became =====================
spec("spdylay",
    canonical_name="SPDY (spdylay) -- the experimental protocol that became HTTP/2 and was then retired",
    aliases=["SPDY", "spdylay"],
    lineage="SPDY (Google, 2009) attacked HTTP/1.1 head-of-line blocking with multiplexed streams, header compression and prioritisation over one TLS connection. It worked, and the IETF took it as the BASIS for HTTP/2 (RFC 7540). Its authors then deprecated it: SPDY is a loser of an unusual kind -- defeated by its own successor, having won the argument. spdylay is Tatsuhiro Tsujikawa's C implementation (the ancestor of nghttp2).",
    domain=["networks", "protocol", "http", "multiplexing", "loser"],
    era="2009-2015 (SPDY); HTTP/2 published 2015; SPDY removed from Chrome 2016",
    version="github.com/tatsuhiro-t/spdylay as of 2026-09-13 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/tatsuhiro-t/spdylay", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/tatsuhiro-t/spdylay"},
    license={"spdx": "MIT", "status": "permissive", "evidence": "LICENSE in the tree"},
    language=["C"], build_system="autotools (autoreconf + configure + make)",
    compiler_or_interpreter="gcc (docker prometheus-fossil-c:bookworm)",
    dependencies=["a C compiler; zlib for header compression; autotools"],
    entry_points=["libspdylay -- frame a SPDY session; the tree ships unit tests for framing/compression"],
    example={"command": "build and run the shipped tests",
             "input": "SPDY frames", "output": "round-tripped frames; the tests are the ORACLE"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["RFC 7540, Hypertext Transfer Protocol Version 2 (HTTP/2)",
                   "Chromium blog, Hello HTTP/2, Goodbye SPDY (2015)"],
    human_capability_summary={"built_to": "remove HTTP/1.1's head-of-line blocking by multiplexing many requests over one connection with compressed headers",
                              "pressure": "pages needing dozens of round-trips over high-latency links; browsers opening many TCP connections to work around it",
                              "success_means": "fewer connections and lower page load time at the same bandwidth"},
    known_human_problem_solved="HTTP latency over high-latency links",
    human_environmental_pressure="latency and connection limits; TCP head-of-line blocking under loss",
    human_failure_condition="retired by its own authors once its ideas were standardised as HTTP/2; deployments moved off it",
    behavioral_entry_point="frame the same request set under SPDY and HTTP/2 header compression and compare bytes on the wire",
    acquisition_tags=["batch09", "loser", "superseded_design", "networks", "protocol"],
    historical_disposition={
        "state": "SUPERSEDED", "failure_reasons": ["superior_rival"],
        "superseded_by": "HTTP/2 (RFC 7540) / nghttp2", "rival_of": "",
        "evidence": [
            {"kind": "standards_history", "ref": "RFC 7540 (HTTP/2), May 2015",
             "says": "HTTP/2 was developed from SPDY as its starting point and supersedes it as the standardised protocol."},
            {"kind": "release_notes", "ref": "Chromium blog, 'Hello HTTP/2, Goodbye SPDY' (Feb 2015)",
             "says": "Google announced it would remove SPDY support from Chrome in favour of HTTP/2."}]},
    lineage_relations=[{"relation": "superseded", "to": "HTTP/2 (RFC 7540)", "note": "SPDY was the basis of the standard that replaced it"}])

# ===================== SOLO: OpenSSL 1.0.1f -- before/observed/replacement =====================
spec("openssl-1.0.1f-heartbleed",
    canonical_name="OpenSSL 1.0.1f -- the last release carrying Heartbleed (CVE-2014-0160)",
    aliases=["Heartbleed", "CVE-2014-0160", "openssl-1.0.1f"],
    lineage="OpenSSL's TLS heartbeat extension (RFC 6520) accepted a caller-supplied payload LENGTH and copied that many bytes back without checking it against the record actually received. 1.0.1 through 1.0.1f carry the defect; 1.0.1g fixes it with a bounds check. Preserved as the BEFORE-FAILURE body of a documented failure whose replacement is one released version away. Archival only: this fossil exists so the defect can be read in its original world, and the vault carries no exploit for it.",
    domain=["cryptography", "tls", "security", "memory-safety", "loser"],
    era="2012-2014 (1.0.1 line); disclosed 2014-04-07; fixed in 1.0.1g",
    version="OpenSSL 1.0.1f source tarball (openssl.org archive)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://www.openssl.org/source/old/1.0.1/openssl-1.0.1f.tar.gz", "filename": "openssl-1.0.1f.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"archive": "openssl.org/source/old/1.0.1", "file": "openssl-1.0.1f.tar.gz"},
    license={"spdx": "OpenSSL", "status": "OpenSSL/SSLeay dual licence", "evidence": "LICENSE in the tree"},
    language=["C"], build_system="./config && make (not built here)",
    compiler_or_interpreter="not executed in the vault (archival)",
    dependencies=["a C compiler"],
    entry_points=["ssl/d1_both.c and ssl/t1_lib.c -- the heartbeat request/response path carrying the unchecked length"],
    example={"command": "read ssl/d1_both.c dtls1_process_heartbeat / tls1_process_heartbeat",
             "input": "the preserved source", "output": "the missing bounds check, in its original context"},
    environment={"runner": "none (archival source)"},
    upstream_docs=["CVE-2014-0160", "OpenSSL Security Advisory 07 Apr 2014", "RFC 6520 (TLS Heartbeat Extension)"],
    human_capability_summary={"built_to": "keep a TLS session alive and discover path MTU without renegotiating, per RFC 6520",
                              "pressure": "long-lived TLS sessions over NAT/firewall timeouts needed a cheap liveness probe",
                              "success_means": "a heartbeat reply echoing the peer's payload"},
    known_human_problem_solved="TLS session liveness (heartbeat)",
    human_environmental_pressure="untrusted input crossing a trust boundary into a memory-unsafe language",
    human_failure_condition="the responder trusted an attacker-supplied length field and echoed adjacent process memory -- disclosed as Heartbleed, fixed by bounds-checking in 1.0.1g",
    behavioral_entry_point="diff 1.0.1f against 1.0.1g in ssl/d1_both.c: the failure and its repair are a few lines apart",
    acquisition_tags=["batch09", "loser", "security", "archival_only", "before_failure", "documented_pathology"],
    historical_disposition={
        "state": "FAILED", "failure_reasons": ["security_weakness", "brittleness"],
        "superseded_by": "OpenSSL 1.0.1g", "rival_of": "",
        "evidence": [
            {"kind": "release_notes", "ref": "OpenSSL Security Advisory, 07 April 2014 (CVE-2014-0160)",
             "says": "A missing bounds check in the TLS heartbeat extension allows disclosure of up to 64kB of process memory; affected versions are 1.0.1 through 1.0.1f, fixed in 1.0.1g."},
            {"kind": "standards_history", "ref": "RFC 6520, TLS Heartbeat Extension",
             "says": "The heartbeat response must echo the payload of the request; the length handling is where the implementation failed."}]},
    lineage_relations=[{"relation": "historical_version_of", "to": "OpenSSL 1.0.1g (the fix)", "note": "before-failure body; the replacement is one release later"}])


def main():
    from .. import record as R
    for rec in S:
        try:
            old = R.load(rec["specimen_id"])
            for k in ("run_classification", "test_classification", "receipts", "hashes", "acquisition_date",
                      "observability", "nyx_handoff"):
                if old.get(k):
                    rec[k] = old[k]
        except FileNotFoundError:
            pass
        probs = R.validate(rec)
        R.save(rec)
        print("%-30s %s" % (rec["specimen_id"], "ok" if not probs else probs))
    print(len(S), "records")


if __name__ == "__main__":
    main()
