@echo off
REM ============================================================
REM Cross-Model Genome Transfer Test
REM
REM Hypothesis: Raw-model genomes (evolved on base Qwen 1.5B)
REM may transfer to the corpus-first fine-tuned model, combining
REM the benefits of both approaches.
REM
REM Tests all 2^7 - 1 = 127 combinations of 7 raw-model genomes
REM injected into the corpus-first ft_model.
REM
REM Expected runtime: ~1-2 hours on 5060 Ti
REM Expected VRAM: ~6-8 GB (single forward passes, no evolution)
REM ============================================================

setlocal

set MODEL=results\corpus_first\stageB_finetune\ft_model
set OUTDIR=results\cross_model_transfer

echo ============================================================
echo  CROSS-MODEL GENOME TRANSFER TEST
echo  Model: corpus-first fine-tuned Qwen 1.5B
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
echo  Transfer test complete: %date% %time%
echo  Results in: %OUTDIR%
echo ============================================================

pause
