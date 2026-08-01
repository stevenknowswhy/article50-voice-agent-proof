# Article 50 voice-agent proof

A secrets-free reference implementation for an inbound AI voice qualification agent. It demonstrates the engineering controls behind Forhemit Labs' fixed-price Article 50 Launch Patch; it does not decide whether Article 50 applies or certify compliance.

## What the proof enforces

- Identifies itself as an AI voice agent at the start of every call.
- Gives implementation information only; buyer counsel or a named compliance owner retains applicability and wording decisions.
- Requests explicit permission before collecting business follow-up details.
- Asks one question at a time and caps the delivery shape at three product surfaces.
- Never requests credentials, source code, payment-card data, health information, or private checkout details.
- Stops persuasion when a caller opts out or says they are not interested.
- Logs only that a consented capture occurred and the number of fields; the reference code does not log raw lead details.

## Provider adapters and local simulation

- `src/agent.py` is a LiveKit Agents reference implementation for an inbound RTC session.
- `vapi-assistant.example.json` is a provider-neutralized Vapi assistant definition with the same conversation boundaries.
- `src/call_simulator.py` is a deterministic, standard-library simulator for inbound and permission-gated outbound call lifecycles.

These files contain no phone number, API key, provider account identifier, destination number, or checkout URL. No live telephony resource is created by this repository.

## Simulate the lifecycle

Run an inbound call that declines recording consent:

```bash
PYTHONPATH=src python -m call_simulator inbound --recording-consent no
```

Prove that an outbound call fails closed without prior contact permission:

```bash
PYTHONPATH=src python -m call_simulator outbound
```

Simulate a permitted outbound call with a data-minimized three-field capture:

```bash
PYTHONPATH=src python -m call_simulator outbound \
  --prior-contact-permission yes \
  --recording-consent yes \
  --supplied-field-count 3
```

The JSON output contains only lifecycle state, booleans, and a field count. It accepts no raw contact values, persists nothing, and explicitly reports `live_telephony_created: false`.

## Verify locally

```bash
python -m pytest -q
python -m ruff check .
```

The adapter tests statically verify disclosure, consent, legal, sensitive-data, checkout, and logging boundaries. The simulator tests execute inbound disclosure, outbound permission, opt-out, and data-minimization behavior without provider credentials.

## Deployment boundary

Before connecting a number, supply your own provider account, confirm recording and telemarketing requirements for every relevant jurisdiction, define retention and deletion rules, and replace the reference capture with a reviewed business-data sink. Do not use this sample for emergency, healthcare, financial, or other high-stakes decisions.

The commercial engineering offer and human-reviewed fit check are available at [article50-launch-patch-public.vercel.app](https://article50-launch-patch-public.vercel.app/). The public checkout is intentionally not exposed.
