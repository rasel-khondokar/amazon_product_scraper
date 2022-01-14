import requests
from requests.auth import HTTPBasicAuth

from settings import API_ENDPOINT


def save_to_api(payload):
    files = [

    ]

    response = requests.request("POST", API_ENDPOINT,  auth=HTTPBasicAuth('post_api', 'X84z Cuw6 008T Wu3O kXl7 eOJL'), data=payload, files=files)

    return response