# pytest -v tests/test_bark.py
from unittest.mock import MagicMock, patch

import pytest
import requests

from utils.bark import Bark  # Replace 'your_module' with the actual module name


@pytest.fixture
def bark_instance():
    return Bark("test_group")


@patch("utils.bark.requests.get")
def test_send_notification_success(mock_get, bark_instance):
    # Mock the successful response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = bark_instance.send(
        title="Test Title",
        body="Test Body",
        url="http://test.url",
        sound="test_sound",
        icon_url="http://test.icon",
        level="active",
        is_archive=1,
    )

    assert result is True
    mock_get.assert_called_once()
    # You might want to add more specific assertions about the URL here


@patch("utils.bark.requests.get")
def test_send_notification_failure(mock_get, bark_instance):
    # Mock the failed response
    mock_get.side_effect = requests.RequestException("Test error")

    result = bark_instance.send(
        title="Test Title", body="Test Body", url="http://test.url"
    )

    assert result is False
    mock_get.assert_called_once()
