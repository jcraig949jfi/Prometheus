"""Pipeline-D training loop (W3.6).

Fine-tunes Qwen2.5-Math-1.5B-Instruct + LoRA on serialized
boundary-layer / synthetic-env records via `trl.SFTTrainer`. Per
design doc §3 Pipeline-D framing the training framing is
substrate-verdict reproduction (classification head via causal-LM
next-token prediction).

Library stack:
- `transformers` for the base model + tokenizer (loaded by W3.4
  `model.py`)
- `peft` for LoRA adapters
- `trl.SFTTrainer` for the supervised fine-tuning loop
- Unsloth was specified in the v8 design doc (Change 10) but is NOT
  installed in this environment. Fallback to vanilla peft + trl per
  the W3.6 task brief; documented in the run report.

Windows note: trl 1.3.0 on Python 3.11 requires UTF-8 default
encoding (chat-template files contain non-cp1252 bytes). Run with
`python -X utf8 ...` or set `PYTHONUTF8=1`. Both the test runner
and any train.py CLI invocation must use this; `model.py`'s
`__main__` smoke does too.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import torch
from datasets import Dataset


# Best-effort UTF-8 enforcement: if Python wasn't started with -X utf8
# on Windows, trl will fail to import its chat-template files. We can't
# retroactively flip the interpreter flag, but we surface a clear error.
if sys.platform == "win32" and not sys.flags.utf8_mode:
    if os.environ.get("PYTHONUTF8") != "1":
        # Defer the explicit warning to import time so it shows up
        # before the cryptic UnicodeDecodeError from trl.
        import warnings as _warnings
        _warnings.warn(
            "trl 1.3.0 chat templates require UTF-8 default encoding. "
            "If imports fail with UnicodeDecodeError, re-run with "
            "`python -X utf8 ...` or set PYTHONUTF8=1.",
            stacklevel=2,
        )

from trl import SFTConfig, SFTTrainer  # noqa: E402


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


DEFAULT_RUNS_DIR = Path("ergon/pipeline_d/runs")


@dataclass
class TrainingArgs:
    """Training hyperparameters. v0.5 defaults are smoke-friendly;
    real tire-kick (W4.1) overrides max_steps + num_train_epochs.

    E001 v0.5b additive flag: ``completion_only_loss`` enables loss
    masking on the prompt portion (only the label tokens contribute
    to the loss). Default False preserves prior trl.SFTTrainer
    behaviour. When True, the trainer is wired with a completion-only
    collator using ``completion_response_template`` to find the
    boundary; on this corpus the data_loader formats records with
    a fixed " | Class: " separator that we use as the template.
    """

    run_name: str = "smoke"
    runs_dir: Path = field(default_factory=lambda: DEFAULT_RUNS_DIR)
    max_steps: int = 50
    num_train_epochs: int = 1
    learning_rate: float = 5e-5
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 1
    warmup_steps: int = 0
    logging_steps: int = 5
    save_steps: int = 1_000_000  # effectively "save only at end" for smoke
    seed: int = 42
    bf16: bool = True
    max_seq_length: int = 512
    early_stopping_patience: Optional[int] = None  # set to int to enable
    eval_strategy: str = "no"  # "no" | "steps" | "epoch"
    eval_steps: Optional[int] = None
    # E001 additive flag (default False = prior behaviour preserved)
    completion_only_loss: bool = False
    completion_response_template: str = " | Class: "

    @property
    def output_dir(self) -> Path:
        return self.runs_dir / self.run_name


# ---------------------------------------------------------------------------
# Training entry point
# ---------------------------------------------------------------------------


def _build_sft_config(args: TrainingArgs) -> SFTConfig:
    """Map our TrainingArgs onto `trl.SFTConfig`."""
    output_dir = str(args.output_dir)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # bf16 only if CUDA is available; otherwise fall back to fp32.
    use_bf16 = bool(args.bf16 and torch.cuda.is_available())

    cfg_kwargs: Dict[str, Any] = dict(
        output_dir=output_dir,
        max_steps=args.max_steps,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_steps=args.warmup_steps,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        seed=args.seed,
        bf16=use_bf16,
        report_to=[],  # disable wandb/tensorboard for smoke
        remove_unused_columns=False,
        eval_strategy=args.eval_strategy,
        save_strategy="no",  # smoke: just save_model at end
    )
    if args.eval_steps is not None:
        cfg_kwargs["eval_steps"] = args.eval_steps
    # max_length is used by SFTTrainer to truncate text; let it
    # match data_loader's tokenization budget.
    cfg_kwargs["max_length"] = args.max_seq_length
    return SFTConfig(**cfg_kwargs)


def train_model(
    model: Any,
    tokenizer: Any,
    train_dataset: Dataset,
    eval_dataset: Optional[Dataset] = None,
    args: Optional[TrainingArgs] = None,
) -> Dict[str, Any]:
    """Train `model` on `train_dataset` via `trl.SFTTrainer`.

    The dataset must carry a `text` column (built by
    `data_loader.load_dataset_for_training`); SFTTrainer consumes
    that field directly.

    Returns a metrics dict:
        {
          "run_name": str,
          "output_dir": str,
          "final_loss": float | None,
          "log_history": [{...}, ...],   # raw HF log entries
          "trained_steps": int,
          "saved_lora_path": str,        # where LoRA weights live
        }
    """
    if args is None:
        args = TrainingArgs()
    if "text" not in train_dataset.column_names:
        raise ValueError(
            f"train_dataset must have a 'text' column; got {train_dataset.column_names}. "
            "Use data_loader.load_dataset_for_training to build it."
        )

    sft_config = _build_sft_config(args)

    trainer_kwargs: Dict[str, Any] = dict(
        model=model,
        args=sft_config,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
    )
    if args.completion_only_loss:
        # E001 v0.5b: completion-only loss masking. Loss is computed only
        # over tokens AFTER the response template; prompt tokens contribute
        # nothing. Concretely makes the LM head learn the label-token
        # distribution rather than the next-token distribution after a
        # numeric prompt (the v0.5 binding constraint).
        try:
            from trl import DataCollatorForCompletionOnlyLM
            collator = DataCollatorForCompletionOnlyLM(
                response_template=args.completion_response_template,
                tokenizer=tokenizer,
            )
            trainer_kwargs["data_collator"] = collator
        except ImportError:
            # Newer trl renamed/moved this collator; fall back gracefully
            # and surface a clear note rather than half-applying.
            import warnings as _w
            _w.warn(
                "trl.DataCollatorForCompletionOnlyLM not importable; "
                "completion_only_loss=True ignored. Train will run with "
                "default loss masking."
            )

    trainer = SFTTrainer(**trainer_kwargs)

    trainer.train()

    # Save LoRA adapter weights. peft.PeftModel.save_pretrained writes
    # adapter_config.json + adapter_model.safetensors only.
    out_dir = str(args.output_dir)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if hasattr(trainer.model, "save_pretrained"):
        trainer.model.save_pretrained(out_dir)
    if hasattr(tokenizer, "save_pretrained"):
        tokenizer.save_pretrained(out_dir)

    # Pull final loss from the trainer's log history.
    log_history = list(trainer.state.log_history)
    final_loss: Optional[float] = None
    for entry in reversed(log_history):
        if "loss" in entry:
            final_loss = float(entry["loss"])
            break

    metrics = {
        "run_name": args.run_name,
        "output_dir": out_dir,
        "final_loss": final_loss,
        "log_history": log_history,
        "trained_steps": int(trainer.state.global_step),
        "saved_lora_path": out_dir,
    }

    # Persist metrics next to the LoRA weights for the W6.1 dossier.
    metrics_path = Path(out_dir) / "training_metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        # log_history may contain non-JSON-native floats from torch;
        # default=str catches stragglers.
        json.dump(metrics, f, indent=2, default=str)

    return metrics


def load_lora_for_eval(
    base_model: Any,
    lora_path: str | Path,
) -> Any:
    """Reload a saved LoRA adapter onto a freshly-loaded base model
    for round-trip eval (W3.5 round-trip test in test_pipeline_d.py).
    """
    from peft import PeftModel

    return PeftModel.from_pretrained(base_model, str(lora_path))


__all__ = [
    "TrainingArgs",
    "train_model",
    "load_lora_for_eval",
    "DEFAULT_RUNS_DIR",
]
