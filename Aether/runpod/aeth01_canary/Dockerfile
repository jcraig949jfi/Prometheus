# AETH-01 RunPod canary container. NOT BUILT OR PUSHED by this repair
# cycle (see README.md "Status"). CUDA 12.x base so CuPy's prebuilt
# wheel (cupy-cuda12x) matches without a source build.
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Pinned only to a major line, not an exact patch version, since this
# has never been built; an exact pin should be recorded in the receipt
# once a real build happens, not guessed here.
RUN pip3 install --no-cache-dir numpy cupy-cuda12x

WORKDIR /app
COPY aeth01_gpu_kernel.py aeth01_cpu_oracle.py run_canary.py watchdog.sh /app/
RUN chmod +x /app/watchdog.sh

# No ENTRYPOINT/CMD: the RunPod pod launch command (README.md) supplies
# the exact invocation explicitly, so a pod started without arguments
# does nothing expensive by accident.
