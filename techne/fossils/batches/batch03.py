"""Batch 03 of the fossil harvest (2026-09-12): records. python -m techne.fossils.batches.batch03

Pushes into the axes the 22-specimen vault was thin on, per the global-archaeology charter:
HARDWARE/logic (was empty), OS survival machinery, more language machines, deeper numerical
Fortran lineages, estimation/uncertainty, compression families, artificial life, and
unconventional computation. Includes the first "one specimen, many versions" pair (the LZW
compress lineage: compress 4.2.4 -> ncompress 5.0). Anti-canon and negative/superseded
machinery welcome. Nothing here is classified into organs.
"""
from __future__ import annotations

import json
import urllib.request

from .. import record

NL = "https://www.netlib.org/%s/%s"


def _netlib(pkg, extras):
    """Live-enumerate a netlib package directory's .f files at record-build time (the package
    has no tarball endpoint; per-file is how minpack was preserved in batch 01)."""
    h = urllib.request.urlopen("https://www.netlib.org/%s/" % pkg, timeout=40).read().decode("latin1")
    import re
    fs = sorted(set(re.findall(r'href="([a-zA-Z0-9_.]+\.f)"', h)))
    files = fs + [e for e in extras if ('href="%s"' % e) in h]
    # Companion routines some netlib index pages do not link but the routines require at link
    # time (real upstream files, acquired rather than shimmed):
    companions = {"eispack": ["epslon.f", "pythag.f", "cdiv.f", "csroot.f"]}
    for c in companions.get(pkg, []):
        if c not in files:
            files.append(c)
    arts = [{"kind": "url", "url": NL % (pkg, f), "filename": f, "extract": False} for f in files]
    # d1mach (machine constants) lives in netlib/blas, not the quadpack dir, but quadpack needs it:
    if pkg == "quadpack":
        # QUADPACK's companion numerical deps that live outside its own directory (real upstream):
        for u, fn in [("https://www.netlib.org/blas/d1mach.f", "d1mach.f"),
                      ("https://www.netlib.org/blas/r1mach.f", "r1mach.f"),
                      ("https://www.netlib.org/linpack/dgtsl.f", "dgtsl.f"),
                      ("https://www.netlib.org/linpack/sgtsl.f", "sgtsl.f")]:
            arts.append({"kind": "url", "url": u, "filename": fn, "extract": False})
    return arts


S = []

# ---- P1 HARDWARE / LOGIC (axis was empty) --------------------------------------------------
S.append(record.skeleton("picorv32",
    canonical_name="PicoRV32 -- a size-optimised RISC-V CPU core in Verilog (Clifford Wolf / YosysHQ)",
    aliases=["picorv32", "PicoRV32"],
    lineage="PicoRV32 (2015-, Clifford Wolf): a small RV32I[MC] processor as synthesisable Verilog with a self-checking testbench; the reference small core of the open RISC-V / Yosys ecosystem",
    domain=["hardware", "cpu", "verilog", "sequential-logic", "finite-state-machine", "processor"], era="2015-",
    version="github.com/YosysHQ/picorv32 main branch as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/YosysHQ/picorv32", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/YosysHQ/picorv32"},
    license={"spdx": "ISC", "status": "permissive", "evidence": "LICENSE in repo"},
    language=["Verilog"], build_system="iverilog (simulation)", compiler_or_interpreter="Icarus Verilog (docker prometheus-fossil-hw)",
    dependencies=["iverilog", "a RISC-V gcc for the firmware test (optional)"],
    entry_points=["picorv32.v (the core); testbench.v / picorv32_tb"],
    example={"command": "iverilog -o tb testbench.v picorv32.v && vvp tb", "input": "a compiled firmware image or the built-in test", "output": "the testbench's PASS/trap report and register trace"},
    environment={"runner": "docker", "image": "prometheus-fossil-hw:bookworm"},
    upstream_docs=["github.com/YosysHQ/picorv32 README", "RISC-V ISA spec"],
    human_capability_summary={"built_to": "execute the RISC-V RV32I instruction set as a small synthesisable processor -- fetch, decode, a state-machine control path, register file, and an ALU -- for FPGAs and teaching",
                              "pressure": "silicon area and timing: the core trades cycles-per-instruction for a tiny gate count, an explicit area/speed decision",
                              "success_means": "correct execution of RISC-V programs (its self-checking testbench passes) within the gate budget"},
    known_human_problem_solved="running a real instruction set on minimal hardware"))

S.append(record.skeleton("espresso-logic",
    canonical_name="Espresso -- two-level Boolean logic minimizer (UC Berkeley)",
    aliases=["espresso", "espresso-logic", "espresso-ii"],
    lineage="Espresso (1980s, Brayton/Hachtel/McMullen/Sangiovanni-Vincentelli, UC Berkeley): heuristic two-level logic minimisation (EXPAND / REDUCE / IRREDUNDANT over cube covers); the tool that defined PLA minimisation and seeded logic synthesis",
    domain=["hardware", "logic-minimization", "boolean-network", "combinational-logic", "optimization"], era="1980s (this a maintained rebuild)",
    version="github.com/classabbyamp/espresso-logic master as of 2026-09-12 (a build-fixed mirror of the Berkeley source)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/classabbyamp/espresso-logic", "commit": "HEAD"}]},
    source_type="LATER_SAME_LINEAGE_RELEASE", source_identity={"repo": "github.com/classabbyamp/espresso-logic", "ancestry": "UC Berkeley Espresso-II"},
    license={"spdx": "custom BSD-like (Berkeley Espresso terms)", "status": "permissive", "evidence": "COPYING in repo"},
    language=["C"], build_system="make (in espresso-src/)", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["espresso <pla-file> (Berkeley PLA format on stdin/argument)"],
    example={"command": "espresso two_bit_adder.pla", "input": "a truth table in Berkeley PLA (.pla) format", "output": "the minimised sum-of-products cover"},
    environment={"runner": "docker", "image": "prometheus-fossil-hw:bookworm"},
    upstream_docs=["Brayton et al., Logic Minimization Algorithms for VLSI Synthesis, Kluwer 1984"],
    human_capability_summary={"built_to": "minimise a two-level Boolean function (a truth table / PLA) to the fewest product terms, so the circuit that implements it is smaller and faster",
                              "pressure": "the exponential number of prime implicants; exact minimisation (Quine-McCluskey) is intractable, so Espresso is a heuristic that gets near-optimal covers fast",
                              "success_means": "a correct, much smaller SOP cover of the same Boolean function, in seconds on functions that defeat exact methods"},
    known_human_problem_solved="two-level Boolean minimisation for hardware synthesis"))

# ---- P2 OS SURVIVAL MACHINERY --------------------------------------------------------------
S.append(record.skeleton("dlmalloc",
    canonical_name="dlmalloc -- Doug Lea's memory allocator",
    aliases=["dlmalloc", "Doug Lea malloc", "malloc.c"],
    lineage="dlmalloc (1987-, Doug Lea): the boundary-tag, binned free-list general-purpose allocator behind glibc's ptmalloc and countless embedded mallocs; a whole lineage of heap management in one file",
    domain=["operating-systems", "memory-allocation", "data-structures", "resource-management"], era="1987-",
    version="gee.cs.oswego.edu/pub/misc/malloc.c as served 2026-09-12 (the file carries its own version string)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://gee.cs.oswego.edu/pub/misc/malloc.c", "filename": "malloc.c", "extract": False}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"site": "gee.cs.oswego.edu/pub/misc", "author": "Doug Lea"},
    license={"spdx": "CC0-1.0 / public-domain (Lea released it to the public domain)", "status": "unrestricted", "evidence": "malloc.c header"},
    language=["C"], build_system="cc (compile as a translation unit and link, or #define USE_DL_PREFIX)", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["dlmalloc / dlfree / dlrealloc (the allocator API)"],
    example={"command": "a Techne driver: many random malloc/free of varied sizes, then check no corruption and report peak", "input": "an allocation workload", "output": "all pointers distinct+writable, freed cleanly"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["gee.cs.oswego.edu/dl/html/malloc.html"],
    human_capability_summary={"built_to": "hand out and reclaim variable-size blocks of memory from a heap, fast, with low fragmentation, using boundary tags and size-binned free lists",
                              "pressure": "fragmentation vs speed vs footprint under adversarial allocation patterns; every general program depends on it being fast and not leaking",
                              "success_means": "correct non-overlapping blocks, quick allocation/free, and low fragmentation across real workloads"},
    known_human_problem_solved="general-purpose dynamic memory allocation"))

S.append(record.skeleton("bdwgc-8.2.6",
    canonical_name="Boehm-Demers-Weiser conservative garbage collector 8.2.6",
    aliases=["bdwgc", "Boehm GC", "libgc"],
    lineage="BDWGC (1988-, Hans Boehm, Alan Demers, Mark Weiser): a conservative mark-sweep (optionally generational, incremental, parallel) garbage collector usable as a drop-in malloc replacement for C/C++; the GC behind many language runtimes",
    domain=["operating-systems", "garbage-collection", "memory-management", "mark-sweep"], era="1988 (8.2.6 rel. 2024)",
    version="git tag v8.2.6, github.com/ivmai/bdwgc",
    source_origin={"artifacts": [{"kind": "url", "url": "https://github.com/ivmai/bdwgc/archive/refs/tags/v8.2.6.tar.gz", "filename": "bdwgc-8.2.6.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/ivmai/bdwgc", "tag": "v8.2.6"},
    license={"spdx": "MIT-style (Boehm GC license)", "status": "permissive", "evidence": "LICENSE in tarball"},
    language=["C"], build_system="./autogen.sh && ./configure && make (or cmake)", compiler_or_interpreter="gcc 12 + autotools (docker bookworm-lang)",
    dependencies=["libatomic_ops (bundled or system)", "autotools"],
    entry_points=["GC_malloc / GC_free_ignored; the shipped test/gctest"],
    example={"command": "make check (runs gctest)", "input": "the collector's own stress test", "output": "gctest completes without leak/corruption"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Boehm & Weiser, Garbage Collection in an Uncooperative Environment, SP&E 1988", "hboehm.info/gc"],
    human_capability_summary={"built_to": "reclaim unreachable heap memory automatically in a language (C/C++) that gives the collector no cooperation -- scanning the stack and heap conservatively for anything that looks like a pointer",
                              "pressure": "no type information about what is a pointer; must never free reachable memory (soundness) while freeing most garbage (completeness) without stopping the program too long",
                              "success_means": "no use-after-free of live objects, bounded pause times, and most garbage reclaimed; gctest passes"},
    known_human_problem_solved="automatic memory reclamation without language support"))

S.append(record.skeleton("xv6-riscv",
    canonical_name="xv6-riscv -- MIT teaching operating system (RISC-V port)",
    aliases=["xv6", "xv6-riscv"],
    lineage="xv6 (2006-, MIT PDOS): a re-implementation of Sixth Edition Unix for teaching -- a real preemptive multiprocess kernel with a scheduler, virtual memory, a log-structured crash-safe filesystem, pipes and traps, small enough to read entirely",
    domain=["operating-systems", "process-scheduling", "virtual-memory", "filesystem", "journaling", "kernel"], era="2006 (riscv port 2019-)",
    version="github.com/mit-pdos/xv6-riscv riscv branch as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/mit-pdos/xv6-riscv", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/mit-pdos/xv6-riscv"},
    license={"spdx": "MIT", "status": "permissive", "evidence": "LICENSE in repo"},
    language=["C", "RISC-V assembly"], build_system="make (needs a riscv64 gcc cross-toolchain and qemu-system-riscv64)", compiler_or_interpreter="riscv64-linux-gnu-gcc + qemu (NOT built this pass)",
    dependencies=["gcc-riscv64", "qemu-system-riscv64"], entry_points=["make qemu (boots the kernel in qemu, drops to the xv6 shell)"],
    example={"command": "make qemu ; then 'ls', 'usertests'", "input": "shell commands / the usertests program", "output": "the shell session; usertests OK"},
    environment={"runner": "none this pass -- SOURCE pinned; the riscv cross-toolchain + qemu world is a later emulated-run item (RUNNABLE_EMULATED candidate)"},
    upstream_docs=["Cox, Kaashoek, Morris, xv6: a simple, Unix-like teaching operating system (the book)", "pdos.csail.mit.edu/6.828"],
    human_capability_summary={"built_to": "be a complete, readable Unix-like kernel -- schedule processes across cores, give each an isolated virtual address space, and keep a crash-recoverable filesystem -- for students to modify",
                              "pressure": "concurrency (locks, sleep/wakeup), crash safety (the FS log), and isolation (page tables) all at once, in a few thousand readable lines",
                              "success_means": "boots, runs a shell and concurrent user programs, and its usertests pass including crash-recovery of the filesystem"},
    known_human_problem_solved="a working multiprocess operating system kernel"))

# ---- P3 LANGUAGE MACHINES ------------------------------------------------------------------
S.append(record.skeleton("pforth",
    canonical_name="pForth -- a portable ANS Forth in C (Phil Burk)",
    aliases=["pforth"],
    lineage="pForth (1994-, Phil Burk): a portable ANS Forth -- an inner interpreter over a threaded-code dictionary, a data and return stack machine, compiled from C; a concatenative stack-machine runtime",
    domain=["languages", "interpreters", "forth", "stack-machine", "bytecode", "virtual-machine"], era="1994-",
    version="github.com/philburk/pforth master as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/philburk/pforth", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/philburk/pforth"},
    license={"spdx": "0BSD / public-domain-like (pForth license)", "status": "permissive", "evidence": "LICENSE in repo"},
    language=["C", "Forth"], build_system="make (build/unix) or cmake", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["pforth (REPL); pforth -i (build the dictionary)"],
    example={"command": "echo ': sq dup * ; 7 sq . cr bye' | pforth", "input": "Forth words on stdin", "output": "49"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["github.com/philburk/pforth", "ANS Forth standard"],
    human_capability_summary={"built_to": "run Forth -- a concatenative language where a program is a sequence of words operating on an explicit data stack, executed by a tiny threaded inner interpreter that a compiler can extend at runtime",
                              "pressure": "minimal footprint and self-hosting on bare or tiny machines; the language and its compiler are one small extensible dictionary",
                              "success_means": "Forth definitions compile and execute with correct stack effects; the interpreter is portable across machines"},
    known_human_problem_solved="a small, extensible, self-hosting stack-machine language"))

S.append(record.skeleton("femtolisp",
    canonical_name="femtolisp -- a small, fast Scheme-ish Lisp (Jeff Bezanson)",
    aliases=["femtolisp", "flisp"],
    lineage="femtolisp (2008-, Jeff Bezanson): a compact Lisp with a bytecode compiler, mark-and-sweep GC, tail calls and a numeric tower; the language that bootstraps parts of Julia's front end",
    domain=["languages", "interpreters", "lisp", "bytecode", "garbage-collection", "virtual-machine"], era="2008-",
    version="github.com/JeffBezanson/femtolisp master as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/JeffBezanson/femtolisp", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/JeffBezanson/femtolisp"},
    license={"spdx": "BSD-3-Clause", "status": "permissive", "evidence": "LICENSE in repo"},
    language=["C", "Lisp"], build_system="make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["./flisp (REPL); ./flisp file.lsp"],
    example={"command": "echo '(princ (+ 1 2))' | ./flisp", "input": "Lisp forms", "output": "3"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["github.com/JeffBezanson/femtolisp"],
    human_capability_summary={"built_to": "evaluate a Lisp by compiling s-expressions to a compact bytecode and running them on a stack VM with garbage collection -- small and fast enough to embed and to bootstrap a larger language",
                              "pressure": "the interpretation overhead of naive tree-walking; the memory pressure of a numeric tower; correctness of tail calls and GC",
                              "success_means": "Lisp programs compile and run correctly and quickly; its own test suite passes"},
    known_human_problem_solved="a small compiled-to-bytecode Lisp"))

S.append(record.skeleton("gnu-prolog-1.5.0",
    canonical_name="GNU Prolog 1.5.0 -- Daniel Diaz (WAM-compiling Prolog)",
    aliases=["gprolog", "GNU Prolog"],
    lineage="GNU Prolog (1996-, Diaz): an ISO Prolog that COMPILES to a WAM (Warren Abstract Machine) and thence to native code, with a finite-domain constraint solver; a WAM lineage distinct from SWI's VM interpreter",
    domain=["languages", "logic-programming", "prolog", "wam", "unification", "resolution", "constraint-solving"], era="1996 (1.5.0 rel. 2020)",
    version="1.5.0 from gprolog.org (the author's site)",
    source_origin={"artifacts": [{"kind": "url", "url": "http://www.gprolog.org/gprolog-1.5.0.tar.gz", "filename": "gprolog-1.5.0.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"site": "gprolog.org", "release": "1.5.0"},
    license={"spdx": "LGPL-3.0-or-later / GPL-2.0-or-later", "status": "copyleft", "evidence": "COPYING in tarball"},
    language=["C", "Prolog", "WAM assembly"], build_system="./configure && make (bootstraps a WAM->native pipeline; heavier)", compiler_or_interpreter="gcc 12 (docker bookworm-lang)",
    dependencies=[], entry_points=["gprolog (REPL); gplc (compile a .pl to native)"],
    example={"command": "echo \"append(X,[c],[a,b,c]), write(X), nl, halt.\" | gprolog", "input": "Prolog goals", "output": "[a,b] unified"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["gprolog.org", "Warren, An Abstract Prolog Instruction Set, 1983 (the WAM)"],
    human_capability_summary={"built_to": "run Prolog by COMPILING clauses to Warren Abstract Machine instructions and then to native code -- unification, backtracking and SLD resolution as compiled machine operations rather than interpreted",
                              "pressure": "interpreted resolution is slow; the WAM is the classic answer, specialising unification and clause indexing into a register machine",
                              "success_means": "correct goal solving at compiled speed; a WAM the fossil record can hold beside SWI's interpreter"},
    known_human_problem_solved="compiling logic programs to a register (WAM) machine",
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "swipl-9.2.9", "note": "both ISO Prolog; gprolog compiles to WAM->native, SWI interprets a VM"},
                       {"relation": "algorithm_from", "to": "Warren, The WAM, 1983", "note": "Warren Abstract Machine"}]))

# ---- P4 NUMERICAL LINEAGES (netlib Fortran) ------------------------------------------------
for pkg, canon, dom, human in [
    ("fftpack", "FFTPACK -- Paul Swarztrauber's Fortran FFT package (NCAR, 1985)",
     ["scientific-computing", "fft", "signal-processing", "numerical"],
     ("compute forward/inverse real and complex FFTs and related sine/cosine transforms in Fortran 77, mixed-radix",
      "the O(N^2) DFT cost, plus the many transform variants (real, complex, quarter-wave) each needing its own optimised radix passes",
      "transforms invert to the input within round-off; the classic NCAR reference results")),
    ("quadpack", "QUADPACK -- Piessens/de Doncker adaptive quadrature (1983)",
     ["scientific-computing", "numerical-integration", "adaptive", "numerical"],
     ("numerically integrate a function of one variable, ADAPTING the subdivision to the estimated error (Gauss-Kronrod rules + epsilon extrapolation), including singular and infinite ranges",
      "an integrand whose difficulty varies across the interval; fixed rules waste effort or miss features, so the routine spends evaluations where the estimated error is largest",
      "the returned integral is within the requested absolute/relative tolerance, with a returned error estimate; QUADPACK's own test battery")),
    ("eispack", "EISPACK -- matrix eigensystem routines (Argonne, 1976)",
     ["numerical-linear-algebra", "eigensolvers", "scientific-computing", "numerical"],
     ("compute eigenvalues and eigenvectors of real/complex, symmetric/general matrices (the QR, QZ, tridiagonalisation and inverse-iteration lineage), from the Wilkinson-Reinsch Algol procedures",
      "eigenvalue computation is numerically delicate (deflation, shifts, balancing) and predates LAPACK; EISPACK was the standard before LAPACK's blocked rewrite",
      "computed eigenvalues/vectors match reference values to working precision; the driver programs' known results")),
]:
    S.append(record.skeleton(pkg + "-netlib",
        canonical_name=canon, aliases=[pkg],
        lineage="%s (netlib historical distribution): the authoritative Fortran source as served by netlib.org, the authors' own channel" % pkg,
        domain=dom, era="1976-1985",
        version="netlib.org/%s as served 2026-09-12 (per-file; no tarball endpoint)" % pkg,
        source_origin={"artifacts": _netlib(pkg, ["readme", "doc", "changes", "test.f"])},
        source_type="HISTORICAL_ARCHIVE_MIRROR", source_identity={"archive": "netlib.org/%s" % pkg},
        license={"spdx": "public-domain (netlib)", "status": "unrestricted", "evidence": "netlib distribution"},
        language=["Fortran 77"], build_system="gfortran per-routine; test driver where present", compiler_or_interpreter="gfortran (WinLibs 15.2, native)",
        dependencies=[], entry_points=["the package's driver / test program where one is shipped; else the named routines"],
        example={"command": "see recipe.json", "input": "the shipped test.f driver or a Techne driver", "output": "the routine's results"},
        environment={"runner": "native"},
        upstream_docs=["netlib.org/%s" % pkg],
        human_capability_summary={"built_to": human[0], "pressure": human[1], "success_means": human[2]},
        known_human_problem_solved=canon.split("--")[1].strip() if "--" in canon else pkg))

# ---- P5 ESTIMATION / CODING ----------------------------------------------------------------
S.append(record.skeleton("libfec-karn",
    canonical_name="libfec -- Phil Karn's forward-error-correction library (Viterbi + Reed-Solomon)",
    aliases=["libfec", "Karn FEC"],
    lineage="libfec (1995-, Phil Karn KA9Q): optimised VITERBI decoders for convolutional codes (the trellis / add-compare-select / traceback machinery) plus Reed-Solomon; the amateur-radio and deep-space FEC reference",
    domain=["error-correcting-codes", "viterbi", "convolutional-codes", "estimation", "signal-processing", "state-estimation"], era="1995-",
    version="github.com/ka9q/libfec master as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/ka9q/libfec", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/ka9q/libfec", "author": "Phil Karn"},
    license={"spdx": "LGPL-2.1-or-later", "status": "copyleft", "evidence": "LICENSE / source headers"},
    language=["C"], build_system="./configure && make", compiler_or_interpreter="gcc 12 (docker bookworm-lang)",
    dependencies=[], entry_points=["the shipped vtest / vtest27 (Viterbi self-test); rstest (Reed-Solomon)"],
    example={"command": "make && ./vtest27 (encode a random frame, add noise, Viterbi-decode)", "input": "a random bitstream + simulated channel noise", "output": "bit-error rate after decoding vs SNR"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["ka9q.net", "Viterbi 1967"],
    human_capability_summary={"built_to": "recover the most-likely transmitted bit sequence from a noisy convolutionally-coded signal by the Viterbi algorithm (dynamic programming over a trellis of hidden encoder states), and to correct Reed-Solomon block errors",
                              "pressure": "channel noise on band-limited links (satellite, deep space, radio); the decoder must find the maximum-likelihood path through an exponential state space in linear time",
                              "success_means": "decoded bit-error rate at or below the code's theoretical curve for a given SNR; the self-tests pass"},
    known_human_problem_solved="maximum-likelihood decoding of noisy coded signals (hidden-state estimation)"))

# ---- P6 COMPRESSION FAMILIES ---------------------------------------------------------------
S.append(record.skeleton("zlib-1.3.1",
    canonical_name="zlib 1.3.1 -- the DEFLATE reference (Gailly & Adler)",
    aliases=["zlib", "libz"],
    lineage="zlib (1995-, Jean-loup Gailly & Mark Adler): the reference DEFLATE -- LZ77 sliding-window matching + Huffman coding of literals/lengths/distances; the compression behind gzip, PNG, zip and HTTP",
    domain=["compression", "lz77", "huffman", "dictionary-coding"], era="1995 (1.3.1 rel. 2024)",
    version="git tag v1.3.1, github.com/madler/zlib",
    source_origin={"artifacts": [{"kind": "url", "url": "https://github.com/madler/zlib/archive/refs/tags/v1.3.1.tar.gz", "filename": "zlib-1.3.1.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/madler/zlib", "tag": "v1.3.1"},
    license={"spdx": "Zlib", "status": "permissive", "evidence": "LICENSE in tarball"},
    language=["C"], build_system="./configure && make (or make test)", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["libz (deflate/inflate); the shipped example / minigzip"],
    example={"command": "make && make test (example round-trips data through deflate/inflate)", "input": "the test data", "output": "inflate reproduces deflate's input; CRC matches"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["zlib.net", "Deutsch, DEFLATE RFC 1951", "Ziv & Lempel 1977"],
    human_capability_summary={"built_to": "compress and decompress a byte stream losslessly by finding repeated substrings within a 32KB window (LZ77) and entropy-coding the result (Huffman)",
                              "pressure": "the LZ77 vs DEFLATE competitors of the early 90s and the LZW patent; zlib had to be free, fast, and byte-stream-safe",
                              "success_means": "inflate exactly reconstructs deflate's input, at a competitive ratio and speed; the test suite's CRCs match"},
    known_human_problem_solved="lossless general-purpose stream compression (DEFLATE)"))

S.append(record.skeleton("bzip2-1.0.8",
    canonical_name="bzip2 1.0.8 -- Burrows-Wheeler block-sorting compressor (Julian Seward)",
    aliases=["bzip2", "libbz2"],
    lineage="bzip2 (1996-, Julian Seward): the Burrows-Wheeler transform + move-to-front + Huffman pipeline -- a DIFFERENT compression paradigm from LZ, reordering the data so that context redundancy becomes local run redundancy",
    domain=["compression", "burrows-wheeler-transform", "move-to-front", "huffman"], era="1996 (1.0.8 rel. 2019)",
    version="1.0.8 from sourceware.org (the maintainer's site)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz", "filename": "bzip2-1.0.8.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"site": "sourceware.org/pub/bzip2", "release": "1.0.8"},
    license={"spdx": "bzip2-1.0.6 (BSD-like)", "status": "permissive", "evidence": "LICENSE in tarball"},
    language=["C"], build_system="make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["./bzip2 / ./bunzip2; make test"],
    example={"command": "make && make test (compresses and decompresses the shipped sample files)", "input": "sample?.ref", "output": "round-trip reproduces the references"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["sourceware.org/bzip2", "Burrows & Wheeler, A Block-sorting Lossless Data Compression Algorithm, 1994"],
    human_capability_summary={"built_to": "compress losslessly by first BLOCK-SORTING the data (the Burrows-Wheeler transform) so repeated contexts cluster, then move-to-front and Huffman coding the transformed stream",
                              "pressure": "to beat DEFLATE's ratio on text; the BWT trades speed and memory for a better model of long-range redundancy",
                              "success_means": "exact round-trip at a higher ratio than gzip on text; the shipped self-test passes"},
    known_human_problem_solved="block-sorting (BWT) lossless compression"))

S.append(record.skeleton("compress-4.2.4-lzw",
    canonical_name="compress 4.2.4 -- the earlier Unix LZW compress (ncompress lineage)",
    aliases=["compress", "ncompress-4.2.4"],
    lineage="compress 4.x (1985-1992): the Unix LZW compressor as it stood before the long ncompress maintenance era; the EARLY version of the same lineage batch 01 preserved at ncompress 5.0",
    domain=["compression", "lzw", "dictionary-coding"], era="1985-1992",
    version="git tag v4.2.4.6, github.com/vapier/ncompress (the tagged historical 4.2.4 line)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://github.com/vapier/ncompress/archive/refs/tags/v4.2.4.6.tar.gz", "filename": "ncompress-4.2.4.6.tar.gz"}]},
    source_type="HISTORICAL_ARCHIVE_MIRROR", source_identity={"repo": "github.com/vapier/ncompress", "tag": "v4.2.4.6"},
    license={"spdx": "public-domain / permissive (compress headers)", "status": "see LICENSE", "evidence": "tarball"},
    language=["C"], build_system="make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["./compress, ./compress -d"],
    example={"command": "make && ./compress -c compress.c | ./compress -dc | cmp - compress.c && echo ROUNDTRIP_OK", "input": "any file", "output": "identical after round trip"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Welch, A Technique for High-Performance Data Compression, 1984"],
    human_capability_summary={"built_to": "shrink files with adaptive LZW dictionary coding -- the same job as the 5.0 version, in the earlier code, before decades of portability maintenance",
                              "pressure": "1980s bandwidth and disk; the LZW patent that eventually pushed the world to gzip",
                              "success_means": "exact reconstruction; and, as a fossil PAIR with ncompress 5.0, a preserved 30-year span of the SAME lineage for later diff"},
    known_human_problem_solved="lossless LZW compression (early form)",
    lineage_relations=[{"relation": "historical_version_of", "to": "ncompress-5.0-lzw-1985", "note": "compress 4.2.4 (1992) is the earlier form; ncompress 5.0 (2021) is the later. Same LZW lineage, ~30 years apart -- the batch-03 one-specimen-many-versions pair. What changed mechanistically is Nyx's question."}]))

# ---- P11 REPRESENTATION TRANSFORMATION -----------------------------------------------------
S.append(record.skeleton("buddy-bdd",
    canonical_name="BuDDy -- a Binary Decision Diagram package (Jorn Lind-Nielsen)",
    aliases=["buddy", "BuDDy", "BDD"],
    lineage="BuDDy (1996-, Lind-Nielsen, DTU): a reduced ordered Binary Decision Diagram library -- canonical DAG representation of Boolean functions with a unique-table + computed-cache, ITE, and dynamic variable reordering; the representation behind model checkers",
    domain=["representation-transformation", "binary-decision-diagram", "boolean-function", "canonicalization", "symbolic"], era="1996-",
    version="sourceforge buddy latest as of 2026-09-12 (release in hashes)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://sourceforge.net/projects/buddy/files/latest/download", "filename": "buddy.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"project": "sourceforge.net/projects/buddy"},
    license={"spdx": "custom permissive (BuDDy terms)", "status": "permissive", "evidence": "COPYING in tarball"},
    language=["C", "C++"], build_system="./configure && make", compiler_or_interpreter="gcc 12 (docker bookworm-lang)",
    dependencies=[], entry_points=["libbdd; the shipped examples (e.g. the queens / adder demos)"],
    example={"command": "build and run a shipped example, or a Techne driver building (a & b) | (a & c) as a BDD and checking node count / SAT count", "input": "a Boolean formula", "output": "the canonical BDD's node and satisfying-assignment counts"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Lind-Nielsen, BuDDy manual", "Bryant, Graph-Based Algorithms for Boolean Function Manipulation, 1986"],
    human_capability_summary={"built_to": "represent and manipulate Boolean functions as reduced ordered BDDs -- a canonical form where equivalence is pointer identity and operations are memoised graph algorithms -- so huge functions become tractable",
                              "pressure": "the exponential size of truth tables; the right variable order can make a function's BDD linear or exponential, so reordering is itself a search",
                              "success_means": "correct canonical BDDs (equal functions -> identical DAGs), fast ITE/apply, and satisfiability/counting read directly off the graph"},
    known_human_problem_solved="canonical symbolic representation of Boolean functions (BDDs)"))

S.append(record.skeleton("tinycc",
    canonical_name="TinyCC (tcc) -- Fabrice Bellard's small C compiler",
    aliases=["tcc", "tinycc"],
    lineage="TinyCC (2001-, Bellard): a tiny, fast C99 compiler with its own back end (parse -> in-memory code generation -> ELF/executable) that can compile-and-run C in one step; a whole compiler pipeline small enough to read",
    domain=["compilers", "code-generation", "parsing", "languages", "representation-transformation"], era="2001-",
    version="repo.or.cz/tinycc.git mob branch as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://repo.or.cz/tinycc.git", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "repo.or.cz/tinycc.git"},
    license={"spdx": "LGPL-2.1-or-later", "status": "copyleft", "evidence": "COPYING in repo"},
    language=["C"], build_system="./configure && make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["tcc -run prog.c (compile and execute in memory); tcc -o prog prog.c"],
    example={"command": "make && echo 'int main(){return 42;}' > t.c && ./tcc -run t.c; echo exit=$?", "input": "a C program", "output": "the program's behaviour (exit 42)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["bellard.org/tcc", "repo.or.cz/tinycc.git"],
    human_capability_summary={"built_to": "compile C to machine code very fast, in one small program that parses, type-checks, allocates registers and emits an executable (or runs it directly in memory)",
                              "pressure": "gcc's size and slowness; tcc trades optimisation for a compiler that is tiny, fast, and can be used as a scripting back end",
                              "success_means": "correct compilation and execution of C programs; tcc can even compile itself"},
    known_human_problem_solved="fast, tiny C compilation (a full front-to-back compiler)"))

# ---- P7 / P12 ARTIFICIAL LIFE + UNCONVENTIONAL COMPUTATION ---------------------------------
S.append(record.skeleton("corewar-redcode",
    canonical_name="Core War (Redcode / MARS) -- warring programs in a virtual machine",
    aliases=["corewar", "Core War", "Redcode", "MARS"],
    lineage="Core War (1984, A.K. Dewdney): two or more programs written in Redcode run in a shared circular memory on the Memory Array Redcode Simulator (MARS); they copy, bomb and evade each other until one survives -- a self-replication / competition substrate that predates and prefigures artificial life",
    domain=["artificial-life", "virtual-machine", "self-replication", "competition", "unconventional-computation", "game"], era="1984-",
    version="github.com/rodrigosetti/corewar master as of 2026-09-12 (a Redcode MARS implementation; commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/rodrigosetti/corewar", "commit": "HEAD"}]},
    source_type="FAITHFUL_PORT",
    source_identity={"repo": "github.com/rodrigosetti/corewar", "ancestry": "Dewdney's Core War / ICWS Redcode standard"},
    license={"spdx": "see repo LICENSE", "status": "read before redistribution", "evidence": "repo"},
    language=["Python"], build_system="none (interpreted)", compiler_or_interpreter="CPython (docker or native)",
    dependencies=["python3"], entry_points=["the MARS simulator run on two Redcode warriors (e.g. Imp vs Dwarf)"],
    example={"command": "run the simulator with two shipped/standard warriors (Imp: a single self-copying instruction; Dwarf: a bomber)", "input": "two Redcode programs", "output": "the surviving warrior / tie after N cycles"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Dewdney, Core War, Scientific American 1984", "ICWS Redcode standard"],
    human_capability_summary={"built_to": "run competing self-modifying programs in a shared virtual memory and see which survives -- a substrate where programs copy themselves, attack rivals' code, and defend, entirely inside a tiny instruction set",
                              "pressure": "a fixed shared memory and a single CPU shared round-robin; a warrior must replicate or damage others faster than it is damaged",
                              "success_means": "in its native domain, surviving longer than the opponent; as a fossil, a running self-replication/competition VM Nyx can perturb"},
    known_human_problem_solved="a virtual battleground for self-replicating, competing programs"))

S.append(record.skeleton("avida",
    canonical_name="Avida -- a digital-evolution research platform (Devosoft / Ofria lab)",
    aliases=["avida"],
    lineage="Avida (1993-, Adami/Ofria/Brown, later Devosoft): a platform of self-replicating computer programs (digital organisms) that mutate, compete for CPU time, and evolve to perform logic tasks for rewards; the workhorse of experimental digital evolution",
    domain=["artificial-life", "digital-evolution", "self-replication", "genetic-programming", "unconventional-computation"], era="1993-",
    version="github.com/devosoft/avida master as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/devosoft/avida", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/devosoft/avida"},
    license={"spdx": "GPL-3.0 / Apache-2.0 (mixed; see COPYING)", "status": "see COPYING", "evidence": "repo"},
    language=["C++"], build_system="cmake (heavy)", compiler_or_interpreter="g++ + cmake (NOT built this pass)",
    dependencies=["cmake", "a C++ toolchain"], entry_points=["avida (runs a population from a config + ancestor genome)"],
    example={"command": "avida -c avida.cfg (evolve a population from the default ancestor)", "input": "config + ancestral genome", "output": "population statistics over generations; evolved genomes"},
    environment={"runner": "none this pass -- SOURCE pinned; heavy cmake build deferred (RUNNABLE candidate later)"},
    upstream_docs=["Ofria & Wilke, Avida: A software platform for research in computational evolutionary biology, Artificial Life 2004", "Lenski et al., The evolutionary origin of complex features, Nature 2003"],
    human_capability_summary={"built_to": "let self-replicating programs (digital organisms) mutate and compete for CPU cycles and memory, rewarding those that evolve to compute logic functions -- an instrumented Petri dish for open-ended evolution",
                              "pressure": "finite CPU and space; an organism must copy its own genome faster and more accurately than rivals while the reward landscape selects for new computation",
                              "success_means": "in its domain, evolving populations that acquire new functions from mutation and selection; the published Avida experiments reproduce"},
    known_human_problem_solved="controlled experiments in the evolution of computation"))


def main():
    from .. import record as R
    for rec in S:
        try:
            old = R.load(rec["specimen_id"])
            for k in ("run_classification", "test_classification", "receipts", "hashes", "acquisition_date"):
                if old.get(k):
                    rec[k] = old[k]
        except FileNotFoundError:
            pass
        probs = R.validate(rec)
        R.save(rec)
        print("%-28s %s" % (rec["specimen_id"], "ok" if not probs else probs))


if __name__ == "__main__":
    main()
