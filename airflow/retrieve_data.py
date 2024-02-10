import requests
import datetime
import json 

def get_bikepoints_from_api():
    url = 'https://api.tfl.gov.uk/BikePoint/'
    return requests.get(url).json()



def select_properties(bikepoints_data):
    
    bikepoints = []

    for bikepointInfo in bikepoints_data :
        item = {
            "id": bikepointInfo["id"],
            "commonName": bikepointInfo["commonName"],
            "lat": str(bikepointInfo["lat"]),
            "lon": str(bikepointInfo["lon"])
        }

        recent_datetime = None
        for detail in bikepointInfo['additionalProperties']:
            if detail['key'] in ("NbDocks", "NbBikes", "NbEBikes", 
                                "NbEmptyDocks", "Installed", "Locked"):
                
                item[detail["key"]] = detail['value']
            
            # Get the most recent modified datetime of the objects
            modified_datetime = str(detail['modified'])
            if recent_datetime == None or \
            recent_datetime < modified_datetime:
                recent_datetime = modified_datetime    
            item['extracted_datetime'] = recent_datetime

        bikepoints.append(item)

    return bikepoints