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

chatgpt_role_column = "AI Role"
chatgpt_vision_labels_column = "Google Vision API Labels"
chatgpt_additional_notes_column = "ChatGPT Additional Notes"
chatgpt_output_column = "ChatGPT Generated Description"

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

import requests

def call_chatgpt(chatgpt_role, chatgpt_vision_labels, chatgpt_additional_notes):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "messages": [
            {"role": "system", "content": chatgpt_role},
            {"role": "user", "content": f"Please mind these notes, refine and improve them for your task: {chatgpt_additional_notes}\n"}, 
            {"role": "user", "content": f"Google Vision Labels: {chatgpt_vision_labels}\n"},
        ],
        "model": "gpt-3.5-turbo",
        "max_tokens": 1000,
        "temperature": 0.9,
        "n": 1
    }
    response = requests.post(url, headers=headers, json=data)
    generated_text = response.json()["choices"][0]["message"]["content"]
    return generated_text

def main():

    chatgpt_role = row[chatgpt_role_column]

    chatgpt_vision_labels = row[chatgpt_vision_labels_column]
    if chatgpt_additional_notes_column in row:
        chatgpt_additional_notes = row[chatgpt_additional_notes_column]
    else:
        chatgpt_additional_notes = ""  # Or you can use an empty list [], if you want an empty array

    generated_text = call_chatgpt(chatgpt_role, chatgpt_vision_labels, chatgpt_additional_notes)
    
    row_data = {
        chatgpt_output_column: generated_text
    }

    base.update_row(table_name, row["_id"], row_data)


if __name__ == "__main__":
    main()

exit()
