#!/bin/sh
# Generate openapi schema from running local instance.
SERVER=http://localhost:8080/v1
OUTPUT_DIR=../../src/ska_src_site_capabilities_api/rest/openapi

# get the openapi.json schema and make sure the server attr is populated
curl http://localhost:8080/v1/openapi.json --output $OUTPUT_DIR/openapi.json




