import pytest
from unittest.mock import patch

import service


@pytest.mark.parametrize(
    "side_effect, expected",
    [
        (True, True),
        (False, False),
    ],
)
def test_should_process_request_with_patch_object(
    side_effect,
    expected,
):
    with patch.object(
        service,
        "is_feature_enabled",
        autospec=True,
        side_effect=lambda: side_effect,
    ):
        assert service.should_process_request() is expected

