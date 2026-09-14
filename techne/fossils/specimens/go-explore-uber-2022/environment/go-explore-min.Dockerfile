# Minimal managed world for go-explore's non-Atari, non-MuJoCo modules (Nyx NYX-44).
# Python 3.7 is the era interpreter the 2020 pins require. Build:
#   docker build -t prometheus-fossil-goexplore:min -f go-explore-min.Dockerfile .
FROM python:3.7-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 && rm -rf /var/lib/apt/lists/*
COPY requirements-min.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-min.txt
WORKDIR /w
