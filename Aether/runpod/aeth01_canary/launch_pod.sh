#!/bin/bash
# Disabled migration stub: no provider calls, credentials, or paid path.

set -euo pipefail

printf '%s\n' \
    '[launch_pod] DISABLED: the legacy shell launcher is unsafe. Nothing was launched.' \
    '[launch_pod] Use age_controller.py after reviewing its run-specific plan and approval requirements.' \
    '[launch_pod] From this directory, consult: python age_controller.py --help' >&2
exit 1
