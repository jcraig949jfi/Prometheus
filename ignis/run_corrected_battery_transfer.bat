@echo off
REM ============================================================
REM Corrected Battery Cross-Model Transfer Test
REM
REM Re-runs the transfer test with the 3 fixed dead-signal traps.
REM Counting Fence Posts, Rank Reversal, Pages in Book now use
REM single-token parity phrasings instead of colliding numerics.
REM
REM This tells us the TRUE ceiling for L19+L20+L21 x1.5 on the
REM corpus-first model.
REM
REM Expected runtime: ~18 minutes
REM ============================================================

setlocal

set MODEL=results\corpus_first\stageB_finetune\ft_model
set OUTDIR=results\corrected_battery_transfer

echo ============================================================
echo  CORRECTED BATTERY CROSS-MODEL TRANSFER TEST
echo  Model: corpus-first fine-tuned Qwen 1.5B
echo  Battery: 30 traps (3 fixed dead-signal traps)
echo  Genomes: 7 raw-model vectors (L19-L26)
echo  Output: %OUTDIR%
echo  Started: %date% %time%
echo ============================================================

python src\multilayer_eval.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %OUTDIR% ^
    --genomes ^
        L19=results\layer_sweep\L19\best_genome_1_5b.pt ^
        L20=results\layer_sweep\L20\best_genome_1_5b.pt ^
        L21=results\batch4_followup\stage2_L21\best_genome_1_5b.pt ^
        L23_forge=results\forge_augmented\L23\best_genome_1_5b.pt ^
        L24=results\batch4_followup\stage2_L24\best_genome_1_5b.pt ^
        L25=results\layer_sweep\L25\best_genome_1_5b.pt ^
        L26=results\layer_sweep\L26\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5

echo.
echo ============================================================
echo  Corrected battery test complete: %date% %time%
echo  Results in: %OUTDIR%
echo ============================================================

pause
