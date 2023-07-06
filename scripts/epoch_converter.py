"""
__author__ = "Vitali Quiering"
__version__ = "1.0.0"
"""

import datetime
from seatable_api import Base, context

# Get the server URL and API token from the context
server_url = context.server_url
api_token = context.api_token

# Create a base object and authenticate with the API token and server URL
base = Base(api_token, server_url)
base.auth()

# Get the current row and table name from the context
row = context.current_row
table_name = context.current_table

# Define the source and target columns
_source_column="DateTime"
_target_column="EpochTime"

# Get the ISO timestamp from the row
_iso_datetime = row[_source_column]

# Convert the ISO timestamp to a datetime object
dt = datetime.datetime.fromisoformat(_iso_datetime)

# Get the epoch time in seconds
_epoch_time = int(dt.timestamp())

# Update the row data with the epoch time
row_data = {
    _target_column: _epoch_time
}

# Update the row in the base
base.update_row(table_name, row["_id"], row_data)