# Preserved 32-bit x86 world (batch 06, TECHNE-70): a genuine i386 Debian 12 userland (the
# i386/debian image) with gcc, gas, make, autotools -- for fossils that assume ILP32 or ship
# 32-bit x86 assembly (libfec's MMX/SSE2 Viterbi butterflies; compact's K&R pointer arithmetic).
#   docker build -t prometheus-fossil-i386:bookworm -f fossil-i386-toolchain.Dockerfile .
FROM i386/debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential make autoconf automake libtool bison flex \
        file bc time ca-certificates && rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8
WORKDIR /w
