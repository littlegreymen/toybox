import pytest
from unittest.mock import patch

import service


@pytest.fixture
def feature_enabled():
    """
    Patch using side_effect to return True.
    """
    def enabled_side_effect():
        return True

    with patch("service.is_feature_enabled", side_effect=enabled_side_effect):
        yield


@pytest.fixture
def feature_disabled():
    """
    Patch using side_effect to return False.
    """
    def disabled_side_effect():
        return False

    with patch("service.is_feature_enabled", side_effect=disabled_side_effect):
        yield


def test_should_process_request_when_enabled(feature_enabled):
    assert service.should_process_request() is True


def test_should_process_request_when_disabled(feature_disabled):
    assert service.should_process_request() is False

