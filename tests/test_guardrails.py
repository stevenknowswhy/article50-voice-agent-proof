import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
SOURCE = (ROOT / "src" / "agent.py").read_text()
README = (ROOT / "README.md").read_text()
VAPI = json.loads((ROOT / "vapi-assistant.example.json").read_text())
DEMO_TRANSCRIPT_PATH = ROOT / "docs" / "fictional-call-demo.md"
DEMO_AUDIO_PATH = ROOT / "docs" / "fictional-call-demo.mp3"


def test_livekit_agent_discloses_ai_identity_and_offer_boundary() -> None:
    assert "AI voice agent for Forhemit Labs" in SOURCE
    assert "nine-thousand-eight-hundred-dollar" in SOURCE
    assert "five business days" in SOURCE
    assert "one TypeScript or JavaScript web product" in SOURCE
    assert "three buyer-approved surfaces" in SOURCE
    assert "twenty-four engineering hours" in SOURCE


def test_livekit_agent_reserves_legal_decisions_and_checkout() -> None:
    assert "Forhemit is not a law firm" in SOURCE
    assert "Never decide whether Article 50 applies" in SOURCE
    assert "Buyer counsel" in SOURCE
    assert "Never share a checkout link on a call" in SOURCE


def test_livekit_agent_requires_consent_and_minimizes_sensitive_data() -> None:
    assert "ask the caller for permission to record" in SOURCE
    assert "only if they explicitly agree" in SOURCE
    assert "If they decline, do not call the tool" in SOURCE
    assert "Never request passwords" in SOURCE
    assert "payment-card details" in SOURCE


def test_capture_fails_closed_and_does_not_log_raw_lead_values() -> None:
    assert SOURCE.index("consent_confirmed: bool") < SOURCE.index(
        "if not consent_confirmed:"
    )
    assert "No fit details were recorded" in SOURCE
    assert "raw_values_logged=false" in SOURCE
    assert "json.dumps" not in SOURCE


def test_vapi_adapter_has_the_same_public_boundaries() -> None:
    instructions = VAPI["model"]["messages"][0]["content"]
    assert VAPI["firstMessage"].startswith("Hello, I")
    assert "AI voice agent" in VAPI["firstMessage"]
    assert "Never decide whether Article 50 applies" in instructions
    assert "ask the caller for permission to record" in instructions
    assert "Never share a checkout link by phone" in instructions
    assert VAPI["maxDurationSeconds"] == 300


def test_public_tree_contains_no_live_telephony_or_checkout_values() -> None:
    public_text_files = [
        ROOT / ".gitignore",
        ROOT / "Dockerfile",
        ROOT / "LICENSE",
        ROOT / "README.md",
        ROOT / "SECURITY.md",
        ROOT / "pyproject.toml",
        ROOT / "src" / "agent.py",
        ROOT / "vapi-assistant.example.json",
    ]
    combined = "\n".join(
        path.read_text() for path in public_text_files
    )
    assert "existing_phone" not in combined
    assert "destination_number" not in combined
    assert "api_key" not in combined.lower()
    assert "buy.stripe.com" not in combined
    assert "No live telephony resource is created" in README


def test_fictional_audio_demo_is_labeled_and_data_minimized() -> None:
    transcript = DEMO_TRANSCRIPT_PATH.read_text()

    assert "Fictional local audio rendering" in transcript
    assert "not a recording of a phone call" in transcript
    assert "No contact details were captured" in transcript
    assert "We did not make a live phone call" in transcript
    assert "AI voice agent for Forhemit Labs" in transcript
    assert "I don't provide legal advice" in transcript
    assert "May I collect business details for a human follow-up?" in transcript
    assert "Please don't share credentials or source code" in transcript
    assert "buy.stripe.com" not in transcript
    assert "destination_number" not in transcript
    assert "docs/fictional-call-demo.mp3" in README


def test_fictional_audio_demo_is_a_nonempty_mp3() -> None:
    payload = DEMO_AUDIO_PATH.read_bytes()

    assert len(payload) > 10_000
    assert payload.startswith(b"ID3") or payload[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"}
