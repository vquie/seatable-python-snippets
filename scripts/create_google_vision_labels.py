"""
"""
__author__ = "Vitali Quiering"
__version__ = "1.0.0"

import os
import requests
import base64
import json
import urllib.parse
from seatable_api import Base, context

# config
config_table = "_settings"
image_column = "Image"
google_vision_label_column = "Google Vision API Labels"

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

check_config_table(config_table)
config_values = get_config_values(config_table)
locals().update(config_values)

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_vision_application_credentials

def download_image(image_url):
    image_path = os.path.basename(urllib.parse.urlparse(image_url).path)
    base.download_file(image_url, image_path)

    # Read the image file
    with open(image_path, "rb") as image_file:
        image_content = image_file.read()

    return base64.b64encode(image_content).decode("utf-8")

def get_images():
    encoded_images = []
    for image_url in row[image_column]:
        encoded_image = download_image(image_url)
        encoded_images.append(encoded_image)
        
    return encoded_images

def google_vision_process(encoded_image):

    google_vision_payload = {
        "requests": [
            {
                "image": {"content": encoded_image},
                "features": [{"type": "LABEL_DETECTION"}],
            }
        ]
    }

    # Make the API request
    api_url = "https://vision.googleapis.com/v1/images:annotate?key=" + google_vision_api_key
    response = requests.post(api_url, json=google_vision_payload)

    # Parse the response
    response_json = response.json()

    # Extract and print the labels
    if "responses" in response_json and len(response_json["responses"]) > 0:
        labels = response_json["responses"][0].get("labelAnnotations", [])
        label_results = []
        for label in labels:
            label_description = label["description"]
            label_score = label["score"]
            label_results.append((label_description, label_score))
        return label_results
    else:
        print("Label detection failed.")
        exit()

def main():
    encoded_images = get_images()

    google_vision_labels = []

    for counter, encoded_image in enumerate(encoded_images, 1):
        print(f"Processing image {counter}/{len(encoded_images)}...")
        google_vision_labels.extend(google_vision_process(encoded_image))


    row_data = {
        google_vision_label_column: str(google_vision_labels)
    }

    base.update_row(table_name, row["_id"], row_data)


if __name__ == "__main__":
    main()

exit()