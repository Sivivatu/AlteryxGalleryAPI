from alteryx_server_py.client import AlteryxClient
from alteryx_server_py.models.common import ExecutionMode


def test_serialize_form_data_normalizes_bool_enum_and_numbers():
	client = AlteryxClient(
		base_url="https://mock-gallery.com/webapi/",
		client_id="test_key",
		client_secret="test_secret",
	)

	serialized = client._serialize_form_data(
		{
			"isPublic": False,
			"executionMode": ExecutionMode.SAFE,
			"publishedVersionNumber": 3,
			"name": "Example",
		}
	)

	assert serialized == {
		"isPublic": "false",
		"executionMode": "Safe",
		"publishedVersionNumber": "3",
		"name": "Example",
	}
