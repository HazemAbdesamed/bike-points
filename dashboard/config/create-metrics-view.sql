CREATE OR REPLACE VIEW kafka.default.v_realtime_metrics AS 

SELECT 
  json_extract_scalar(_message, '$.min_extraction_datetime') AS min_extraction_datetime,
  json_extract_scalar(_message, '$.max_extraction_datetime') AS max_extraction_datetime,
  json_extract_scalar(_message, '$.percentage_available_bikes') AS percentage_available_bikes,
  json_extract_scalar(_message, '$.nb_in_use_bikes') AS nb_in_use_bikes,
  json_extract_scalar(_message, '$.percentage_in_use_bikes') AS percentage_in_use_bikes,
  json_extract_scalar(_message, '$.nb_broken_docks') AS nb_broken_docks,
  json_extract_scalar(_message, '$.percentage_broken_docks') AS percentage_broken_docks
FROM kafka.default.metrics
WHERE _message <> '{}'
ORDER BY
  from_iso8601_timestamp(json_extract_scalar(_message, '$.max_extraction_datetime')) DESC,
  from_iso8601_timestamp(json_extract_scalar(_message, '$.min_extraction_datetime')) DESC
LIMIT 1
;