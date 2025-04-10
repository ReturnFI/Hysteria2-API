import pytest
from unittest.mock import patch, MagicMock
from hysteria2_api import Hysteria2Client
from hysteria2_api.models import TrafficStats, OnlineStatus


@pytest.fixture
def client():
    return Hysteria2Client(base_url="http://localhost:25413", secret="test_secret")


def test_client_init():
    client = Hysteria2Client(base_url="http://test:1234", secret="secret123")
    assert client.base_url == "http://test:1234"
    assert "Authorization" in client._session.headers
    assert client._session.headers["Authorization"] == "secret123"


@patch("requests.Session.get")
def test_get_traffic_stats(mock_get, client):
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "user1": {"tx": 100, "rx": 200},
        "user2": {"tx": 300, "rx": 400}
    }
    mock_get.return_value = mock_response

    # Call method
    result = client.get_traffic_stats()

    # Assertions
    mock_get.assert_called_once_with("http://localhost:25413/traffic", timeout=10)
    assert len(result) == 2
    assert isinstance(result["user1"], TrafficStats)
    assert result["user1"].tx == 100
    assert result["user1"].rx == 200
    assert result["user2"].tx == 300
    assert result["user2"].rx == 400


@patch("requests.Session.get")
def test_get_online_clients(mock_get, client):
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"user1": 1, "user2": 2}
    mock_get.return_value = mock_response

    # Call method
    result = client.get_online_clients()

    # Assertions
    mock_get.assert_called_once_with("http://localhost:25413/online", timeout=10)
    assert len(result) == 2
    assert isinstance(result["user1"], OnlineStatus)
    assert result["user1"].connections == 1
    assert result["user1"].is_online is True
    assert result["user2"].connections == 2