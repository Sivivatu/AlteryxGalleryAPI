import os
from pathlib import Path

from AlteryxGallery import AlteryxGalleryAPI
from dotenv import load_dotenv

load_dotenv()

base_url = "https://spider.theinformationlab.co.uk/webapi/"

client_id: str = os.getenv("CLIENT_ID", "NoValueFound")
client_secret: str = os.getenv("CLIENT_SECRET", "NoValueFound")
owner_id: str = os.getenv("TEST_OWNER_ID", "NoValueFound")
file_path = Path("tests/Test_Upload.yxzp")
# payload = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}

# response = httpx.post(token_url, data=payload)

# print(response.url)
# print(response.status_code)
# print(response.text)


with AlteryxGalleryAPI.GalleryClient(base_url=base_url) as client:
    client.authenticate(client_id, client_secret)
    # response, content = client.get_all_workflows(name="00-Octopus Download Pipeline")
    # print(f"workflow query status response: {response.status_code}")
    # print(f"workflow query content: {content}")
    response, content = client.post_publish_workflow(file_path, "Test_Upload", owner_id)
    print(f"workflow publish query status response: {response.status_code}")
    print(f"workflow publish query content: {content}")
