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

def main():
    insta_image_url = row[image_column]  # Replace 'image_column' with the column name that contains the image URL
    insta_caption = row[text]  # Replace 'text' with the column name that contains the caption
    
    access_token = 'your_access_token'
    
    session = requests.Session()
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Referer': 'https://www.instagram.com/',
        'Authorization': f'Bearer {access_token}'
    })
    
    session.get('https://www.instagram.com/')
    
    upload_url = 'https://graph.instagram.com/me/media'
    
    image_data = session.get(insta_image_url).content
    
    files = {
        'media': ('image.jpg', image_data)
    }
    
    upload_response = session.post(upload_url, files=files)
    
    if upload_response.status_code == 200:
        media_id = upload_response.json().get('id')
        caption_url = f'https://graph.instagram.com/{media_id}'
        
        caption_data = {
            'caption': insta_caption
        }
        
        caption_response = session.post(caption_url, data=caption_data)
        
        if caption_response.status_code == 200:
            print('Image and caption posted successfully!')
        else:
            print('Failed to add caption to the image.')
    else:
        print('Failed to upload image.')

if __name__ == "__main__":
    # Check if the config table exists
    check_config_table(config_table)
    
    # Retrieve config values and update the local scope
    config_values = get_config_values(config_table)
    locals().update(config_values)

    # Call the main function
    main()

    # Terminate the script execution
    exit()
