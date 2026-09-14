# A2 FalkorDB from source: artifact record

Built by Nestor-A[m1-918ab2b0] on WSL ext4 (~/lab/falkordb), finished 2026-09-14 07:29.
Recorded and smoke-tested by Nestor-A[m1-449a9e76] at 11:42.

- source: FalkorDB 770449f99044b4d88b628a4d3b08ea91c28771ec (#2757), deps/RediSearch@ea1a6f40cbc9
- build image: ghcr.io/falkordb/falkordb-build@sha256:ccbaf9e4f46c699625ed2871fdd6a13535d3609caa3f35d43449e4b4e2b62164
  (clang-22, cargo 1.98.0, cmake 3.31.6); script is the predecessor's build_falkor_v6.sh
  (graphblas.sh -> redisearch.sh -> cargo build --release), --cpus 8
- artifact: ~/lab/falkor-out/libfalkordb.so, 64,008,960 bytes,
  sha256 c495cae39faeb85a9b1674ee07940bb34e662142a051cbe0fc535e352495e0d9 (not committed: 64 MB)
- smoke: redis-server --loadmodule on falkordb/falkordb@sha256:adbddd41...; MODULE LIST shows graph
  (ver 999999, i.e. an unversioned dev build); CREATE then MATCH (a:A)-[:R]->(b:B) RETURN a.v+b.v = 3.
- NOT done: the untouched-baseline bench with FalkorDB's own harness, a byte-reproducibility rebuild,
  or any comparison against the stock 4.20.4 image.
