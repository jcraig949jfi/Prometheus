#!/bin/bash
# Disabled migration stub: does not terminate a pod or print provider data.

set -euo pipefail

printf '%s\n' \
    '[terminate_pod] DISABLED: no pod was terminated; any existing pod may still be billing.' \
    '[terminate_pod] Use the recovery workflow in age_controller.py, or terminate in the RunPod console now.' \
    '[terminate_pod] From this directory, consult: python age_controller.py --help' \
    '[terminate_pod] Verify termination independently and record actual spend regardless of outcome.' >&2
exit 1
