#!/bin/bash
# Runs inside prometheus-fossil-c:bookworm with /vault (ro) and /ruler mounted.
# Bodies are compiled from the vault, unmodified; only the driver is ours.
set -e
A=/vault/reed-solomon-rockliff-1991/upstream
B=/vault/libfec-karn/upstream/tree
OUT=/ruler/out
mkdir -p $OUT
sha256sum $A/rs.c $B/init_rs_int.c $B/encode_rs_int.c $B/decode_rs_int.c $B/int.h $B/rs-common.h $B/init_rs.h $B/encode_rs.h $B/decode_rs.h > $OUT/bodies.sha256
gcc --version | head -1 > $OUT/toolchain.txt
gcc -O0 -c $B/init_rs_int.c   -I$B -o $OUT/init_rs_int.o
gcc -O0 -c $B/encode_rs_int.c -I$B -o $OUT/encode_rs_int.o
gcc -O0 -c $B/decode_rs_int.c -I$B -o $OUT/decode_rs_int.o
gcc -O0 -std=gnu89 -w -c /ruler/ruler.c -I$A -o $OUT/ruler.o
gcc -O0 -o $OUT/ruler $OUT/ruler.o $OUT/init_rs_int.o $OUT/encode_rs_int.o $OUT/decode_rs_int.o -lm
TRIALS=${1:-2000}
SEED=${2:-20260916}
for m in pair self-karn self-rock mismap; do
  $OUT/ruler $m $TRIALS $SEED > $OUT/$m.json
  echo "$m exit $?"
done
sha256sum $OUT/ruler > $OUT/ruler_binary.sha256
