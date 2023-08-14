import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd

def parse_rei_all(driver):
    # Open the REI Used Shop website
    driver.get("https://www.rei.com/used/shop/all")
    
    xpath_selector = "//*[@id='REI']/main/div/section/article/div[2]/ol/li[*]/a"
    
    # Use WebDriverWait to wait for elements to be present
    wait = WebDriverWait(driver, 10)
    elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_selector)))
    
    # Create an empty DataFrame
    df = pd.DataFrame(columns=['item_url', 'item_name', 'price_new', 'brand', 'price'])
    
    # Iterate through elements and extract required information
    for element in elements:
        try:
            item_url = element.get_attribute('href')
        except:
            item_url = None
        try:
            item_name = element.find_element(By.XPATH, './footer/h4/span[2]').text
        except:
            item_name = None        
        try:
            price_new = element.find_element(By.XPATH, './footer/div[1]/del/span[1]').text
        except:
            price_new = None        
        try:
            brand = element.find_element(By.XPATH, './footer/h4/span[1]').text
        except:
            brand = None        
        try:
            price = element.find_element(By.XPATH, './footer/div[1]/div/span[1]').text
        except:
            price = None
        
        new_row = pd.DataFrame({
            'item_url': [item_url],
            'item_name': [item_name],
            'price_new': [price_new],
            'brand': [brand],
            'price': [price],
        })
        
        # Append to DataFrame
        df = pd.concat([df, new_row], ignore_index=True)
    
    return df