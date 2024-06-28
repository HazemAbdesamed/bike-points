from utils import logger
import requests

def get_bikepoints_from_api():
    """Fetch bikepoints data from the API"""
    try :
        url = 'https://api.tfl.gov.uk/BikePoint/'
        logger.info("bikepoints data have been fetched from the API successfully", len(requests.get(url).json()))
        
        return requests.get(url).json()
    except :
        logger.error("Error in fetching data from the API")