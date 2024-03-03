from .utils import logger

def select_fields(bikepoints_data):
    """Preprocess data, Select the fields of the fetched data"""
    bikepoints = []

    for bikepointInfo in bikepoints_data :
        processed_bikepoint = {
            "Id": bikepointInfo["id"],
            "CommonName": bikepointInfo["commonName"],
            "Lat": str(bikepointInfo["lat"]),
            "Lon": str(bikepointInfo["lon"])
        }

        
        for detail in bikepointInfo['additionalProperties']:
            if detail['key'] in ("Installed", "Locked"):
                processed_bikepoint[detail["key"]] = detail['value']
            
            if detail['key'] in ("NbDocks", "NbBikes", "NbEBikes", 
                                "NbEmptyDocks"):
                processed_bikepoint[detail["key"]] = int(detail['value'])
            
        # Get the most recent modified datetime of the objects
        recent_datetime = max(detail['modified'] for detail in bikepointInfo['additionalProperties'])
        processed_bikepoint['ExtractionDatetime'] = str(recent_datetime) 
        bikepoints.append(processed_bikepoint)
    
    logger.info("Preprocessing completed successfully")
    return bikepoints