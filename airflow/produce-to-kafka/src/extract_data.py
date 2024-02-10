import requests

def get_bikepoints_from_api():
    url = 'https://api.tfl.gov.uk/BikePoint/'
    return requests.get(url).json()