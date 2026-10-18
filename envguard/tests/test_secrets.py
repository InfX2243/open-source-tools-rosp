from envguard.core.secrets import (
    calculate_entropy,
    mask_secret,
    scan_text_for_secrets,
)


def test_calculate_entropy():
    # Low entropy: all same characters
    low = calculate_entropy("aaaaaaaa")
    # High entropy: random alphanumeric
    high = calculate_entropy("gT9!xP#2qZ90Lkm@")
    assert low < high
    assert low == 0.0


def test_mask_secret():
    masked = mask_secret("AKIA1234567890ABCDEF")
    assert masked.startswith("AKI")
    assert masked.endswith("EF")
    assert "*" in masked
    assert "1234567890ABCD" not in masked


def test_scan_text_for_secrets():
    content = """
    DEBUG=true
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456
    """
    findings = scan_text_for_secrets(content)
    assert len(findings) == 2
    types = [f.secret_type for f in findings]
    assert "AWS Access Key ID" in types
    assert "OpenAI API Key" in types
