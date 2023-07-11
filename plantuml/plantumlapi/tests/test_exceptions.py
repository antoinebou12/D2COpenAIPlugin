import pytest
from unittest import mock

from plantuml import PlantUMLHTTPError


def test_PlantUMLHTTPError():
    response = mock.Mock(status_code=404, reason_phrase='Not Found')
    content = b'The requested resource was not found.'
    with pytest.raises(PlantUMLHTTPError) as excinfo:
        raise PlantUMLHTTPError(response, content)