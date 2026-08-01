# Spec: Deterministic call lifecycle simulator

## Objective

Add a secrets-free local simulator that proves the reference agent's inbound and outbound decision boundaries without creating a provider account, buying a number, routing telephony, or placing a real call. It is for technical reviewers who need executable evidence of disclosure, prior outbound permission, recording consent, opt-out handling, and data-minimized lead capture.

## Tech stack

- Python 3.11–3.14
- Python standard library only for the simulator
- Pytest for behavior tests
- Ruff for linting

## Commands

- Test: `python3 -m pytest -q`
- Lint: `python3 -m ruff check .`
- Simulate inbound: `PYTHONPATH=src python3 -m call_simulator inbound --recording-consent yes --supplied-field-count 3`
- Simulate permitted outbound: `PYTHONPATH=src python3 -m call_simulator outbound --prior-contact-permission yes --recording-consent no`
- Prove outbound fail-closed: `PYTHONPATH=src python3 -m call_simulator outbound`

## Project structure

- `src/call_simulator.py` — pure lifecycle logic and a JSON CLI
- `tests/test_call_simulator.py` — executable behavior specification
- `README.md` — reviewer commands and evidence limitations

## Code style

Use small typed functions, immutable result objects, and safe defaults:

```python
result = simulate_call(
    direction="outbound",
    prior_contact_permission=False,
    recording_consent=False,
    supplied_field_count=0,
    opted_out=False,
)
assert result.started is False
```

Names describe business state. JSON output may contain counts and booleans, never raw contact values, provider identifiers, phone numbers, credentials, or checkout data.

## Testing strategy

Unit tests cover inbound disclosure, outbound permission, recording consent, opt-out termination, input rejection, and safe serialized output. The existing static guardrail tests continue to cover both provider adapters. No test uses the network, a microphone, a phone number, or provider credentials.

## Boundaries

- Always: identify the agent as AI on every started call; fail closed for outbound calls without prior permission; capture zero fields without recording consent; emit only counts and booleans.
- Ask first: uploading an assistant, buying or routing a number, placing a live call, or changing a provider account.
- Never: imply that the simulator proves live telephony, accept raw lead values, persist caller data, expose checkout, make a legal conclusion, or bypass the exact external-approval gate.

## Success criteria

- An inbound simulation starts with AI identity disclosure.
- An outbound simulation cannot start without explicit prior contact permission.
- A permitted outbound simulation also starts with AI identity disclosure.
- Recording-consent refusal forces captured field count to zero.
- Opt-out ends the simulated call without a persuasion step.
- CLI output is deterministic JSON and contains no raw lead data or live telephony claim.
- All tests and lint pass, README states the limitation, and the version is released as `v1.1.0` only after CI succeeds.

## Rollback

Revert the additive simulator commit and retain `v1.0.0`; no external telephony or stored data requires migration.

## Open questions

None. Live carrier verification remains separately blocked on the recorded approval phrase and a verified destination number.
