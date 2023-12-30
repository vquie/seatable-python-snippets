from seatable_api import Base, context

SERVER_URL = context.server_url
API_TOKEN = context.api_token

base = Base(API_TOKEN, SERVER_URL)
base.auth()

row = context.current_row
table_name = context.current_table

column_names = list(row.keys())
unique_identifier = 'Datum'
all_rows = base.list_rows(table_name)
rows_to_merge = [r for r in all_rows if r.get(unique_identifier) == row.get(unique_identifier)]
updated_data = {}

meta = base.get_metadata()
table_meta = next((table for table in meta.get('tables', []) if table.get('name') == table_name), None)
column_metas = {column['name']: column for column in table_meta['columns']}

# Defining merge function
def merge(column_name, column_value):
    if column_name in updated_data:
        updated_data[column_name].extend(column_value)
    else:
        updated_data[column_name] = column_value if isinstance(column_value, list) else [column_value]

def merge_links(column_name, column_value):
    if column_name in updated_data:
        for row_id in column_value:
            try:
                # Get the linked records for the current row_id
                other_row_ids = base.get_linked_records(table_name, column_name, [{'row_id': row_id}])
                for other_row_id in other_row_ids:
                    # Check if the other_row_id is already in the updated_data for the current column_name
                    if other_row_id not in updated_data[column_name]:
                        # If not, add the link
                        base.add_link(column_name, table_name, other_table_name, row_id, other_row_id['row_id'])
                        updated_data[column_name].append(other_row_id)
            except Exception as e:
                print(f"Error while getting linked records for row_id {row_id}: {e}")
    else:
        updated_data[column_name] = []
        for row_id in column_value:
            try:
                other_row_ids = base.get_linked_records(table_name, column_name, [{'row_id': row_id}])
                for other_row_id in other_row_ids:
                    base.add_link(column_name, table_name, other_table_name, row_id, other_row_id['row_id'])
                    updated_data[column_name].append(other_row_id)
            except Exception as e:
                print(f"Error while getting linked records for row_id {row_id}: {e}")

# Defining append function
def append(column_name, column_value):
    updated_data[column_name] = (str(updated_data.get(column_name, '')) + '\n' + str(column_value)).strip()

# Defining overwrite function
def overwrite(column_name, column_value):
    if column_name in max(rows_to_merge, key=lambda r: r['_mtime']):
        updated_data[column_name] = max(rows_to_merge, key=lambda r: r['_mtime'])[column_name]

for row_to_merge in rows_to_merge:
    for column_name in column_names:
        if column_name in row_to_merge:
            if column_name == unique_identifier:
                updated_data[column_name] = row[unique_identifier]
            elif column_name not in ['_id', '_mtime', '_ctime']:
                column_value = row_to_merge.get(column_name, '')
                column_type = column_metas[column_name]['type']
                if column_type == 'number':
                    print("number")
                    overwrite(column_name, column_value)
                elif column_type == 'date':
                    print("date")
                elif column_type == 'button':
                    print("button")
                elif column_type == 'formula':
                    print("formula")
                elif column_type == 'single-select':
                    print("single-select")
                elif column_type in ['text', 'long-text']:
                    print("text")
                    append(column_name, column_value)
                elif column_type == 'rate':
                    print("rate")
                elif column_type == 'link':
                    print("link")
                    merge_links(column_name, column_value)
                else:
                    overwrite(column_name, column_value)

base.update_row(table_name, row['_id'], updated_data)

for row_to_merge in rows_to_merge:
    if row_to_merge['_id'] != row['_id']:
        base.delete_row(table_name, row_to_merge['_id'])