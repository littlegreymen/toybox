import pytest
from unittest.mock import patch

import service


@pytest.fixture
def feature_enabled():
    """
    Fixture that patches is_feature_enabled to return True.
    """
    with patch("service.is_feature_enabled", return_value=True):
        yield


@pytest.fixture
def feature_disabled():
    """
    Fixture that patches is_feature_enabled to return False.
    """
    with patch("service.is_feature_enabled", return_value=False):
        yield


def test_should_process_request_when_enabled(feature_enabled):
    assert service.should_process_request() is True


def test_should_process_request_when_disabled(feature_disabled):
    assert service.should_process_request() is False
