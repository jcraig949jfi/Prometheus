# Archaeon v0 detector calibration

Measured, not asserted. Regenerate with `python -m archaeon.calibrate --seeds 200 --power`.

    seeds                200
    thresholds version   archaeon.thresholds.v0

Binomial SE at 200 seeds is about 0.015 near p=0.05, so differences under
~0.03 are noise.

## Headline

```
detector                    null    hit   worst-control   separation
-------------------------------------------------------------------
REPEATED_SMALL_DEVIATION   0.040  0.335       0.065        +0.270
SIGN_INSTABILITY           0.000  0.780       0.000        +0.780
LOCAL_VARIANCE_ANOMALY     0.000  0.955       0.040        +0.915
PLAYER_ORDER_REVERSAL      0.000  1.000       0.000        +1.000
REPEATED_OUTLIER_REGION    0.000  1.000       0.000        +1.000
BOUNDARY_TRANSITION_HINT   0.000  1.000       0.020        +0.980
```

`null` is the fraction of pure-null corpora on which the detector fired at
least once -- the corpus-level false-alarm rate, which is the one that
matters because Archaeon proposes once per corpus. `worst-control` is the
paired control with the identical structure and no effect; a detector with a
high hit rate AND a high control rate has learned the shape, not the effect.

## Per detector

### REPEATED_SMALL_DEVIATION

    null fire rate            0.040   (eligible on 100% of null corpora)
    planted hit rate          0.335   (eligible on 100% of planted corpora)
    control [no_deviation  ]  0.065
    separation                +0.270

### SIGN_INSTABILITY

    null fire rate            0.000   (eligible on 100% of null corpora)
    planted hit rate          0.780   (eligible on 100% of planted corpora)
    control [sign_stable   ]  0.000
    separation                +0.780

### LOCAL_VARIANCE_ANOMALY

    null fire rate            0.000   (eligible on 100% of null corpora)
    planted hit rate          0.955   (eligible on 100% of planted corpora)
    control [equal_variance]  0.040
    separation                +0.915

### PLAYER_ORDER_REVERSAL

    null fire rate            0.000   (eligible on 100% of null corpora)
    planted hit rate          1.000   (eligible on 100% of planted corpora)
    control [stable_order  ]  0.000
    separation                +1.000

### REPEATED_OUTLIER_REGION

    null fire rate            0.000   (eligible on 100% of null corpora)
    planted hit rate          1.000   (eligible on 100% of planted corpora)
    control [no_outliers   ]  0.000
    separation                +1.000

### BOUNDARY_TRANSITION_HINT

    null fire rate            0.000   (eligible on 0% of null corpora)
    planted hit rate          1.000   (eligible on 100% of planted corpora)
    control [flat          ]  0.020
    control [gradual       ]  0.000
    separation                +0.980

## Power curves

Where each detector stops being able to see anything. A single hit rate at
one effect size is not a characterisation; the curve is.

```
REPEATED_SMALL_DEVIATION  (effect_sd)
    effect_sd = 0.4     hit 0.10
    effect_sd = 0.6     hit 0.21
    effect_sd = 0.7     hit 0.27
    effect_sd = 0.8     hit 0.34
    effect_sd = 0.9     hit 0.34
    effect_sd = 1.0     hit 0.23

LOCAL_VARIANCE_ANOMALY  (variance_ratio)
    variance_ratio = 1.5     hit 0.11
    variance_ratio = 2.0     hit 0.23
    variance_ratio = 3.0     hit 0.58
    variance_ratio = 4.0     hit 0.80
    variance_ratio = 6.0     hit 0.95
    variance_ratio = 9.0     hit 1.00

SIGN_INSTABILITY  (gap)
    gap      = 0.01    hit 0.01
    gap      = 0.02    hit 0.03
    gap      = 0.04    hit 0.29
    gap      = 0.06    hit 0.80
    gap      = 0.1     hit 1.00

PLAYER_ORDER_REVERSAL  (gap)
    gap      = 0.01    hit 0.01
    gap      = 0.02    hit 0.05
    gap      = 0.04    hit 0.59
    gap      = 0.08    hit 1.00
    gap      = 0.12    hit 1.00

REPEATED_OUTLIER_REGION  (offset_sd)
    offset_sd = 2.0     hit 0.00
    offset_sd = 3.0     hit 0.04
    offset_sd = 4.0     hit 0.70
    offset_sd = 6.0     hit 1.00
    offset_sd = 12.0    hit 1.00

BOUNDARY_TRANSITION_HINT  (step)
    step     = 0.02    hit 0.12
    step     = 0.05    hit 0.60
    step     = 0.1     hit 1.00
    step     = 0.25    hit 1.00
    step     = 0.5     hit 1.00

```
