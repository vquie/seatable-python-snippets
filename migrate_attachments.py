"""
This script downloads file attachments from a SeaTable table row, uploads them to Seafile, and updates the table row with the new URLs.

Prerequisites:
- A SeaTable base and a Seafile library with valid credentials.
- A Seafile API key for the user that is used to connect to the API.

Usage:
1. Connect your SeaTable base to your Seafile library.
2. Create a Seafile API key for your user.
3. Import this script into your SeaTable base.
4. Run the script once. It will create a settings table.
5. Fill the values in the settings table:
   - seafile_host: the hostname or IP address of your Seafile server for the API calls.
   - seafile_api_token: the Seafile API token for your user (not the library).
   - seafile_library_id: the ID of your Seafile library.
   - seafile_library_api_token: the Seafile library API token that you used for connecting to Seafile.
   - seafile_dir: the parent directory of the uploaded files in your Seafile library.
6. Run the script in an automation or via a button.

Note: Make sure that your settings are correct before running the script.
"""
__author__ = "Vitali Quiering"
__version__ = "1.0.0-beta"

from datetime import datetime

import requests
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

    # Define the default rows to be added to the table
    default_rows = [
        {"Name": "seafile_host"},
        {"Name": "seafile_api_token"},
        {"Name": "seafile_library_id"},
        {"Name": "seafile_library_api_token"},
        {"Name": "seafile_dir", "value": ".seatable_uploads"},
    ]

    # Batch append the default rows to the table
    base.batch_append_rows(config_table, default_rows)


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


def get_upload_url(
    seafile_host, seafile_library_id, seafile_api_token, seafile_upload_dir
):
    """
    Get the URL for uploading files to a Seafile library.

    Args:
        seafile_host (str): The URL of the Seafile server.
        seafile_library_id (str): The ID of the Seafile library.
        seafile_api_token (str): The API token for accessing the Seafile server.
        seafile_upload_dir (str): The directory in the library to upload the files to.

    Returns:
        The URL for uploading files to the specified Seafile library and directory.
    """
    # Build the URL for requesting the upload link
    url = f"{seafile_host}/api2/repos/{seafile_library_id}/upload-link/?p={seafile_upload_dir}"

    # Set the headers for the request
    headers = {"Authorization": f"Token {seafile_api_token}"}

    # Send the request to the Seafile server
    response = requests.get(url, headers=headers)

    # Check if the response was successful (HTTP status code 200)
    if response.status_code == 200:
        # Get the upload link from the response and return it
        return response.json()
    else:
        # Raise an exception if the response was not successful
        raise Exception(
            f"Failed to get upload URL. Status code: {response.status_code}"
        )

def check_seafile_dir(dir):
    """
    Check if a given directory exists in the Seafile library.

    Args:
        dir (str): The directory to check.

    Returns:
        int: The HTTP status code indicating the result of the API request.

    """

    url = f"{seafile_host}/api/v2.1/repos/{seafile_library_id}/dir/detail/?path={dir}"
    headers = {"Authorization": f"Token {seafile_api_token}"}

    return requests.get(url, headers=headers)


def check_seafile_upload_dir(seafile_upload_dir):
    """
    Check if a given directory exists in the Seafile library.
    If it does not exist, create the directory.

    Args:
        seafile_upload_dir (str): The directory to check for.

    Returns:
        None
    """

    response = check_seafile_dir(seafile_upload_dir)

    while response.status_code == 404:
        create_seafile_upload_dir(seafile_upload_dir)

        # Get the details of the path again
        response = check_seafile_dir(seafile_upload_dir)

        # If the directory was successfully created, break out of the loop
        if response.status_code == 200:
            print("Directory exists: " + seafile_upload_dir)
            break

    if response.status_code != 200:
        print("Failed to create directory: " + seafile_upload_dir)


def create_seafile_upload_dir(seafile_upload_dir):
    """
    Create a directory in the Seafile library.

    Args:
        seafile_upload_dir (str): The directory to create.

    Returns:
        None
    """

    # Split the path into individual directories
    dirs = seafile_upload_dir.strip("/").split("/")

    # Loop through each directory and try to create it
    for i in range(1, len(dirs) + 1):
        dir_path = "/" + "/".join(dirs[:i])

        response = check_seafile_dir(dir_path)  # Call check_seafile_dir

        if response.status_code != 200:
            url = f"{seafile_host}/api/v2.1/repos/{seafile_library_id}/dir/?p={dir_path}"
            data = {"operation": "mkdir"}
            headers = {"Authorization": f"Token {seafile_api_token}"}
            
            response = requests.post(url, data=data, headers=headers)
            if response.status_code == 201:
                print("Created directory: " + dir_path)

def get_upload_dir():
    """
    Get the upload directory path in the Seafile library.
    The upload directory is named with the current date.

    Returns:
        str: The upload directory path.
    """

    now = datetime.now()
    date_string = now.strftime("%Y/%m/%d")

    return f"{seafile_dir}/{date_string}"


def upload_to_seafile(item_url, item_name):
    """
    Upload a file to the Seafile library.

    Args:
        item_url (str): The URL of the file to upload.
        item_name (str): The name of the file.

    Returns:
        str: The URL of the uploaded file in the Seafile library.
    """

    seafile_upload_dir = get_upload_dir()

    check_seafile_upload_dir(seafile_upload_dir)

    url = get_upload_url(
        seafile_host, seafile_library_id, seafile_api_token, seafile_upload_dir
    )
    headers = {"Authorization": f"Token {seafile_api_token}"}
    files = {"file": open(item_name, "rb")}
    data = {"parent_dir": f"/{seafile_upload_dir}"}
    requests.post(url, headers=headers, files=files, data=data)

    return f"seafile-connector://{seafile_library_api_token}/{seafile_upload_dir}/{item_name}"


def copy_attachments(column_data):
    """
    Copy attachments from Seatable to Seafile and update the URLs in the column data.

    Args:
        column_data (list): A list of dictionaries representing the attachments column data.

    Returns:
        list: A list of updated dictionaries representing the attachments column data with updated URLs.
    """

    updated_data = []
    if isinstance(column_data, list):
        for item in column_data:
            item_url = item["url"]
            item_name = item["name"]

            base.download_file(item_url, item_name)

            new_url = upload_to_seafile(item_url, item_name)
            item["url"] = new_url
            updated_data.append(item)

    return updated_data


check_config_table(config_table)
config_values = get_config_values(config_table)
locals().update(config_values)


def main():
    """Copy attachments from the 'file' columns of a SeaTable row, upload them to Seafile, and update the row data with the new URLs.

    Raises:
        ValueError: If the SeaTable row or any of its 'file' columns are not found.
    """
    # Get the current row data from SeaTable
    row = context.current_row
    if not row:
        raise ValueError("Row not found")

    # Iterate through the 'file' columns and copy the attachments
    updated_row_data = []
    columns = base.list_columns(table_name)
    for item in columns:
        if item.get("type") == "file":
            item.get("key")
            column_name = item.get("name")
            column_data = row.get(column_name)
            updated_data = copy_attachments(column_data)

            # Update the row data with the new URLs
            row_data = {column_name: updated_data}
            updated_row_data.append(row_data)

    # Update the row in SeaTable with the new URLs
    if updated_row_data:
        for row_data in updated_row_data:
            base.update_row(table_name, row["_id"], row_data)
    else:
        raise ValueError("No 'file' columns found in the row")


if __name__ == "__main__":
    main()
