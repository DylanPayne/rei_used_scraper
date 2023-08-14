import time, logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def parse_rei_all(driver, run_id):
    # Define base XPath for the items (pre-a tag, which contains the items)
    base_xpath = "//*[@id='REI']/main/div/section/article/div[2]/ol/li"
    
    # Open the REI Used Shop website
    driver.get("https://www.rei.com/used/shop/all")
    
    # Use WebDriverWait to wait for elements to be present
    wait = WebDriverWait(driver, 10)
    
    # Find the last item (a-tag), by appending '[last()]/a'
    last_item_link_xpath = f"{base_xpath}[last()]/a"
    wait.until(EC.visibility_of_all_elements_located((By.XPATH, last_item_link_xpath)))
    
    # breakpoint()
    
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