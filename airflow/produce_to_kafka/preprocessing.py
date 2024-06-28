from utils import logger
from datetime import datetime
from dateutil import parser

def select_fields(bikepoints_data):
    """Preprocess data, Select the fields of the fetched data"""
    
    # Get the system's local timezone
    system_timezone = datetime.now().astimezone().tzinfo
    
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
        recent_datetime = max(parser.isoparse(detail['modified']) for detail in bikepointInfo['additionalProperties'])
        processed_bikepoint['ExtractionDatetime'] = str(recent_datetime.astimezone(system_timezone).strftime("%Y-%m-%d %H:%M:%S"))

        bikepoints.append(processed_bikepoint)
    
    logger.info("Preprocessing completed successfully")
    return bikepoints