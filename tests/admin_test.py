import pytest
from AlteryxGallery.Admin import admin
from decouple import config

client_key = config('client_key')
client_secret = config('client_secret')
apiLocation = config('gallery_url')

con = admin.GalleryAdmin(apiLocation, client_key, client_secret)

class TestGallery:  
    def workflows_migratable(self):
        response = con.get_workflows_migratable()[0]
        assert response.status_code == 200

    def post_workflow(self):
        response = con.post_workflows_migratable()[0]
        assert response.status_code == 200