import time, logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
from collections import defaultdict


def parse_rei_all_json(json_data, page_n, limit, filters, logger):
    # 1) Parse data into page_df (1 row per API page)
    count = json_data['data']['partner']['shop']['browse']['count']
    
    # 1)b Generate and populate filter columns
    # Define all possible filter tags
    all_tags = ["condition", "gender", "color", "size", "activity", "category", "department", "brand", "itemStorefrontPriceRange"]
    # Initialize a defaultdict to hold filter values as comma-separated lists
    filter_dict = defaultdict(list)
    # Iterate through the filters and append values to the corresponding keys
    if filters:
        for filter_item in filters:
            tag = filter_item.get('tag')
            name = filter_item.get('name')
            filter_dict[f'filter_{tag}'].append(name)
    # Create a dictionary with fixed keys, comma-join values, and set None if empty
    fixed_filter_dict = {f'filter_{tag}': ', '.join(filter_dict[f'filter_{tag}']) if filter_dict[f'filter_{tag}'] else None for tag in all_tags}

    df_page = pd.DataFrame({
        'page_n':[page_n],
        'limit':[limit],
        'count': [count],
        'filters':[filters],
        **fixed_filter_dict # Unpack the filter columns into the df
    })
    

    # 2) Parse items details ('limit' rows per API page)
    items_list = json_data['data']['partner']['shop']['browse']['items']
    items_data = []
    for item in items_list:
        item_data = {
            'page': page_n,
            'title': item['title'],
            'brand': item['brand'],
            'path': item['pdpLink']['path'],
            'parentSKU': item['parentSKU'],
            'price': item['price'],
            'originalPrice': item['originalPrice'],
            'priceRange': item['priceRange'],
            'availableSizes': item['availableSizes'],
            'color': item['color'],
        }
        items_data.append(item_data)

    df_items = pd.DataFrame(items_data)
    logger.info(f"Parsed page {page_n}.")
    return df_page, df_items

def request_handler(request):
    # Check if this is the request you're interested in
    if 'algolianet' in request['request']['url']:
        # Extract userToken or other data from the request
        user_token = request['request']['postData']['userToken']
        print(f"User Token: {user_token}")



####  LEGACY - selenium-based approach (much slower) #####
def parse_rei_all(driver, run_id):
    # Define base XPath for the items (pre-a tag, which contains the items)
    base_xpath = "//*[@id='REI']/main/div/section/article/div[2]/ol/li"
    
    # Open the REI Used Shop website
    driver.get("https://www.rei.com/used/shop/all")
    
    ###### CODE TO Extract userToken so we can use API for the actual scraping #####
    # global_variables = driver.execute_script("return Object.keys(window);")
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.requestWillBeSent", {"request": request_handler})
    #### END ######
    
    # Use WebDriverWait to wait for elements to be present
    wait = WebDriverWait(driver, 10)
    
    # Find the last item (a-tag), by appending '[last()]/a'
    last_item_link_xpath = f"{base_xpath}[last()]/a"
    wait.until(EC.visibility_of_all_elements_located((By.XPATH, last_item_link_xpath)))
    
    breakpoint()
    
    
    
    # Use base_xpath to locate all items and iterate over them
    elements = driver.find_elements(By.XPATH, f"{base_xpath}/a")
    
    # Create an empty DataFrame
    df = pd.DataFrame(columns=['run_id','item_url', 'item_name', 'price_new', 'brand', 'price'])
    
    # Iterate through elements and extract required information
    # Iterate through elements and extract required information
    for element in elements:
        try:
            item_url = element.get_attribute('href')
        except:
            item_url = None
            logging.info(f"XPath: {base_xpath}/a - Value: Unable to extract item_url")
            
        try:
            item_name = element.find_element(By.XPATH, './footer/h4/span[2]').text
        except:
            item_name = None
            logging.info(f"XPath: {base_xpath}/footer/h4/span[2] - Value: Unable to extract item_name")
            
        try:
            price_new = element.find_element(By.XPATH, './footer/div[1]/del/span[1]').text
        except:
            price_new = None
            logging.info(f"XPath: {base_xpath}/footer/div[1]/del/span[1] - Value: Unable to extract price_new")
            
        try:
            brand = element.find_element(By.XPATH, './footer/h4/span[1]').text
        except:
            brand = None
            logging.info(f"XPath: {base_xpath}/footer/h4/span[1] - Value: Unable to extract brand")
            
        try:
            price = element.find_element(By.XPATH, './footer/div[1]/div/span[1]').text
        except:
            price = None
            logging.info(f"XPath: {base_xpath}/footer/div[1]/div/span[1] - Value: Unable to extract price")
        
        new_row = pd.DataFrame({
            'run_id': [run_id],
            'item_url': [item_url],
            'item_name': [item_name],
            'price_new': [price_new],
            'brand': [brand],
            'price': [price],
        })
        
        # Append to DataFrame
        df = pd.concat([df, new_row], ignore_index=True)
    
    return df