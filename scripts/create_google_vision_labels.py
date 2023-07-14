"""
This script is designed to interact with the SeaTable API and perform operations related to Google Vision API labels.
It requires the `seatable-api` package to be installed.
"""

__author__ = "Vitali Quiering"
__version__ = "1.0.2"

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

def process_image_labels():
    """
    Processes the labels of an image using the Google Vision API.

    This function retrieves the image URL from the current row in the SeaTable table,
    sends a request to the Google Vision API to obtain labels for the image,
    and updates the corresponding row in the SeaTable table with the obtained labels.

    Args:
        None

    Returns:
        None
    """
    # Read configuration from the "_settings" table
    config_row = base.get_row(config_table, table_name=table_name)
    if not config_row:
        raise ValueError(f"Configuration row for table '{table_name}' not found.")

    # Get the image URL from the current row
    image_url = row[image_column]

    # Encode the image URL as Base64 for the Google Vision API request
    encoded_image_url = base64.b64encode(image_url.encode()).decode()

    # Prepare the request payload for the Google Vision API
    payload = {
        "requests": [
            {
                "image": {"source": {"imageUri": encoded_image_url}},
                "features": [{"type": "LABEL_DETECTION", "maxResults": 10}],
            }
        ]
    }

    # Send the request to the Google Vision API
    response = requests.post(
        "https://vision.googleapis.com/v1/images:annotate",
        params={"key": config_row["Google Vision API Key"]},
        json=payload,
    )

    # Parse the response and extract the labels
    if response.status_code == 200:
        labels = []
        response_json = json.loads(response.text)
        if "responses" in response_json and len(response_json["responses"]) > 0:
            label_annotations = response_json["responses"][0].get("labelAnnotations", [])
            labels = [label["description"] for label in label_annotations]

        # Update the row in the SeaTable table with the labels
        update_data = {google_vision_label_column: labels}
        base.update_row(config_table, config_row["_id"], update_data)
    else:
        raise ValueError(f"Failed to process image labels. Error: {response.text}")

def get_config_values(config_table):
    """
    Retrieve the values in a config table.

    This function retrieves all rows from the specified config table in SeaTable
    and creates a dictionary that maps config keys to their corresponding values.

    Args:
        config_table (str): Name of the config table.

    Returns:
        dict: A dictionary mapping config keys to their values.
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

    This function checks if the specified config table exists in the SeaTable database.
    If the table does not exist, the function raises a SystemExit with an error message.

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

def download_image(image_url):
    """
    Download an image from the specified URL and return its Base64-encoded content.

    This function downloads an image from the given URL and saves it to the local file system.
    It then reads the content of the image file, encodes it as Base64, and returns the Base64-encoded content.

    Args:
        image_url (str): URL of the image to download.

    Returns:
        str: Base64-encoded content of the downloaded image.
    """
    # Extract the filename from the image URL
    image_path = os.path.basename(urllib.parse.urlparse(image_url).path)

    # Download the image file
    base.download_file(image_url, image_path)

    # Read the image file
    with open(image_path, "rb") as image_file:
        image_content = image_file.read()

    # Encode the image content as Base64
    encoded_image_content = base64.b64encode(image_content).decode("utf-8")

    return encoded_image_content

def get_images():
    """
    Get the Base64-encoded content of images from the 'Image' column in the current row.

    This function retrieves the URLs of images from the 'Image' column in the current row.
    It then calls the 'download_image' function to download each image and get its Base64-encoded content.
    The Base64-encoded contents of the images are stored in a list and returned.

    Returns:
        list: A list of Base64-encoded contents of the downloaded images.
    """
    encoded_images = []
    for image_url in row[image_column]:
        encoded_image = download_image(image_url)
        encoded_images.append(encoded_image)

    return encoded_images

def google_vision_process(encoded_image):
    """
    Process the labels of an image using the Google Vision API.

    This function sends a request to the Google Vision API to obtain labels for the specified image,
    based on its Base64-encoded content.
    It returns a list of tuples, where each tuple contains the label description and the label score.

    Args:
        encoded_image (str): Base64-encoded content of the image.

    Returns:
        list: A list of tuples containing label descriptions and scores.
    """
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
    """
    Main function for processing image labels using the Google Vision API.

    This function is the entry point of the script.
    It retrieves the Base64-encoded contents of images from the 'Image' column in the current row,
    processes the images using the Google Vision API to obtain labels,
    and updates the 'Google Vision API Labels' column in the current row with the obtained labels.

    Returns:
        None
    """
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
    # Check if the config table exists
    check_config_table(config_table)

    # Retrieve the config values
    config_values = get_config_values(config_table)
    locals().update(config_values)

    # Set up Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_vision_application_credentials

    # Execute the main function
    main()

exit()
