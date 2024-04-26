import os
from pathlib import Path

import requests
from AlteryxGallery import AlteryxGalleryAPI
from dotenv import load_dotenv

load_dotenv()

host_url: str = os.getenv("HOST_URL", "NoValueFound")

client_id: str = os.getenv("CLIENT_ID", "NoValueFound")
client_secret: str = os.getenv("CLIENT_SECRET", "NoValueFound")
owner_id: str = os.getenv("TEST_OWNER_ID", "NoValueFound")
file_path = Path("tests/Test_Upload.yxzp")
# payload = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}

# response = httpx.post(token_url, data=payload)

# print(response.url)
# print(response.status_code)
# print(response.text)


# with AlteryxGalleryAPI.GalleryClient(host_url=host_url) as client:
#     client.authenticate(client_id, client_secret)
# response, content = client.get_all_workflows(name="00-Octopus Download Pipeline")
# print(f"workflow query status response: {response.status_code}")
# print(f"workflow query content: {content}")
# response, content = client.post_publish_workflow(file_path, "Test_Upload", owner_id)
# print(f"workflow publish query status response: {response.status_code}")
# print(f"workflow publish query content: {content}")


client = AlteryxGalleryAPI.GalleryClient(
    host_url=host_url, client_id=client_id, client_secret=client_secret
)
print(client)

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)
