import json
import requests
from Alteryx_Gallery.gallery_connection import Gallery


class GallerySubscription(Gallery):
    '''Extends the Gallery Class containing connection to access Alteryx Server API endpoints'''
    def __init__(self, api_location: str, api_key: str, api_secret: str):
        Gallery.__init__(self, api_location, api_key, api_secret)
        super().__init__(self.api_location, self.api_key, self.api_secret)
        self.api_version = "/api/v1"

    def subscription(self):
        """
        :return: workflows in a subscription
        """
        method = 'GET'
        url = f"{self.api_location}{self.api_version}/workflows/subscription/"
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})
        response = requests.get(url, params=params)
        output, output_content = response, json.loads(response.content.decode("utf8"))
        return output, output_content

    def questions(self, app_id):
        """
        :return: Returns the questions for the given Alteryx Analytics App
        """
        method = 'GET'
        url = self.api_location + self.api_version + '/workflows/' + app_id + '/questions/'
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})
        response = requests.get(url, params=params)
        output, output_content = response, json.loads(response.content.decode("utf8"))
        return output, output_content

    def execute_workflow(self, app_id, **kwargs):
        """
        Queue an app execution job.
        :return:  Returns ID of the job
        """
        method = 'POST'
        url = self.api_location + self.api_version + '/workflows/' + app_id + '/jobs/'
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})

        if 'payload' in kwargs:
            output = requests.post(url,
                                   json=kwargs['payload'],
                                   headers={'Content-Type': 'application/json'},
                                   params=params)
        else:
            response = requests.post(url, params=params)

        output, output_content = response, json.loads(response.content.decode("utf8"))
        return output, output_content

    def get_jobs(self, app_id):
        """
        :return: Returns the jobs for the given Alteryx Analytics App
        """
        method = 'GET'
        url = self.api_location + self.api_version + '/workflows/' + app_id + '/jobs/'
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})
        response = requests.get(url, params=params)
        output, output_content = response, json.loads(response.content.decode("utf8"))
        return output, output_content

    def get_job_status(self, job_id):
        """
        :return: Retrieves the job and its current state
        """
        method = 'GET'
        url = self.api_location + self.api_version + '/jobs/' + job_id + '/'
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})
        response = requests.get(url, params=params)
        output, output_content = response, json.loads(response.content.decode("utf8"))
        return output, output_content

    def get_job_output(self, job_id, output_id):
        """
        :return: Returns the output for a given job (FileURL)
        """
        method = 'GET'
        url = self.api_location + self.api_version + '/jobs/' + job_id + '/output/' + output_id + '/'
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})
        response = requests.get(url, params=params)
        output, output_content = response, response.content.decode("utf8")
        return output, output_content

    def get_app(self, app_id):
        """
        :return: Returns the App that was requested
        """
        method = 'GET'
        url = self.api_location + self.api_version + '/' + app_id + '/package/'
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})
        response = requests.get(url, params=params)
        output, output_content = response, json.loads(response.content.decode("utf8"))
        return output, output_content
