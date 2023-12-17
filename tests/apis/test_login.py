import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apac_coe_technical_test_fall_2023.api.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "username, password, expected_status_code",
    [
        (None, None, status.HTTP_500_INTERNAL_SERVER_ERROR),
        ("username", "password", status.HTTP_401_UNAUTHORIZED),
        ("admin", "secret", status.HTTP_200_OK),
    ],
)
def test_login(username, password, expected_status_code):
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    assert response.status_code == expected_status_code
