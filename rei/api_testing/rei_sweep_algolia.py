import os
import requests
import json
import uuid

# Desktop API request, ex-cookies, randomly generated userToken uuid works
# Response is more powerful than one GraphQL one currently implemented - gives item_count, sku urls, product category info, etc
# But filtering / pagination is less obvious

#userToken = '21e69a44-bdf5-4f09-9ff1-f6989c88cd35'
# random = b05d1881-71c2-402a-8646-2a87036a6e4b
userToken = str(uuid.uuid4())
print("Generated user token:", userToken)

url = 'https://t5qjjs38p2-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.18.0)%3B%20Browser%3B%20JS%20Helper%20(3.13.3)%3B%20react%20(18.2.0)%3B%20react-instantsearch%20(6.40.1)'

breakpoint()

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://www.rei.com',
    'Referer': 'https://www.rei.com/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'content-type': 'application/json',
    'x-algolia-api-key': '3fac962f25c999c5ebea72ae3b602fb5',
    'x-algolia-application-id': 'T5QJJS38P2'
}

payload = {
    "requests": [
        {
            "indexName": "production-rei-stack-parent_sku_color",
            "params": f"clickAnalytics=true&facets=[]&filters=availability:true AND stack_version=3 AND warehouse_code:\"Valley-240\"&highlightPostTag=</ais-highlight-0000000000>&highlightPreTag=<ais-highlight-0000000000>&query=&tagFilters=&userToken={userToken}"
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)
response_json = response.json()

# Write JSON response to file named after this script
script_name = os.path.basename(__file__)
filename = f'{script_name}.json'
with open(filename, 'w') as file:
    json.dump(response_json, file, indent=4)
    
print(len(response_json['results']['hits']))

breakpoint()
