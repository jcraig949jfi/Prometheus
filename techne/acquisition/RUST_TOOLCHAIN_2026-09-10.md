# Rust toolchain — installed 2026-09-10 under operator authority

Authority: operator via Archaeon, 2026-09-10 ("RUSTUP GRANTED"). Installed to unblock the
stitch Rust-core route, which was `ROUTE_VIABLE_BUILD_BLOCKED` on nothing but a compiler.

## Exact versions

```
rustup   1.29.1 (d95a37b6a 2026-08-13)
rustc    1.98.1 (48a229cea 2026-09-01)
cargo    1.98.1 (797e8a9bc 2026-08-05)
host     x86_64-pc-windows-gnu
toolchain stable-x86_64-pc-windows-gnu   (profile: minimal)
extra target installed: x86_64-pc-windows-gnullvm  (tried, then NOT used -- see below)
```

Installer: `rustup-init.exe` for `x86_64-pc-windows-gnu`, 14,686,353 bytes,
`sha256 6d5b5709addc0122c916d8c810da8d8a7b086a5d64fa805ef404d506392aadc8`.

## Contained, not installed into the user profile

```
RUSTUP_HOME = <tool_cache>/rust/rustup
CARGO_HOME  = <tool_cache>/rust/cargo
rustup-init … -y --default-host x86_64-pc-windows-gnu --default-toolchain stable \
              --profile minimal --no-modify-path
```

`--no-modify-path` is deliberate: nothing was added to the user's `PATH`, and no shell profile
was edited. The toolchain lives in the gitignored tool cache beside every other acquired
artifact, and is reached by absolute path. Removing it is deleting `<tool_cache>/rust`, or
`rustup self uninstall` with those two variables set.

## Footprint — MEASURED, not estimated

I refused to quote a figure before installing. Here is the measurement.

```
rustup/            952.6 MiB      998,840,561 B   (toolchain + the extra gnullvm target)
cargo/             307.1 MiB      322,066,444 B   (registry cache + binaries)
rustup-init.exe     14.0 MiB       14,686,353 B
------------------------------------------------------------
TOOLCHAIN TOTAL   1273.7 MiB    1,335,593,358 B

stitch build target/  231.4 MiB     242,627,334 B
------------------------------------------------------------
GRAND TOTAL       1505.1 MiB    1,578,220,692 B
```

Cross-check against the volume: F: free went 2204.55 → 2203.25 GiB, a delta of ~1.30 GiB,
consistent with the 1.47 GiB walked total after allowance for the registry's small files and
cluster slack. Both numbers are reported rather than reconciled into one.

Wall clock: rustup install ≈ 3 min; `cargo build --release --bin=compress` **31.09 s** for 22
declared dependencies.

## The linker: my earlier note was true and insufficient

I reported on 2026-09-10 that "`cc`/`link` are present via MinGW, so the gnu target is likely
the cheaper route". Present, yes. Sufficient, no — and the difference cost two failed builds.

**What is on `PATH` first is `llvm-mingw`** (Martin Storsjö's UCRT build, clang 21.1.7,
`lld`). It provides `gcc`, `cc` and `x86_64-w64-mingw32-gcc` as *clang* front-ends and ships
**no `libgcc.a` and no `libgcc_eh.a`**. Rust's `x86_64-pc-windows-gnu` target links against
those, so:

```
lld: error: unable to find library -lgcc_eh
lld: error: unable to find library -lgcc
```

Switching the *target* to `x86_64-pc-windows-gnullvm` did not help, and the reason is worth
recording: build scripts and proc-macros compile for the **host**, which was still
`…-windows-gnu`, so the same link failed one layer down. A target change cannot fix a host
toolchain mismatch.

**The fix needed no new install.** A real GCC MinGW-w64 was already on the host —
`BrechtSanders.WinLibs.POSIX.UCRT`, **GCC 15.2.0**, with `libgcc.a` and `libgcc_eh.a` present.
It was simply later on `PATH` than llvm-mingw. Putting its `bin` first for the build:

```
PATH="<WinLibs>/mingw64/bin:$PATH" cargo build --release --bin=compress
```

built cleanly in 31 s. So the `gnullvm` target is installed but **unused**, and it is recorded
here rather than removed so a later reader knows it was tried and why it was not the answer.

Generalisable: "a C toolchain is present" is not a fact about linking. Which MinGW, and whether
it ships the runtime the target expects, is the fact.

## What it unblocked

`compress.exe`, 4,108,196 bytes, built from `mlb2251/stitch` at `0ef5ec7f17091d22b8fa959fb5705e359d735a47`
— the revision the Python bindings pin, so the route comparison compares interfaces and not
versions. Result: `ROUTES_AGREE` on all four metrics, receipt
`techne/acquisition/receipts/paper_reproduction-stitch_rust_core-20260910T161201Z.json`.

## DreamCoder: one of four blockers cleared, and it was not the binding one

Asked and answered, nothing more attempted today.

- **BLK-DC-3 Rust compressor — CLEARED.** `cargo 1.98.1` is present; `rust_compressor/` could
  now be built.
- **BLK-DC-2 OCaml solver — STILL BLOCKED.** `opam`, `ocaml` and `make` are all still absent.
  The README needs an `opam switch 4.06.1+flambda` plus ten named OCaml packages. Every domain
  script invokes the solver binaries, so this one alone stops a domain run.
- **BLK-DC-1 python stack — UNCHANGED.** 14 of 38 pinned requirements have a wheel for either
  interpreter here (3.12.10, 3.11.9); 22 are sdist-only.
- **BLK-DC-4 resource envelope — UNCHANGED.** All 199 official commands are cloud-launcher
  invocations for `n1-megamem-96` / `x1.32xlarge` class machines with timeouts to 57,600 s.

So a Rust toolchain moves DreamCoder from four blockers to three, and the three that remain
each independently prevent a domain run. No DreamCoder work was attempted.
