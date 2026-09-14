# Preserved simulation world for HDL / logic fossils (batch 03, 2026-09-12). Debian bookworm
# + Icarus Verilog, Verilator, Yosys, GTKWave. Build once per host:
#   docker build -t prometheus-fossil-hw:bookworm -f fossil-hw-toolchain.Dockerfile .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential iverilog verilator yosys gtkwave \
        make file ca-certificates && rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8
WORKDIR /w
