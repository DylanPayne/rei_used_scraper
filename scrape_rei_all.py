import os, argparse, logging, time, random
from datetime import datetime, timezone
from utils.db_utils import DatabaseInserter
from utils.scrape_utils import initialize_driver, fetch_rei_all_api
from rei.rei_parser import parse_rei_all, parse_rei_all_json
from utils.log_config import log_config

def main(suffix=None):
    # Log the start time
    start_time = time.time()
    run_id = int(time.time() * 1000)
    logger = log_config("scrape_rei_all.log")
    logger.info(f"\nScript started: {run_id}")
    
    # Determine the table name based on the suffix
    items_table_name = f'rei_item_all_{suffix}' if suffix else 'rei_item_all'
    page_table_name = f'rei_item_page_{suffix}' if suffix else 'rei_item_page'
    
    offset = 0
    limit = 100
    filters = None
    item_count = None
    item_cap = 400 # set to None for unlimited
    
    while item_count is None or offset < (item_cap or item_count):
        page_n = 1 + int(offset/limit)
        json_data, dt = fetch_rei_all_api()
        df_page, df_items = parse_rei_all_json(json_data, page_n, limit, filters, logger)

    # Open postgresql connection, insert rows, close
        db_conn = DatabaseInserter()
        db_conn.insert_rei_all(df_items, items_table_name, run_id, dt, logger)
        db_conn.insert_rei_all(df_page, page_table_name, run_id, dt, logger)
        db_conn.close()
        
        offset += limit # increment to next page
        item_count = df_page['count'].item() # Assign item_count so it knows when to stop paginating
        time.sleep(random.uniform(2,6)) # wait between 1-5 seconds
    
    # Calculate and log the time elapsed
    elapsed_time = round((time.time() - start_time) / 60, 1)
    logger.info(f"Script completed. Time elapsed: {elapsed_time} minutes.")

### OLD CODE for selenium-based extraction ##
# initialize selenium driver, extract data
# driver = initialize_driver()
# df = parse_rei_all(driver, run_id)

# argparse allows you to pass in suffix: python scrape_rei_all.py --suffix=test
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and save REI data")
    parser.add_argument("--suffix", help="Optional suffix for the table name", default=None)
    args = parser.parse_args()

    main(args.suffix)