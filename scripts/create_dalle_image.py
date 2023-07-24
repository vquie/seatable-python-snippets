"""
This script is used to configure and interact with Seatable API for ChatGPT.
It requires the `seatable-api` package to be installed.
"""

__author__ = "Vitali Quiering"
__version__ = "1.0.0-alpha"

import os
import requests
import base64
import json
import urllib.parse
import random
import string
from seatable_api import Base, context

# Configuration variables
config_table = "_settings"
dalle_prompt_column = "Image Prompt"
dalle_output_column = "Image"

# Retrieve server URL and API token from the context
server_url = context.server_url
api_token = context.api_token

# Initialize the Seatable API client
base = Base(api_token, server_url)
base.auth()

# Retrieve the current row and table name from the context
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

def get_dalle_url(dalle_prompt):
    """
    Call the DALL-E API to generate an image based on the provided input.

    Args:
        dalle_prompt (str): The prompt for the DALL-E image generation.

    Returns:
        str: The URL of the generated image.
    """
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "prompt": f"{dalle_prompt}",
        "size": "1024x1024",
        "n": 1
    }
    response = requests.post(url, headers=headers, json=data)
    generated_image_url = response.json()["data"][0]["url"]
    return generated_image_url


def main():
    """
    The main function that executes the ChatGPT generation process.

    Returns:
        None
    """

    # Retrieve the role from the specified column in the current row
    dalle_prompt = row[dalle_prompt_column]

    # Generate the image using the call_dalle function
    generated_image_url = get_dalle_url(dalle_prompt)

    generated_image = requests.get(generated_image_url)

    # Generate a random 8-character string
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Add file suffix
    random_str += ".png"

    uploaded_url = base.upload_bytes_file(content=generated_image.content, name=random_str, file_type='image', replace=True)

    img_url = uploaded_url.get('url')

    row[dalle_output_column] = [img_url]

    base.update_row(table_name, row['_id'], row)


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
