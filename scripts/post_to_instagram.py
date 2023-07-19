"""
This script is designed to interact with the SeaTable API and perform operations related to Google Vision API labels.
It requires the `seatable-api` package to be installed.
"""

__author__ = "Vitali Quiering"
__version__ = "1.0.1-alpha"

import requests
from seatable_api import Base, context

# config
config_table = "_settings"
image_column = "Image"
text = "Text"

server_url = context.server_url
api_token = context.api_token

base = Base(api_token, server_url)
base.auth()

# get context
row = context.current_row
table_name = context.current_table

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

    # If the config table does not exist, exit with an error message
    if not config_table_found:
        raise SystemExit("Config table not found!")
    
def get_instagram_user_token(user_access_token):
    print(user_access_token)
    # Step 3: Request Instagram Account Access
    url = f"https://graph.facebook.com/v17.0/me/accounts"
    params = {
        "access_token": user_access_token,
        "fields": "instagram_business_account",
    }

    response = requests.get(url, params=params)

    print(response.headers)
    print(response)

    exit()

    data = response.json()

    # Extract the Instagram Business Account ID from the response
    instagram_account_id = data['data'][0]['instagram_business_account']['id']

    # Step 4: Obtain Instagram User Token
    url = f"https://graph.facebook.com/v17.0/{instagram_account_id}"
    params = {
        "fields": "access_token",
        "access_token": user_access_token,
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Extract the Instagram User Token from the response
    instagram_user_token = data['access_token']

    return instagram_user_token

def post_content_on_instagram(instagram_user_token):
    # Step 5: Post content on Instagram
    # Use the Instagram User Token to post content on Instagram
    # Implement your posting logic here
    pass

def main():
    # insta_image_url = row[image_column]  # Replace 'image_column' with the column name that contains the image URL
    # insta_caption = row[text]  # Replace 'text' with the column name that contains the caption

    #print(instagram_user_access_token)

    instagram_user_token = get_instagram_user_token(instagram_user_access_token)

    post_content_on_instagram(instagram_user_token)

    print(instagram_user_token)
    


if __name__ == "__main__":
    # Check if the config table exists
    check_config_table(config_table)
    
    # Retrieve config values and update the local scope
    config_values = get_config_values(config_table)
    locals().update(config_values)

    # Call the main function
    main()
