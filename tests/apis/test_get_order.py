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
def test_get_order_authorization(headers, expected_status):
    response = client.get("/api/getOrder", headers=headers)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "headers, query_params",
    [
        (
            {"Authorization": "Bearer valid_token"},
            {
                "date": "2023-12-15",
                "buySell": "B",
                "topLevel": "Y",
                "ticker": "AAPL",
                "counterparty": "XYZ",
            },
        ),
    ],
)
def test_get_order_with_query_params(headers, query_params):
    response = client.get("/getOrder", headers=headers, params=query_params)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "data" in response.json()
    assert "timestamp" in response.json()
    assert "pagination" in response.json()
