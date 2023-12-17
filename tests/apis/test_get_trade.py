import pytest
from fastapi.testclient import TestClient

from apac_coe_technical_test_fall_2023.api.main import app
from apac_coe_technical_test_fall_2023.jwt.auth import SAMPLE_USER_TOKEN

client = TestClient(app)

@pytest.mark.parametrize(
    "headers, expected_status",
    [
        (None, 401),
        ({"Authorization": "Bearer invalid_token"}, 401),
        ({"Authorization": f"Bearer {SAMPLE_USER_TOKEN}"}, 200),
    ],
)
def test_get_trade_authorization(headers, expected_status):
    response = client.get("/api/getTrade", headers=headers)
    assert response.status_code == expected_status