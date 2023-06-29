"""
WORK IN PROGRESS
"""
__author__ = "Vitali Quiering"
__version__ = "0.1.0-alpha"

from datetime import datetime

from seatable_api import Base, context
from seatable_api.constants import ColumnTypes

# config
config_table = "_settings"

server_url = context.server_url
api_token = context.api_token

base = Base(api_token, server_url)
base.auth()

# get context
row = context.current_row
table_name = context.current_table


def update_config_rows():
    config_rows = base.list_rows(config_table)
    default_rows = [
        {"Name": "seafile_host2"},
    ]
    for default_row in default_rows:
        for config_row in config_rows:
            if config_row["Name"] == default_row["Name"]:
                config_row.update(default_row)
    print(config_rows)


def create_config_table(config_table):
    """
    Add a config table to the database with a 'value' column and pre-populate it with default values.

    Args:
        config_table (str): Name of the table to create.

    Returns:
        None
    """
    # Add the table to the database
    base.add_table(config_table)

    # Add a 'value' column to the table
    base.insert_column(config_table, "value", ColumnTypes.TEXT)

    update_config_rows()


def check_config_table(config_table):
    """
    Check if a config table exists, and create it if it does not.

    Args:
        config_table (str): Name of the table to check.

    Returns:
        None
    """
    # Get the metadata for the database
    base_metadata = base.get_metadata()

    # Check if the config table exists
    config_table_found = any(
        table["name"] == config_table for table in base_metadata["tables"]
    )

    # If the config table does not exist, create it
    if not config_table_found:
        create_config_table(config_table)
    else:
        update_config_rows()

def get_config_values(config_table):
    """
    Retrieve the values in a config table.

    Args:
        config_table (str): Name of the config table.

    Returns:
        A dictionary mapping config keys to their values.
    """
    # Get the rows in the config table
    rows = base.list_rows(config_table)

    # Create a dictionary to store the config values
    config_dict = {}

    # Iterate over the rows and add the non-empty 'value' fields to the dictionary
    for row in rows:
        if "value" in row and row["value"]:
            config_dict[row["Name"]] = row["value"]

    return config_dict

check_config_table(config_table)
config_values = get_config_values(config_table)
locals().update(config_values)