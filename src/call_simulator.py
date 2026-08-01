"""Local, secrets-free call lifecycle simulator.

This module proves decision boundaries only. It does not create or connect live
telephony resources.
"""

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

Direction = Literal["inbound", "outbound"]

AI_DISCLOSURE = "You are speaking with an AI voice agent for Forhemit Labs."
MAX_INTAKE_FIELDS = 9


@dataclass(frozen=True)
class SimulationResult:
    direction: Direction
    started: bool
    ai_disclosure: str
    prior_contact_permission: bool
    recording_consent: bool
    captured_field_count: int
    ended: bool
    outcome: str
    live_telephony_created: bool = False


def simulate_call(
    *,
    direction: Direction,
    prior_contact_permission: bool,
    recording_consent: bool,
    supplied_field_count: int,
    opted_out: bool,
) -> SimulationResult:
    """Return a deterministic, data-minimized simulation result."""
    if direction not in {"inbound", "outbound"}:
        raise ValueError("direction must be inbound or outbound")
    if not 0 <= supplied_field_count <= MAX_INTAKE_FIELDS:
        raise ValueError("supplied field count must be between zero and nine")

    if direction == "outbound" and not prior_contact_permission:
        return SimulationResult(
            direction=direction,
            started=False,
            ai_disclosure="",
            prior_contact_permission=False,
            recording_consent=False,
            captured_field_count=0,
            ended=True,
            outcome="blocked-no-prior-contact-permission",
        )

    if opted_out:
        return SimulationResult(
            direction=direction,
            started=True,
            ai_disclosure=AI_DISCLOSURE,
            prior_contact_permission=prior_contact_permission,
            recording_consent=recording_consent,
            captured_field_count=0,
            ended=True,
            outcome="ended-opt-out",
        )

    captured_field_count = supplied_field_count if recording_consent else 0
    outcome = (
        "completed-capture-ready"
        if captured_field_count
        else "completed-without-capture"
    )
    return SimulationResult(
        direction=direction,
        started=True,
        ai_disclosure=AI_DISCLOSURE,
        prior_contact_permission=prior_contact_permission,
        recording_consent=recording_consent,
        captured_field_count=captured_field_count,
        ended=True,
        outcome=outcome,
    )


def yes_or_no(value: str) -> bool:
    if value == "yes":
        return True
    if value == "no":
        return False
    raise argparse.ArgumentTypeError("expected yes or no")


def bounded_field_count(value: str) -> int:
    try:
        field_count = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected an integer") from error
    if not 0 <= field_count <= MAX_INTAKE_FIELDS:
        raise argparse.ArgumentTypeError(
            "supplied field count must be between zero and nine"
        )
    return field_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", choices=("inbound", "outbound"))
    parser.add_argument(
        "--prior-contact-permission",
        type=yes_or_no,
        default=False,
        metavar="yes|no",
    )
    parser.add_argument(
        "--recording-consent",
        type=yes_or_no,
        default=False,
        metavar="yes|no",
    )
    parser.add_argument("--supplied-field-count", type=bounded_field_count, default=0)
    parser.add_argument(
        "--opted-out",
        type=yes_or_no,
        default=False,
        metavar="yes|no",
    )
    return parser


def main() -> None:
    arguments = build_parser().parse_args()
    result = simulate_call(
        direction=arguments.direction,
        prior_contact_permission=arguments.prior_contact_permission,
        recording_consent=arguments.recording_consent,
        supplied_field_count=arguments.supplied_field_count,
        opted_out=arguments.opted_out,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
