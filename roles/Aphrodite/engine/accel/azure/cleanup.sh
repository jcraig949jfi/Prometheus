#!/usr/bin/env bash
# Delete EVERY resource group tagged purpose=aphrodite-accel-canary. Idempotent.
set -euo pipefail
for rg in $(az group list --tag purpose=aphrodite-accel-canary --query "[].name" -o tsv); do
  echo "deleting $rg"; az group delete -n "$rg" --yes --no-wait
done
echo "remaining:"; az group list --tag purpose=aphrodite-accel-canary --query "[].{name:name,state:properties.provisioningState}" -o table
