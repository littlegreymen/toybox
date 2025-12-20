import pytest
from unittest.mock import patch

import service


@pytest.fixture
def feature_flag_error():
    """
    Patch is_feature_enabled to raise an exception.
    """
    with patch(
        "service.is_feature_enabled",
        side_effect=RuntimeError("feature flag service unavailable"),
    ):
        yield


def test_should_process_request_raises_when_flag_service_fails(
    feature_flag_error,
):
    with pytest.raises(RuntimeError, match="feature flag service unavailable"):
        service.should_process_request()


