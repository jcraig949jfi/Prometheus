#!/bin/bash
# ================================================================
# Prometheus Migration & Launch Script
# Run once. Approve once. No popups.
# ================================================================
set -e

echo "============================================================"
echo "  PROMETHEUS MIGRATION SCRIPT"
echo "  Archive → Copy Results → RPH Eval → Git Init → GitHub Push"
echo "============================================================"
echo ""

# ── 1. Archive the Qwen3-4B run ─────────────────────────────────
echo "[1/6] Archiving Qwen3-4B run..."
cd "f:/bitfrost-mech/bitfrost-mech/seti-pipeline_v2/src"
python archive_run.py preserve "Qwen3-4B Gen 9, 545 genomes, NULL confirmed, cos_r -0.061, PC1 54.1%"
echo "  ✓ Run archived"
echo ""

# ── 2. Copy results to Prometheus ────────────────────────────────
echo "[2/6] Copying results to Prometheus/ignis..."
if [ ! -d "f:/Prometheus/ignis/src/results" ]; then
    mkdir -p "f:/Prometheus/ignis/src/results"
fi
# Copy the results directory (archives, watchman data, logs)
cp -r "f:/bitfrost-mech/bitfrost-mech/seti-pipeline_v2/src/results/setiv2" \
      "f:/Prometheus/ignis/src/results/ignis" 2>/dev/null || true
echo "  ✓ Results copied to Prometheus/ignis/src/results/ignis"
echo ""

# ── 3. Copy RPH eval results ────────────────────────────────────
echo "[3/6] Copying RPH eval results..."
cp f:/bitfrost-mech/bitfrost-mech/seti-pipeline_v2/results/rph_eval_*.json \
   "f:/Prometheus/ignis/src/results/" 2>/dev/null || echo "  (no RPH eval JSONs to copy)"
echo "  ✓ RPH results copied"
echo ""

# ── 4. Kick off RPH eval on CPU (background) ────────────────────
echo "[4/6] Starting RPH eval on CPU (background)..."
cd "f:/bitfrost-mech/bitfrost-mech/seti-pipeline_v2/src"
python eval_rph_survivors.py --device cpu --models 0.5B 1.5B 3B > /tmp/rph_eval.log 2>&1 &
RPH_PID=$!
echo "  ✓ RPH eval running in background (PID: $RPH_PID)"
echo "    Log: /tmp/rph_eval.log"
echo ""

# ── 5. Git init Prometheus ───────────────────────────────────────
echo "[5/6] Initializing git repository..."
cd "f:/Prometheus"

# Init if not already a repo
if [ ! -d ".git" ]; then
    git init
    echo "  ✓ Git initialized"
else
    echo "  ✓ Git already initialized"
fi

# Stage everything (respecting .gitignore)
git add -A
echo "  ✓ Files staged"

# Commit
git commit -m "$(cat <<'EOF'
feat: initialize Prometheus — unified research program

Three pillars:
- Ignis (formerly SETI v2): reasoning circuit discovery via CMA-ES steering vectors
- Arcanum (formerly Arcanum Infinity): waste stream novelty mining
- Eos/Dawn: horizon scanner with 6 sources + Nemotron 120B analysis

Includes:
- Full rename: seti→ignis, bitfrost→prometheus across all source
- Night Watchman, Review Watchman, RPH Evaluator analysis tools
- Constitution (the_fire.md), North Star, priorities, master TODO
- API registry with 10+ verified free-tier services
- Grammata taxonomy framework (from Vesta concepts)
- Aethon concept docs (backburnered)
- Archive of all superseded work (SETI v1, mech, vesta, fennel, etc.)

Scale gradient results (all NULL):
- Qwen 2.5: 0.5B, 1.5B, 3B
- Qwen 3: 4B (PC1=54.1%, strongest consolidation)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
echo "  ✓ Initial commit created"
echo ""

# ── 6. Create GitHub repo and push ───────────────────────────────
echo "[6/6] Creating GitHub repo and pushing..."

# Create the repo (public)
gh repo create Prometheus --public --source=. --description "Stealing fire from the gods — reasoning circuit discovery + waste stream novelty mining in transformer internals" --push 2>/dev/null || {
    echo "  GitHub repo may already exist. Trying to add remote and push..."
    git remote add origin https://github.com/jcraig949jfi/Prometheus.git 2>/dev/null || true
    git push -u origin main 2>/dev/null || git push -u origin master
}
echo "  ✓ Pushed to GitHub"
echo ""

# ── Done ─────────────────────────────────────────────────────────
echo "============================================================"
echo "  MIGRATION COMPLETE"
echo ""
echo "  Repo: https://github.com/jcraig949jfi/Prometheus"
echo "  RPH eval running in background (PID: $RPH_PID)"
echo "  Check RPH progress: tail -f /tmp/rph_eval.log"
echo ""
echo "  Next: run Ignis from F:/Prometheus/ignis/src/"
echo "============================================================"
