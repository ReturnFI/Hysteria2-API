import pytest
from hysteria2_api.models import TrafficStats, OnlineStatus


def test_traffic_stats():
    stats = TrafficStats(tx=100, rx=200)
    assert stats.tx == 100
    assert stats.rx == 200
    assert stats.upload_bytes == 100
    assert stats.download_bytes == 200


def test_traffic_stats_from_dict():
    stats = TrafficStats.from_dict({"tx": 100, "rx": 200})
    assert stats.tx == 100
    assert stats.rx == 200

    # Test with missing fields
    stats = TrafficStats.from_dict({"tx": 100})
    assert stats.tx == 100
    assert stats.rx == 0


def test_online_status():
    status = OnlineStatus(connections=2)
    assert status.connections == 2
    assert status.is_online is True

    status = OnlineStatus(connections=0)
    assert status.connections == 0
    assert status.is_online is False


def test_online_status_from_int():
    status = OnlineStatus.from_int(2)
    assert status.connections == 2
    assert status.is_online is True