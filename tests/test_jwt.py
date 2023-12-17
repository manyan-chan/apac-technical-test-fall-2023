from apac_coe_technical_test_fall_2023.jwt.auth import (
    SAMPLE_EXPIRED_TOKEN,
    SAMPLE_USER_TOKEN,
    generate_token,
    verify_token,
)


def test_valid_token_returns_true():
    result = verify_token(SAMPLE_USER_TOKEN)
    assert result is True


def test_expired_token_returns_false():
    result = verify_token(SAMPLE_EXPIRED_TOKEN)
    assert result is False


def test_token_with_invalid_payload_returns_false():
    token = generate_token({"username": "test", "password": "test"})
    result = verify_token(token)
    assert result is False
