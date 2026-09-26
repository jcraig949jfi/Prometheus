"""Scout -> calibrate -> campaign, with AETH-02 as the regression case.

AETH-02 preregistered $0.83 per 2048^2 x 50,000-tick trajectory from a
throughput figure measured on a DIFFERENT workload: a larger lattice with
no causal-edge observer running. Measured, it was $0.889. The controller
ceiling had been set at $2.60, just above the $2.49 projection, so the
7.2% miss stopped the third of three trajectories against the ceiling.

`test_the_aeth02_campaign_would_have_been_refused_in_advance` is that
incident as a test. Everything else in this file exists to keep the two
ways it could recur closed: calibrating on the wrong workload, and
setting a ceiling that leaves no room for the calibration to be wrong.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "runpod")))

from prometheus_gpu import receipt as rc                 # noqa: E402
from prometheus_gpu import scout as scout_mod            # noqa: E402
from prometheus_gpu import spec as spec_mod              # noqa: E402

# The AETH-02 campaign, as it was actually run.
A40_HOURLY = 0.49
SITES = 2048 * 2048
TICKS = 50000
TRAJECTORY_UNITS = float(SITES * TICKS)          # 2.0972e11 site-ticks
MEASURED_WALL_S = 6525.3
MEASURED_RATE = TRAJECTORY_UNITS / MEASURED_WALL_S
PREREGISTERED_PER_TRAJECTORY = 0.83
CEILING_AS_SET = 2.60

CAMPAIGN = {
    "name": "aeth02-circuitry",
    "entrypoint": "aeth02_runner.py",
    "dependencies": {"pip": ["cupy-cuda12x==13.3.0", "numpy==2.2.0"]},
    "gpu": {"class": "NVIDIA A40", "count": 1},
    "max_runtime_s": 20000,
    "artifacts": ["out/circuitry.log"],
    "canary": "python3 -c 'import cupy'",
    "env": {"AETH02_SAMPLE_EVERY": "250", "AETH02_GRAPH_EVERY": "500"},
    "work_units": {"name": "site-ticks", "estimate": 3 * TRAJECTORY_UNITS},
}


@pytest.fixture
def campaign():
    return spec_mod.from_dict(dict(CAMPAIGN), source="aeth02.json")


@pytest.fixture
def calibration(campaign):
    """What a representative scout would have measured."""
    return scout_mod.calibrate(
        work_units_done=TRAJECTORY_UNITS / 20.0,
        elapsed_seconds=MEASURED_WALL_S / 20.0,
        spec=campaign, hourly=A40_HOURLY)


# ------------------------------------------------------------ the regression

def test_the_aeth02_campaign_would_have_been_refused_in_advance(
        campaign, calibration):
    """The incident, as a test.

    Three trajectories against a $2.60 ceiling, planned from a measured
    calibration rather than a carried-over figure. The planner must refuse,
    and must say how much of the request the ceiling actually affords --
    which is roughly the 2.4 trajectories that in fact completed.
    """
    plan = scout_mod.plan_campaign(
        campaign, calibration, requested_units=3 * TRAJECTORY_UNITS,
        ceiling_usd=CEILING_AS_SET,
        preregistered_usd=3 * PREREGISTERED_PER_TRAJECTORY)

    assert plan["decision"] == "REFUSE"
    assert plan["shortfall_usd"] > 0

    # The bare estimate is close to what was really spent per trajectory.
    per_trajectory = plan["calibrated_estimate"]["expected_usd"] / 3.0
    assert 0.85 < per_trajectory < 0.95, per_trajectory

    # And it exceeds what was preregistered, by about the observed miss.
    assert plan["estimate_error"] > 0.05

    # The proposal names the workload that fits: about 2.4 trajectories,
    # which is what actually completed before the ceiling stopped the run.
    affordable = plan["proposal"]["affordable_units"] / TRAJECTORY_UNITS
    assert 2.0 < affordable < 2.9, affordable


def test_a_ceiling_set_at_the_estimate_is_what_truncates_a_run(
        campaign, calibration):
    """The second half of the lesson: the margin, not the estimate, is
    what the decision must be taken on."""
    two = scout_mod.plan_campaign(campaign, calibration,
                                  requested_units=2 * TRAJECTORY_UNITS,
                                  ceiling_usd=1.95)
    bare = two["calibrated_estimate"]["expected_usd"]
    with_margin = two["calibrated_estimate"]["usd_with_margin"]
    assert bare < 1.95 < with_margin
    assert two["decision"] == "REFUSE", (
        "a ceiling the bare estimate clears but the margin does not is "
        "exactly the configuration that truncated AETH-02")
    assert two["recommended_controller_ceiling_usd"] == with_margin


def test_the_recommended_ceiling_leaves_room_for_the_estimate_to_be_wrong(
        campaign, calibration):
    plan = scout_mod.plan_campaign(campaign, calibration,
                                   requested_units=TRAJECTORY_UNITS,
                                   ceiling_usd=10.0)
    assert plan["decision"] == "PROCEED"
    est = plan["calibrated_estimate"]
    assert plan["recommended_controller_ceiling_usd"] > est["expected_usd"]
    # A 7.2% miss must fit inside the recommended headroom.
    assert (plan["recommended_controller_ceiling_usd"]
            > est["expected_usd"] * 1.072)


# --------------------------------------------------------- representativeness

def test_a_scout_keeps_everything_that_changes_seconds_per_unit(campaign):
    """A scout that dropped the instrumentation would reproduce the AETH-02
    error exactly, so only the work-unit count and runtime bound shrink."""
    reduced = scout_mod.scout_spec(campaign, 0.02)
    rep = scout_mod.representativeness(reduced, campaign)
    assert rep["representative"], rep["differences"]
    assert reduced["work_units"]["estimate"] < campaign["work_units"]["estimate"]
    assert reduced["max_runtime_s"] < campaign["max_runtime_s"]
    assert reduced["gpu"] == campaign["gpu"]
    assert reduced["dependencies"] == campaign["dependencies"]
    assert reduced["env"] == campaign["env"]
    assert reduced["entrypoint"] == campaign["entrypoint"]


@pytest.mark.parametrize("mutate,expected", [
    ({"gpu": {"class": "NVIDIA RTX A4000", "count": 1}}, "gpu_class"),
    ({"dependencies": {"pip": ["numpy==2.2.0"]}}, "dependencies"),
    ({"env": {}}, "env"),
    ({"entrypoint": "other.py"}, "entrypoint"),
])
def test_a_materially_different_scout_is_not_silently_usable(
        campaign, calibration, mutate, expected):
    """This is the AETH-02 error in its general form: a calibration from a
    workload that differs in something that changes seconds per unit."""
    other = spec_mod.from_dict(dict(CAMPAIGN, **mutate), source="other.json")
    rep = scout_mod.representativeness(other, campaign)
    assert not rep["representative"]
    assert expected in rep["differences"]

    with pytest.raises(scout_mod.CampaignRefused) as exc:
        scout_mod.plan_campaign(other, calibration,
                                requested_units=TRAJECTORY_UNITS,
                                ceiling_usd=10.0, campaign_spec=campaign)
    assert expected in str(exc.value)

    # It becomes usable only when the caller says so in as many words.
    plan = scout_mod.plan_campaign(
        other, calibration, requested_units=TRAJECTORY_UNITS,
        ceiling_usd=10.0, campaign_spec=campaign, accept_differences=True)
    assert plan["accepted_differences"] is True
    assert not plan["representativeness"]["representative"]


def test_a_scout_must_be_a_fraction_of_the_campaign(campaign):
    for bad in (0.0, 1.0, 1.5, -0.2):
        with pytest.raises(ValueError):
            scout_mod.scout_spec(campaign, bad)


def test_a_module_without_work_units_cannot_be_scouted(campaign):
    """Calibration is measured in the module's own denominator. Without
    one there is nothing to calibrate."""
    bare = spec_mod.from_dict({"name": "bare", "entrypoint": "run.py"})
    with pytest.raises(ValueError):
        scout_mod.scout_spec(bare, 0.1)


# ------------------------------------------------------------------ mechanics

def test_overhead_is_added_per_pod_and_compute_is_divided(campaign,
                                                          calibration):
    """Getting this backwards makes long campaigns look expensive and
    short ones look cheap."""
    one = scout_mod.project_from_calibration(calibration, TRAJECTORY_UNITS,
                                             pods=1)
    four = scout_mod.project_from_calibration(calibration, TRAJECTORY_UNITS,
                                              pods=4)
    assert four["compute_seconds_total"] == one["compute_seconds_total"]
    # Four pods finish sooner each, but the fixed cost is paid four times.
    assert four["per_pod_seconds"] < one["per_pod_seconds"]
    assert four["expected_usd"] > one["expected_usd"]
    # The expectation carries the measured overhead three more times; the
    # ceiling figure additionally carries the teardown reserve three more
    # times (Iteration 2: the reserve is a guardrail, not an expectation).
    rate = calibration["hourly_usd"]
    extra = four["expected_usd"] - one["expected_usd"]
    assert abs(extra - 3 * calibration["overhead_seconds"] / 3600.0
               * rate) < 1e-9
    extra_ceiling = (four["usd_with_margin"] - four["expected_usd"]
                     * (1 + four["margin"])) - (
        one["usd_with_margin"] - one["expected_usd"] * (1 + one["margin"]))
    assert abs(extra_ceiling - 3 * scout_mod.DEFAULT_TEARDOWN_RESERVE_S
               / 3600.0 * rate) < 1e-9


def test_calibration_refuses_degenerate_input(campaign):
    for units, seconds in ((0, 10.0), (-1, 10.0), (10, 0.0), (10, -1.0)):
        with pytest.raises(ValueError):
            scout_mod.calibrate(units, seconds, campaign)


def test_teardown_time_is_reserved_not_assumed_free(campaign, calibration):
    with_reserve = scout_mod.project_from_calibration(
        calibration, TRAJECTORY_UNITS, teardown_reserve_s=120.0)
    without = scout_mod.project_from_calibration(
        calibration, TRAJECTORY_UNITS, teardown_reserve_s=0.0)
    # Reserved in what a ceiling is set from and the decision is taken on.
    assert with_reserve["usd_with_margin"] > without["usd_with_margin"]
    # And NOT in the expectation: a scout's measured overhead already
    # contains a real teardown, so adding the reserve there counted it
    # twice and put Iteration 2's calibrated estimate 19% high.
    assert with_reserve["expected_usd"] == without["expected_usd"]


def test_render_names_the_decision_and_the_proposal(campaign, calibration):
    plan = scout_mod.plan_campaign(campaign, calibration,
                                   requested_units=3 * TRAJECTORY_UNITS,
                                   ceiling_usd=CEILING_AS_SET,
                                   preregistered_usd=2.49)
    text = scout_mod.render(plan)
    assert "REFUSE" in text
    assert "preregistered" in text
    assert "RECOMMENDED controller ceiling" in text
    assert "the seat's decision" in text


def test_the_controller_never_reshapes_the_workload_itself(campaign,
                                                           calibration):
    """A refusal offers a proposal. It does not return a smaller campaign
    dressed up as the one that was asked for."""
    plan = scout_mod.plan_campaign(campaign, calibration,
                                   requested_units=3 * TRAJECTORY_UNITS,
                                   ceiling_usd=CEILING_AS_SET)
    assert plan["decision"] == "REFUSE"
    assert plan["calibrated_estimate"]["requested_units"] == 3 * TRAJECTORY_UNITS
    assert "proposal" in plan
    assert "seat's decision" in plan["proposal"]["note"]


# -------------------------------------------------------------- the receipt

def test_a_receipt_carrying_a_calibration_must_carry_what_it_replaced():
    """Keeping only the estimate that turned out right is how a
    calibration miss disappears from the record."""
    base = {"schema": rc.SCHEMA, "run_id": "r1", "module": "m@1",
            "result": "OK", "bundle_sha256": "a" * 64, "pods": [],
            "cleanup": rc.cleanup_block([], inventory_read_ok=True),
            "calibrated_estimate": {"expected_usd": 2.69,
                                    "requested_units": 6.3e11,
                                    "margin": 0.2}}
    with pytest.raises(rc.ReceiptError) as exc:
        rc.validate(base)
    assert "preregistered_estimate" in str(exc.value)

    base["preregistered_estimate"] = {"expected_usd": 2.49}
    rc.validate(base)


def test_a_calibrated_estimate_must_state_its_workload_and_margin():
    base = {"schema": rc.SCHEMA, "run_id": "r1", "module": "m@1",
            "result": "OK", "bundle_sha256": "a" * 64, "pods": [],
            "cleanup": rc.cleanup_block([], inventory_read_ok=True),
            "preregistered_estimate": {"expected_usd": 2.49},
            "calibrated_estimate": {"expected_usd": 2.69}}
    with pytest.raises(rc.ReceiptError):
        rc.validate(base)


def test_the_receipt_renders_calibration_against_what_actually_ran():
    from prometheus_gpu import cost as cost_mod
    rec = {"schema": rc.SCHEMA, "run_id": "r1", "module": "m@1",
           "result": "OK", "bundle_sha256": "a" * 64, "pods": [],
           "cleanup": rc.cleanup_block([], inventory_read_ok=True),
           "preregistered_estimate": {"expected_usd": 2.49},
           "calibrated_estimate": {"expected_usd": 2.69,
                                   "requested_units": 6.3e11, "margin": 0.2},
           "cost": cost_mod.actual(19159.0, 0.49)}
    rc.validate(rec)
    text = rc.render(rec)
    assert "calibration" in text
    assert "predicted $2.6900" in text


def test_the_cli_scout_and_campaign_round_trip(tmp_path, capsys):
    from prometheus_gpu import cli
    spec_path = tmp_path / "campaign.json"
    spec_path.write_text(json.dumps(CAMPAIGN))
    (tmp_path / "aeth02_runner.py").write_text("print('x')\n")

    assert cli.main(["scout", str(spec_path), "--scale", "0.02"]) == 0
    reduced = json.loads(capsys.readouterr().out)
    assert reduced["name"].endswith("-scout")

    cal_path = tmp_path / "cal.json"
    spec = spec_mod.from_dict(dict(CAMPAIGN))
    cal_path.write_text(json.dumps(scout_mod.calibrate(
        TRAJECTORY_UNITS / 20.0, MEASURED_WALL_S / 20.0, spec,
        hourly=A40_HOURLY)))

    code = cli.main(["campaign", str(spec_path), "--calibration",
                     str(cal_path), "--units", str(3 * TRAJECTORY_UNITS),
                     "--ceiling", "2.60", "--preregistered", "2.49"])
    out = capsys.readouterr().out
    assert code == 1, "a refused campaign must not exit 0"
    assert "REFUSE" in out
