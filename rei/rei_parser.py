import time, logging, json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
from collections import defaultdict


def parse_rei_scrape_sku(json_data, logger):
    return None

def parse_rei_scrape_variants(json_data, logger):
    return None

def parse_rei_sweep_all(json_data, page_n, logger): ## 
    # Parse items details ('page_limit' rows per API page)
    try:
        items_list = json_data['data']['partner']['shop']['browse']['items']
        items_data = []
        
        for item in items_list:
            try:
                # Check if 'parent SKU' exists in item, if not set it to None
                parent_sku = item['parentSKU'] if 'parentSKU' in item and str(item['parentSKU']).isnumeric() else None
                if parent_sku is None:
                    logger.warning(f"Invalid or missing parent SKU. Setting it to NULL.")
                price = item['price']/100 if item['price'] is not None else None # To handle NULL prices
                price_orig = item['originalPrice']/100 if item['originalPrice'] is not None else None
                size_range = item['availableSizes']
                price_range = [price/100 for price in item['priceRange']] if item['priceRange'] is not None else None # To handle NULL price_range
                
                item_data = {
                    'title': item['title'],
                    'brand': item['brand'],
                    'path': item['pdpLink']['path'],
                    'parent_sku': parent_sku,
                    'price': price,
                    'price_orig': price_orig,
                    'price_range': price_range,
                    'size_range': size_range,
                    'color': item['color'],
                }
                items_data.append(item_data)
            except Exception as e:
                logger.warning(f"Failed to parse an item. Error: {str(e)}")

        df_items = pd.DataFrame(items_data)
        logger.info(f"Parsed item-level data for page {page_n}")
        return df_items
    except Exception as e:
        logger.info(f"Failed to parse item-level data for page {page_n}. Error: {str(e)}")
        return None
    
def parse_rei_sweep_page(json_data, page_n, page_limit, filters, logger): ##
    # Parse page-level data for rei_sweep
    try:
        count = json_data['data']['partner']['shop']['browse']['count']
        parsed_filter = json.loads(filters)
        condition = parsed_filter['name']

        df_page = pd.DataFrame({
            'page_limit':[page_limit],
            'count': [count],
        })
        logger.info(f"Parsed page data for {filters} n={page_n})")
        return df_page, condition
    except Exception as e:
        logger.error(f"Failed to parse page data for {filters} n={page_n}. Error {str(e)}")
        return None

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