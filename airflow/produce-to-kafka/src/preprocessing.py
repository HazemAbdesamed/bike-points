def select_properties(bikepoints_data):
    
    bikepoints = []

    for bikepointInfo in bikepoints_data :
        item = {
            "id": bikepointInfo["id"],
            "commonName": bikepointInfo["commonName"],
            "lat": str(bikepointInfo["lat"]),
            "lon": str(bikepointInfo["lon"])
        }

        
        for detail in bikepointInfo['additionalProperties']:
            if detail['key'] in ("NbDocks", "NbBikes", "NbEBikes", 
                                "NbEmptyDocks", "Installed", "Locked"):
                
                item[detail["key"]] = detail['value']
            
        # Get the most recent modified datetime of the objects
        recent_datetime = max(detail['modified'] for detail in bikepointInfo['additionalProperties'])
        item['extracted_datetime'] = str(recent_datetime) 
        bikepoints.append(item)

    return bikepoints