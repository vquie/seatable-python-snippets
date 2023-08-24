__author__ = "Vitali Quiering"
__version__ = "1.0.0"
import hashlib
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from seatable_api import Base, context
from html.parser import HTMLParser
import requests

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.text = ''
        self.recording = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.recording = 1

    def handle_endtag(self, tag):
        if tag == 'p':
            self.recording = 0

    def handle_data(self, data):
        if self.recording:
            self.text += data

def fetch_and_parse_data():
    server_url = context.server_url
    api_token = context.api_token
    base = Base(api_token, server_url)
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        base.auth()
    except Exception as e:
        print(f"Authentication failed with error: {e}")
        exit(1)

    sites_table = "Sites"
    sites_table_view = "Crawl"
    content_table = "Content"
    link_column_key = "Site"

    try:
        sites_rows = base.list_rows(sites_table, view_name=sites_table_view)
        link_id = base.get_column_link_id(content_table, link_column_key)
    except Exception as e:
        print(f"Failed to get rows or link id with error: {e}")
        exit(1)

    for row in sites_rows:
        url = row['URL']
        text = '' 

        if row['Type'] == 'static':
        
            try:
                response = requests.get(url, headers=headers)
                data = response.text
    
                parser = MyHTMLParser() 
                parser.feed(data)
                text = parser.text
    
                shahash = hashlib.sha256(data.encode('utf-8')).hexdigest()
    
            except Exception as e:
                print(f"Failed to open URL {url} with error: {e}")
                continue
            
        elif row['Type'] == 'rss':
            try:
                response = requests.get(url, headers=headers)
                data = response.text
                tree = ET.ElementTree(ET.fromstring(data))
                root = tree.getroot()
    
                message = ''
                for item in root.iter('item'):
                    title = item.find('title').text
                    description = item.find('description').text
    
                    message += title + description
                
                text = message
    
                shahash = hashlib.sha256(message.encode()).hexdigest()
    
            except Exception as e:
                print(f"Failed to open URL {url} with error: {e}")
                continue
            
        existing_hash = row.get('Hash', '')
    
        if shahash != existing_hash:
            try:
                row_data = {'Hash': shahash, 'Content': text}
                update_result = base.update_row(sites_table, row['_id'], row_data)
    
                if update_result:
                    print(f"Successfully updated hash and content for URL : {url}")
                    new_row = base.append_row(content_table, {'Content': text})
                    base.add_link(link_id, content_table, sites_table, new_row['_id'], row['_id'])
                else:
                    print(f"Failed to update hash and content for URL : {url}")
            except Exception as e:
                print(f"Updating row/repository failed with error: {e}")
        else:
            print("nothing to do")

if __name__ == "__main__":
    fetch_and_parse_data()
