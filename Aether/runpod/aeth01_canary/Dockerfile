# AETH-01 RunPod canary container. NOT BUILT OR PUSHED by this repair
# cycle (see README.md "Status"). CUDA 12.x base so CuPy's prebuilt
# wheel (cupy-cuda12x) matches without a source build.
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Pinned target versions (ASTRA_CLOSURE_REVIEW_02.md section 7/9): this is
# a best-effort pin only, NOT build-verified -- the Docker daemon was
# unavailable in the repair environment that wrote this pin (README.md
# "Status"). Before R1: actually build this image, confirm these versions
# resolve and install cleanly, record whatever versions actually installed
# (pip freeze) in the image/source manifest, and deploy only the resulting
# immutable digest. Do not trust this pin as a substitute for that build.
RUN python3 -m pip install --no-cache-dir numpy==2.2.0 cupy-cuda12x==13.3.0

WORKDIR /app
COPY aeth01_gpu_kernel.py aeth01_cpu_oracle.py run_canary.py pod_service.py watchdog.sh /app/
RUN chmod +x /app/watchdog.sh
EXPOSE 8080

# The controller supplies AGE_ARTIFACT_TOKEN, AETH01_RUN_ID and the bounded
# timeout, exposes 8080/http, retrieves artifacts, then TERMINATES the pod.
# Missing auth/run binding fails closed before any canary starts. Finishing
# the canary does NOT stop pod billing. Never put RunPod API credentials here.
CMD ["python3", "/app/pod_service.py"]
