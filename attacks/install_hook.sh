#!/bin/sh
# Git hooks are NOT tracked by git, so each clone must install its own.
# Run once per machine:   sh attacks/install_hook.sh
d="$(git rev-parse --git-dir)/hooks/pre-commit"
printf '#!/bin/sh\nexec python attacks/preflight.py --probes\n' > "$d"
chmod +x "$d"
echo "installed $d"
