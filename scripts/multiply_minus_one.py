"""
This script is used to multiply a value with -1. We need this to make a negative value positive.
That's it. :-)

Prerequisites:
- Update "column" in this script with your column name.
"""

__author__ = "Vitali Quiering"
__version__ = "1.0.0"

from seatable_api import Base, context

server_url = context.server_url
api_token = context.api_token

base = Base(api_token, server_url)
base.auth()

column="update-me"

def update_row_data():
    row = context.current_row

    row_id = context.current_row["_id"]
    negative_value = row[column]

    positive_value = negative_value * -1

    row_data = {
        column: positive_value
    }

    base.update_row(context.current_table, row_id, row_data)

update_row_data()
