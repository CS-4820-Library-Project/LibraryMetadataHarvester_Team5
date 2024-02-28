import json
import requests
from requests.auth import HTTPBasicAuth


def request_authentication_key_from_oclc():
    base_url = "https://oauth.oclc.org/token"
    client_id = "d2au8EHInSt5k21k3CJDlLe4Dn2FlXGEQ1LiNOWaWKIznGSAzEzwqMw9XsBSAbMsUImvplz98B5smA7J"
    secret = "Qjcq0YS93zZY52DK0Z6tDBluVZoUSXSR"

    headers = {'Accept': 'application/json'}
    params = {'grant_type': 'client_credentials', 'scope': 'WorldCatMetadataAPI'}

    try:
        response = requests.get(base_url, auth=HTTPBasicAuth(client_id, secret), params=params, headers=headers)
        response_data = response.json()
        print(response.text)

        if 'access_token' in response_data:
            access_token = response_data['access_token']
            print(f"Access Token: {access_token}")
        else:
            print("Error: Access token not found in response.")
    except Exception as e:
        print(f"Error retrieving access token from OCLC: {e}")
        return None


def retrieve_data_from_oclc(oclc):
    base_url = "https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs/"
    full_url = f"{base_url}{oclc}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.content.decode('utf-8')  # Decode the byte string

        # Extract JSON data from the response (assuming the JSON is inside parentheses)
        json_start = data.find('(') + 1
        json_end = data.rfind(')')
        json_data = data[json_start:json_end]

        # Parse the extracted JSON data
        parsed_data = json.loads(json_data)

        return parsed_data
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from OCLC: {e}")
        return None
