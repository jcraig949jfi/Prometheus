# Preserved historical-machine world for DEC PDP-1 bodies (batch 12 P6, 2026-09-16): open-simh
# `pdp1` (same pinned commit as the simh/VAX world, a1f57fa3, 2026-07-03; headless -- no Type 30
# display, so a display program can be assembled and stepped but not drawn) and Bob Supnik's
# MACRO-1 cross assembler from simh/simtools (crossassemblers/macro1, pinned commit below).
# First consumer: spacewar-pdp1-1962 (MACRO source, 25 Mar 1962).
#   docker build -t prometheus-fossil-pdp1:bookworm -f fossil-pdp1-toolchain.Dockerfile .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential git ca-certificates libpcre3-dev libedit-dev expect file procps python3 \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --quiet https://github.com/open-simh/simh /tmp/simh && cd /tmp/simh \
    && git checkout --quiet a1f57fa3738ed31148d31126ba1a7278ff845c6d \
    && make -s pdp1 2>&1 | tail -3 && install -m755 BIN/pdp1 /usr/local/bin/ \
    && mkdir -p /usr/local/share/pdp1 && git rev-parse HEAD > /usr/local/share/pdp1/simh-commit.txt \
    && rm -rf /tmp/simh
RUN git clone --quiet https://github.com/simh/simtools /tmp/simtools && cd /tmp/simtools \
    && git checkout --quiet 2d9a2d96caa013428f8d0686e26a4f0164c889bf \
    && cd crossassemblers/macro1 && gcc -O2 -o macro1 macro1.c && install -m755 macro1 /usr/local/bin/ \
    && git -C /tmp/simtools rev-parse HEAD > /usr/local/share/pdp1/simtools-commit.txt \
    && rm -rf /tmp/simtools
ENV LANG=C.UTF-8
WORKDIR /w
