@echo off
REM E1 Rerun — Pythia genomes on Llama (with cross-arch fix)
REM PythiaL16 will be auto-skipped (layer 16 exceeds Llama's 16 layers)

echo [E1 RERUN] Started: %date% %time%

python src\multilayer_eval.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir results\batch_E\E1_pythia_to_llama_rerun ^
    --genomes ^
        PythiaL8=results\batch_A\A3_pythia_L8\best_genome_1_5b.pt ^
        PythiaL10=results\batch_A\A3_pythia_L10\best_genome_1_5b.pt ^
        PythiaL16=results\batch_A\A3_pythia_L16\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0

echo [E1 RERUN] Finished (exit=%ERRORLEVEL%): %date% %time%
pause
