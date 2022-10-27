#!/bin/python
import os
import sys
import json
import urllib.request
from zipfile import ZipFile
import http.client

conn = http.client.HTTPSConnection("api.lokalise.co")

headers = {
    "content-type": "application/json",
    "x-api-token": "50226dfe9152847d3f5f34450aaffcedb1542d0f",
}

# Specify the way we want our languages formatted
payload = {
    "format": "yml",
    "filter_data": ["translated"],
    "export_empty_as": "skip",
    "yaml_include_root": False,
    "bundle_structure": "%LANG_NAME%.%FORMAT%",
    "original_filenames": False,
    "replace_breaks": False,
    "export_sort": "first_added",
}

# Get the download location for our locales
json_payload = json.dumps(payload)
conn.request(
    "POST",
    "/api2/projects/968164875d56075abf8d04.48812740/files/download",
    json_payload,
    headers,
)
res = conn.getresponse()
data = res.read()

try:
    # Extract the url from the response
    response = json.loads(data)
    url = response["bundle_url"]
except:  # noqa E722
    print(response)
    sys.exit(1)

# Download the language bundle
file_name = "/tmp/languages.zip"
urllib.request.urlretrieve(url, file_name)

# Extract all the contents of zip file in i18n
with ZipFile(file_name, "r") as zipObj:
    zipObj.extractall("i18n")

os.rename("i18n/Portuguese__28Brazil_29.yml", "i18n/Portuguese (Brazil).yml")
