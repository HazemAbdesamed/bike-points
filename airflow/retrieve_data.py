import requests

def get_bikepoints_from_api():
    url = 'https://api.tfl.gov.uk/BikePoint/'
    return requests.get(url).json()


def select_properties(bikepoints_data):
    
    bikepoints = []

    for bikepointInfo in bikepoints_data :
        item = {
            "id": bikepointInfo["id"],
            "commonName": bikepointInfo["commonName"],
            "lat": bikepointInfo["lat"],
            "lon": bikepointInfo["lon"]
        }
        
        for detail in bikepointInfo['additionalProperties']:
            if detail['key'] in ("NbDocks", "NbBikes", "NbEBikes", 
                                "NbEmptyDocks", "Installed", "Locked"):
                
                item[detail["key"]] = detail['value']

        bikepoints.append(item)
    
    return bikepoints


