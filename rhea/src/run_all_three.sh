#!/bin/bash
set -e
cd "$(dirname "$0")"
source ~/repos/Prometheus/.venv/bin/activate

echo "============================================================"
echo "TASK 1/3: Vocabulary test (100 steps, 50 examples)"
echo "============================================================"
python3 -u lexical_patch.py 2>&1 | tee ../runs/task1_vocab_test.log

echo ""
echo "============================================================"
echo "TASK 2/3: Install elan/Lean 4"
echo "============================================================"
if command -v lean &> /dev/null; then
    echo "Lean already installed: $(lean --version)"
else
    echo "Installing elan..."
    curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:stable 2>&1
    export PATH="$HOME/.elan/bin:$PATH"
    if command -v lean &> /dev/null; then
        echo "SUCCESS: $(lean --version)"
    else
        echo "FAILED: lean not found after install. Trying to source profile..."
        source ~/.profile 2>/dev/null || source ~/.bashrc 2>/dev/null || true
        if command -v lean &> /dev/null; then
            echo "SUCCESS after sourcing: $(lean --version)"
        else
            echo "FAILED: lean still not found. Task 3 will be skipped."
        fi
    fi
fi

echo ""
echo "============================================================"
echo "TASK 3/3: Proof corpus loop (if Lean 4 available)"
echo "============================================================"
export PATH="$HOME/.elan/bin:$PATH"
python3 -u close_the_loop.py 2>&1 | tee ../runs/task3_proof_loop.log

echo ""
echo "============================================================"
echo "ALL TASKS COMPLETE"
echo "============================================================"
