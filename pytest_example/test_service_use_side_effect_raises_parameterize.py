import pytest
from unittest.mock import patch

import service


@pytest.mark.parametrize(
    "side_effect, expected, raises",
    [
        (lambda: True, True, None),
        (lambda: False, False, None),
        (RuntimeError("flag service down"), None, RuntimeError),
    ],
)
def test_should_process_request_parametrized(
    side_effect,
    expected,
    raises,
):
    with patch(
        "service.is_feature_enabled",
        side_effect=side_effect,
    ):
        if raises:
            with pytest.raises(raises):
                service.should_process_request()
        else:
            assert service.should_process_request() is expected



