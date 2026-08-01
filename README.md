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

## Two adapters

- `src/agent.py` is a LiveKit Agents reference implementation for an inbound RTC session.
- `vapi-assistant.example.json` is a provider-neutralized Vapi assistant definition with the same conversation boundaries.

Neither adapter contains a phone number, API key, provider account identifier, destination number, or checkout URL. No live telephony resource is created by this repository.

## Verify locally

```bash
python -m pytest -q
python -m ruff check .
```

The tests are deliberately static: they verify that the disclosure, consent, legal, sensitive-data, checkout, and logging boundaries remain present even when provider credentials are unavailable.

## Deployment boundary

Before connecting a number, supply your own provider account, confirm recording and telemarketing requirements for every relevant jurisdiction, define retention and deletion rules, and replace the reference capture with a reviewed business-data sink. Do not use this sample for emergency, healthcare, financial, or other high-stakes decisions.

The commercial engineering offer and human-reviewed fit check are available at [article50-launch-patch-public.vercel.app](https://article50-launch-patch-public.vercel.app/). The public checkout is intentionally not exposed.
