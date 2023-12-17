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
    "query_params",
    [
        {"buySell": "B"},
        {"counterparty": "FIS"},
        {"date": "2023-01-03"},
        {"topLevel": "Y"},
    ],
)
def test_get_order_with_query_params(query_params):
    headers = {"Authorization": f"Bearer {SAMPLE_USER_TOKEN}"}
    params = query_params
    response = client.get("/api/getOrder", headers=headers, params=params)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "query_params",
    [
        {"buySell": "T"},
        {"date": "2023-13-03"},
    ]
)
def test_get_order_with_invalid_query_params(query_params):
    headers = {"Authorization": f"Bearer {SAMPLE_USER_TOKEN}"}
    response = client.get("/api/getOrder", headers=headers, params=query_params)
    assert response.status_code == 400