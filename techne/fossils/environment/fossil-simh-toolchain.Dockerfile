# Preserved historical-machine world for the TCP lineage (batch 06, TECHNE-69): open-simh vax780
# (VAX-11/780: RP06 disks, TS11 tape -- bootable from tape in the 4.x line, which Debian's 3.8.1 is
# not), expect for console automation, python3 for building .tap images from the TUHS distribution
# files. open-simh pinned to commit a1f57fa3738ed31148d31126ba1a7278ff845c6d (2026-07-03).
#   docker build -t prometheus-fossil-simh:bookworm -f fossil-simh-toolchain.Dockerfile .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential git ca-certificates libpcap-dev libvdeplug-dev libpcre3-dev libedit-dev \
        expect python3 gzip bzip2 file procps && rm -rf /var/lib/apt/lists/*
RUN git clone --quiet https://github.com/open-simh/simh /tmp/simh && cd /tmp/simh \
    && git checkout --quiet a1f57fa3738ed31148d31126ba1a7278ff845c6d \
    && make -s vax780 vax 2>&1 | tail -3 && install -m755 BIN/vax780 BIN/vax /usr/local/bin/ \
    && git rev-parse HEAD > /usr/local/share/simh-commit.txt && rm -rf /tmp/simh
ENV LANG=C.UTF-8
WORKDIR /w
