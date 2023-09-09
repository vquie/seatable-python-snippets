__author__ = "Vitali Quiering"
__version__ = "1.1.0"

import requests
from seatable_api import Base, context

config_table = "_settings"
server_url = context.server_url
api_token = context.api_token

base = Base(api_token, server_url)
base.auth()

table_name = "Auswertung"
gpt_rows = base.list_rows(table_name, view_name="Stats AI")

def get_config_values(config_table):
    rows = base.list_rows(config_table)
    config_dict = {}
    for row in rows:
        if "value" in row and row["value"]:
            config_dict[row["Name"]] = row["value"]
    return config_dict

def check_config_table(config_table):
    base_metadata = base.get_metadata()
    config_table_found = any(table["name"] == config_table for table in base_metadata["tables"])
    if not config_table_found:
        raise SystemExit("Config table not found!")

def call_chatgpt(openai_api_key, chatgpt_prompt, gpt_rows):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "messages": [
            {"role": "system", "content": f"{chatgpt_prompt}"},
            {"role": "assistant", "content": "Ok"},
            {"role": "user", "content": f"{gpt_rows}"}
        ],
        "model": "gpt-4",
        "temperature": 0.3
    }

    print(gpt_rows)

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        generated_text = response.json()["choices"][0]["message"]["content"]
    except (requests.HTTPError, KeyError) as e:
        print(f"Error was caught: {e}")
        return None
    return generated_text

def main(openai_api_key, chatgpt_prompt, gpt_rows):
    generated_text = call_chatgpt(openai_api_key, chatgpt_prompt, gpt_rows)

    row_data = {
        "Analysis": generated_text
    }

    base.append_row("AI Analysis", row_data)

if __name__ == "__main__":
    check_config_table(config_table)
    
    config_values = get_config_values(config_table)
    openai_api_key = config_values.get('openai_api_key')
    chatgpt_prompt = config_values.get('chatgpt_prompt')

    main(openai_api_key, chatgpt_prompt, gpt_rows)