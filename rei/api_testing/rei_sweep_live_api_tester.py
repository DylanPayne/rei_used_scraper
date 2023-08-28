import os
import requests
import json

## Current API approach

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
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
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
        "filters": [], # i.e., [{tag: "condition", name: "Excellent condition"}, {tag: "gender", name: "Women's"}]
        "offset": 60,
        "limit": 30,
        "sort": "",
        "metadata": {}
    }
}



response = requests.post(url, json=data, headers=headers)
response_json = response.json()


# Write JSON response to file named after this script
script_name = os.path.basename(__file__)
filename = f'{script_name}.json'
with open(filename, 'w') as file:
    json.dump(response_json, file, indent=4)

breakpoint()

print(len(response_json['results']['hits']))

# Process the response as needed
print(response_json)

