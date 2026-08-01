import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from call_simulator import simulate_call  # noqa: E402


def test_inbound_call_starts_with_ai_identity_disclosure() -> None:
    result = simulate_call(
        direction="inbound",
        prior_contact_permission=False,
        recording_consent=False,
        supplied_field_count=0,
        opted_out=False,
    )

    assert result.started is True
    assert result.ai_disclosure.startswith("You are speaking with an AI voice agent")
    assert result.live_telephony_created is False


def test_outbound_call_fails_closed_without_prior_contact_permission() -> None:
    result = simulate_call(
        direction="outbound",
        prior_contact_permission=False,
        recording_consent=True,
        supplied_field_count=4,
        opted_out=False,
    )

    assert result.started is False
    assert result.outcome == "blocked-no-prior-contact-permission"
    assert result.ai_disclosure == ""
    assert result.captured_field_count == 0


def test_permitted_outbound_call_still_discloses_ai_identity() -> None:
    result = simulate_call(
        direction="outbound",
        prior_contact_permission=True,
        recording_consent=False,
        supplied_field_count=0,
        opted_out=False,
    )

    assert result.started is True
    assert result.prior_contact_permission is True
    assert "AI voice agent" in result.ai_disclosure


def test_recording_consent_refusal_forces_zero_captured_fields() -> None:
    result = simulate_call(
        direction="inbound",
        prior_contact_permission=False,
        recording_consent=False,
        supplied_field_count=9,
        opted_out=False,
    )

    assert result.recording_consent is False
    assert result.captured_field_count == 0
    assert result.outcome == "completed-without-capture"


def test_opt_out_ends_without_capturing_fields() -> None:
    result = simulate_call(
        direction="inbound",
        prior_contact_permission=False,
        recording_consent=True,
        supplied_field_count=3,
        opted_out=True,
    )

    assert result.ended is True
    assert result.outcome == "ended-opt-out"
    assert result.captured_field_count == 0


@pytest.mark.parametrize("field_count", [-1, 10])
def test_supplied_field_count_rejects_values_outside_the_bounded_intake(
    field_count: int,
) -> None:
    with pytest.raises(ValueError, match="between zero and nine"):
        simulate_call(
            direction="inbound",
            prior_contact_permission=False,
            recording_consent=True,
            supplied_field_count=field_count,
            opted_out=False,
        )


def test_cli_emits_safe_deterministic_json_without_raw_contact_data() -> None:
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "call_simulator",
            "outbound",
            "--prior-contact-permission",
            "yes",
            "--recording-consent",
            "yes",
            "--supplied-field-count",
            "3",
        ],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    serialized = json.dumps(payload, sort_keys=True).lower()

    assert payload["direction"] == "outbound"
    assert payload["captured_field_count"] == 3
    assert payload["live_telephony_created"] is False
    assert "@" not in serialized
    assert "+1" not in serialized
    assert "checkout" not in serialized


def test_cli_rejects_an_unbounded_field_count_without_a_traceback() -> None:
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "call_simulator",
            "inbound",
            "--supplied-field-count",
            "10",
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "between zero and nine" in completed.stderr
    assert "Traceback" not in completed.stderr
