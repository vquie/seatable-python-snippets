"""
__author__ = "Vitali Quiering"
__version__ = "1.0.0"
"""

import requests
from seatable_api import Base, context

# Define the name of the config table
config_table = "_settings"
server_url = context.server_url
api_token = context.api_token

# Create the Base object and authenticate
base = Base(api_token, server_url)
base.auth()

# Get the context
table_name = "Kassenbuch"
gpt_rows = base.list_rows(table_name, view_name="AI Analysis")

def get_config_values(config_table):
    """
    Retrieve the values from the config table and return them as a dictionary.
    
    :param config_table: The name of the config table.
    :return: A dictionary containing the config values.
    """
    rows = base.list_rows(config_table)
    config_dict = {}
    for row in rows:
        if "value" in row and row["value"]:
            config_dict[row["Name"]] = row["value"]
    return config_dict

def check_config_table(config_table):
    """
    Check if the config table exists in the base's metadata.
    Exit the script if the config table is not found.
    
    :param config_table: The name of the config table.
    """
    base_metadata = base.get_metadata()
    config_table_found = any(table["name"] == config_table for table in base_metadata["tables"])
    if not config_table_found:
        raise SystemExit("Config table not found!")

def call_chatgpt(openai_api_key):
    """
    Call the OpenAI GPT-3 API to generate a response based on the given prompt.
    
    :param openai_api_key: The API key for accessing the OpenAI GPT-3 API.
    :return: The generated text response.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "messages": [
            {"role": "system", "content": f"{chatgpt_prompt}"},
            {"role": "user", "content": ""}
        ],
        "model": "gpt-3.5-turbo-16k",
        "max_tokens": 1000,
        "temperature": 0.1,
        "n": 1
    }
    for row in gpt_rows:
        role_obj = {
            "role": "user",
            "content": str(row)
        }
        data["messages"].append(role_obj)
    response = requests.post(url, headers=headers, json=data)
    generated_text = response.json()["choices"][0]["message"]["content"]
    return generated_text

def main():
    """
    The main function that executes the script.
    """
    # Generate the text using the call_chatgpt function
    generated_text = call_chatgpt(openai_api_key)

    row_data = {
        "Analysis": generated_text
    }

    # Update the row in the table with the generated text
    base.append_row("AI Analysis", row_data)

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
