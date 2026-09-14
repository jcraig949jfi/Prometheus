# Preserved run world for MATLAB-dialect control-engineering fossils (batch 06, phase 4): GNU Octave
# 7.3 (Debian 12) without a display; plotting calls in the fossils are shadowed by no-op stubs in
# each specimen's harness (a harness-level accommodation; the .m sources are never edited).
#   docker build -t prometheus-fossil-octave:bookworm -f fossil-octave-toolchain.Dockerfile .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        octave octave-control octave-signal \
        file bc time ca-certificates && rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8
WORKDIR /w
