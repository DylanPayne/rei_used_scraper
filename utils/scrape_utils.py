#!/usr/bin/env python3
import os, logging, time, json, re
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.chrome.options import Options


logging.basicConfig(level=logging.INFO, format='%(message)s')

# Desktop user agents only (mobile commented out)
user_agents = [
    # Google Chrome (Windows 10)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    # Mozilla Firefox (Windows 10)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    # Apple Safari (macOS)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    # Apple Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    # Microsoft Edge (Windows 10)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    # Google Chrome (Android)
    # "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    # Apple Safari (iOS)
    # "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1"  
]
    
rei_sweep_filter_conditions = [
    '{"tag": "condition", "name": "Excellent condition"}',
    '{"tag": "condition", "name": "Lightly worn"}',
    '{"tag": "condition", "name": "Moderately worn"}',
    '{"tag": "condition", "name": "Well worn"}',
]

def simple_logger(msg):
    print(f"[LOG]: {msg}")

def fetch_rei_scrape_api(
        logger=simple_logger,
        base_url='https://www.rei.com/used/p/rei-co-op-flash-hiking-boots-womens/189065?color=Dusty%20Olive%2FGray',
        aqi='3ac82c162d900347ad193501b65c641a',
        user_agents=["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"]
):
    request_datetime = datetime.utcnow().isoformat()
    url = f"{base_url}&aqi={aqi}"
    try:
        user_agent_str = random.choice(user_agents)

        headers = {
            'authority': 'www.rei.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': user_agent_str,
        }

        response = requests.post(url, headers=headers)
        response_content = response.content.decode('utf-8')
        return response_content, request_datetime
    except Exception as e:
        logger(f"Failed to fetch {url} via {user_agent_str}. Error {str(e)}")
        return None, request_datetime

def fetch_rei_sweep_api(logger, offset=0, page_limit=100, filter_json=None):
    try:
        filter_json = filter_json if filter_json is not None else [] # Set filters to an empty list if None
        user_agent_str = random.choice(user_agents)
        
        url = 'https://reware-api-production.trovesite.com/v4/graphql?q=query-initShop'

        headers = {
            'authority': 'reware-api-production.trovesite.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://www.rei.com',
            'referer': 'https://www.rei.com/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': user_agent_str, # i.e., 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-browser-uuid': 'aeceexit1ed8-cd82-4780-bc23-5fdc92801764',
            'x-customer-uuid': '21e69a44-bdf5-4f09-9ff1-f6989c88cd35',
            'x-kameleoon-visitor-code': '3mwd3nhi8zgf8k98',
            'x-session-uuid': 'db4f5e20-fbcc-4aa6-b2e2-6c75ab84aa69',
            'x-trove-app-name': 'storefront:rei',
            'x-trove-country-code': 'US',
            'x-trove-order-uuid': 'null',
            'x-ycustomer-uuid': 'null',
            'x-yerdle-app-name': 'storefront:rei',
        }

        data = {
            "query": """query initShop(
                $partner: String!
                $slug: String!
                $filters: [FacetLimitPublic]
                $offset: Int
                $limit: Int
                $sort: String
                $source: String
                $metadata: ShopMetadataInputTypePublic
            ) {
                partner(uuid: $partner) {
                    shop(
                        slug: $slug
                        filters: $filters
                        metadata: $metadata
                    ) {
                        canonical(filters: $filters)
                        headline
                        subheadline
                        metaDescription
                        slug
                        title
                        facets(filters: $filters) {
                            tag
                            title
                            entries {
                                name
                                displayName
                                count
                            }
                            visibleLimit
                        }
                        browse(
                            filters: $filters
                            offset: $offset
                            limit: $limit
                            sort: $sort
                            source: $source
                        ) {
                            count
                            indexName
                            queryId
                            items {
                                availableSizes
                                availableSizeDisplays
                                brand
                                storefrontDepartment
                                brandDisplay
                                cmsData
                                color
                                displayColor
                                imageUrls
                                itemDetail {
                                    displayCondition
                                }
                                originalPrice
                                parentSKU
                                markdownReason
                                price
                                priceRange
                                title
                                stackId
                                displayTitle
                                objectType
                                pdpStyle
                                pdpLink {
                                    path
                                    url
                                }
                            }
                        }
                    }
                }
            }""",
            "variables": {
                "partner": "7d32ad83-330e-4ccc-ba03-3bb32ac113ae",
                "slug": "all",
                "filters": [filter_json], # [{tag: "condition", name: "Excellent condition"}, {tag: "gender", name: "Women's"}]
                "offset": offset, # i.e., 60
                "limit": page_limit, # ie., 30
                "sort": "",
                "metadata": {}
            }
        }
        response = requests.post(url, json=data, headers=headers)
        response_json = response.json()
        request_datetime = datetime.utcnow().isoformat()
        return response_json, request_datetime
    except Exception as e:
        logger.error(f"Failed to fetch_rei_sweep_api. {filter_json} offset: {offset} limit: {page_limit}. Error {str(e)}")
        request_datetime = datetime.utcnow().isoformat()
        return None, request_datetime

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    user_agent_str = random.choice(user_agents)
    
    chrome_options.add_argument(f"user-agent={user_agent_str}")
    driver = webdriver.Chrome(options=chrome_options)
    logging.info(f"UserAgent: {user_agent_str}")
    return driver

def split_content(content, split_by, index):
    split_data = content.split(split_by, 1) # Only split first instance
    if len(split_data) > index:
        return split_data[index]
    else:
        raise ValueError(f"Error splitting content, {split_by} not found.")

def extract_json_btw_strings(content, logger, start_str, end_str):
    try:
        trim_front = split_content(content, start_str, 1)
        trim_end = split_content(trim_front, end_str, 0)
        return json.loads(trim_end)
    except ValueError as ve:
        logger.error(ve)
        return None
    
def extract_item_level(item_json, logger):
    item_json["confNewPrice"]

# FOR TESTING
if __name__ == "__main__":
    response_content, request_datetime = fetch_rei_scrape_api()
    file_path = 'output.html'
    
    with open(file_path, "w") as file:
        file.write(response_content)
        
    full_json = extract_json_btw_strings(
        response_content,
        logger=simple_logger,
        start_str = '<script>window.__PRELOADED_STATE__ = ',
        end_str = '</script>')
    
    # Serialize the Python object back into a formatted JSON string
    str_full_json = json.dumps(full_json, indent=4)

    # Write the formatted JSON string to a file
    with open('output_full.json', 'w') as file:
        file.write(str_full_json)
        
    if "item" in full_json:
        item_json = full_json["item"]
        str_item_json = json.dumps(item_json, indent=4)
        with open('output_item.json', 'w') as file:
            file.write(str_item_json)
    else:
        print("The key 'item' does not exist in the JSON data.")
    
    # extract_item_level()
    
    # sku_n = extract_skus()

    breakpoint()
    
    # split_by_start = '<script>window.__PRELOADED_STATE__ = '
    # split_by_end = '</script>'
    
    # split_html = response_content.split(split_by_start, 1) # Only split at first instance
    # breakpoint()
    
    # if(len(split_html)) > 1:
    #     extracted_json = split_html[1]
    # else:
    #     print(f"Split string {split_by_start} not found in the response_content")
    #     print(response_content)
    
    # split_json = extracted_json.split(split_by_end, 1)
    # if(len(split_json)) > 1:
    #     clean_json = split_json[0]
    # else:
    #     print(f"Split string {split_by_end} not found in the extracted_json")
    #     print(extracted_json)
    # parsed_json = json.loads(clean_json)
    # return parsed_json