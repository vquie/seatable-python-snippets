__author__ = "Vitali Quiering"
__version__ = "1.0.0-alpha"
import hashlib
import subprocess
import shlex
import os
from urllib.request import urlopen
import requests
from seatable_api import Base, context

# Define the name of the config table
server_url = context.server_url
api_token = context.api_token

# Create the Base object and authenticate
base = Base(api_token, server_url)
try:
    base.auth()
except Exception as e:
    print(f"Authentication failed with error: {e}")
    exit(1)

# Get the context
sites_table = "Sites"
sites_table_view = "Crawl"
content_table = "Content"

try:
    sites_rows = base.list_rows(sites_table, view_name=sites_table_view)
except Exception as e:
    print(f"Failed to get rows with error: {e}")
    exit(1)

for row in sites_rows:
    shahash = ''
    data = ''
    url = row['URL']
    try:
        response = urlopen(url)
        data = response.read()

        shahash = hashlib.sha256(data).hexdigest()

        # ... rest of your code
    except Exception as e:
        print(f"Failed to open URL {url} with error: {e}")

    data = response.read()

    shahash = hashlib.sha256(data).hexdigest()

    try:
        # Update row data
        update_result = base.update_row(sites_table, row['_id'], {'Hash': shahash})

        if update_result:
            print(f"Successfully updated hash for URL : {url}")
        else:
            print(f"Failed to update hash for URL : {url}")
    except Exception as e:
        print(f"Updating row failed with error: {e}")
