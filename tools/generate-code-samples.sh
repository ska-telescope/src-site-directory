#!/bin/sh
# Generate openapi code samples automatically from an openapi.json schema.
SERVER=http://localhost:8080/v1
OUTPUT_DIR=../src/ska_src_site_capabilities_api/rest/request-code-samples

# get the openapi.json schema and make sure the server attr is populated
curl http://localhost:8080/v1/openapi.json --output openapi.json
jq '.servers = [{"url": "'$SERVER'"}]' openapi.json > openapi.json.tmp
mv openapi.json.tmp openapi.json

# add the snippets
touch openapi-with-snippets.json
docker run -v ${PWD}/openapi.json:/tmp/openapi.json -v ${PWD}/openapi-with-snippets.json:/tmp/openapi-with-snippets.json --network host node:latest sh -c " \
  cd /tmp && npm install snippet-enricher-cli &&
  ./node_modules/.bin/snippet-enricher-cli --input=openapi.json --targets=\"python_requests,shell_curl,go_native,node_native\" > enriched.json && \
  cp enriched.json /tmp/openapi-with-snippets.json
"
sed -i 's/Shell + Curl/shell/g' openapi-with-snippets.json
sed -i 's/Node + Native/js/g' openapi-with-snippets.json
sed -i 's/Python + Requests/python/g' openapi-with-snippets.json
sed -i 's/Go + Native/go/g' openapi-with-snippets.json

# parse the schema for the snippets
python3 -c '
import json
import os
from urllib.parse import unquote

with open("openapi-with-snippets.json") as f:
  openapi_schema = json.loads(f.read())

if not(os.path.exists("'$OUTPUT_DIR'") and os.path.isdir("'$OUTPUT_DIR'")):
  os.mkdir("'$OUTPUT_DIR'")

servers = openapi_schema.get("servers")
urls = [server.get("url") for server in servers]

for path, methods in openapi_schema.get("paths").items():
  for method, attr in methods.items():
    code_samples = attr.get("x-codeSamples", [])
    for code_sample in code_samples:
      lang = code_sample.get("lang")
      source = unquote(code_sample.get("source"))
      filename = "{}-{}-{}.j2".format(lang, path.lstrip("/").replace("/", "-"), method)
      with open(os.path.join("'$OUTPUT_DIR'", filename), "w") as f:
        f.write(source.replace("'$SERVER'", "{{ api_server_url }}"))
'

rm openapi.json
rm openapi-with-snippets.json

