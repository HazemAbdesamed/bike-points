from src.utils import logger

def select_fields(bikepoints_data):
    """Preprocess data, Select the fields of the fetched data"""
    bikepoints = []

    for bikepointInfo in bikepoints_data :
        item = {
            "Id": bikepointInfo["id"],
            "CommonName": bikepointInfo["commonName"],
            "Lat": str(bikepointInfo["lat"]),
            "Lon": str(bikepointInfo["lon"])
        }

        
        for detail in bikepointInfo['additionalProperties']:
            if detail['key'] in ("NbDocks", "NbBikes", "NbEBikes", 
                                "NbEmptyDocks", "Installed", "Locked"):
                
                item[detail["key"]] = detail['value']
            
        # Get the most recent modified datetime of the objects
        recent_datetime = max(detail['modified'] for detail in bikepointInfo['additionalProperties'])
        item['ExtractedDatetime'] = str(recent_datetime) 
        bikepoints.append(item)
    
    logger.info("Preprocessing completed successfully")
    return bikepoints