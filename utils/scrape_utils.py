import os, logging, time
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.chrome.options import Options
import requests
import json

logging.basicConfig(level=logging.INFO, format='%(message)s')

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
#[{tag: "condition", name: "Excellent condition"}, {tag: "gender", name: "Women's"}]
# def rei_splitter(categories=('condition','gender')):
    
    
#     category_dict = [
#         {"condition":["Excellent condition", "Lightly worn", "Moderately worn", "Well worn"]},
#         {"gender"}: ["Women's", "Men's", "Unisex", "Kids"],
#         #{"size"}: [] size may avoid the need to scrape individual listings, other than category data. Maybe I scrape the size options, partition by size and condition,
#     ]
    
rei_all_api_filters = [
    '{"tag": "condition", "name": "Excellent condition"}',
    '{"tag": "condition", "name": "Lightly worn"}',
    '{"tag": "condition", "name": "Moderately worn"}',
    '{"tag": "condition", "name": "Well worn"}',
]

def fetch_rei_all_api(logger, offset=0, limit=100, filter_json=None):
    try:
        filter_json = filter_json if filter_json is not None else [] # Set filters to an empty list if None
        # breakpoint()
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
                "limit": limit, # ie., 30
                "sort": "",
                "metadata": {}
            }
        }
        response = requests.post(url, json=data, headers=headers)
        response_json = response.json()
        request_datetime = datetime.utcnow().isoformat()
        return response_json, request_datetime
    except Exception as e:
        logger.error(f"Failed to fetch_rei_all_api. {filter_json} offset: {offset} limit: {limit}. Error {str(e)}")
        return None, request_datetime

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    user_agent_str = random.choice(user_agents)
    
    chrome_options.add_argument(f"user-agent={user_agent_str}")
    driver = webdriver.Chrome(options=chrome_options)
    logging.info(f"UserAgent: {user_agent_str}")
    return driver