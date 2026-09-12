# Preserved build world for C / C++ / Fortran / yacc-era specimens (fossil vault, 2026-09-12).
# Debian 12 "bookworm": gcc 12.2, gfortran 12.2, bison 3.8, flex 2.6, make 4.3, cmake 3.25.
# Built once per host:  docker build -t prometheus-fossil-c:bookworm -f fossil-c-toolchain.Dockerfile .
# Every receipt that ran in it records the image tag and the toolchain probe output.
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gfortran bison flex make cmake pkg-config \
        zlib1g-dev libncurses-dev libreadline-dev libgmp-dev \
        file bc time ca-certificates \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8
WORKDIR /w
