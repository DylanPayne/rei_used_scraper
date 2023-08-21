import os, argparse, logging, time, random, json
from datetime import datetime, timezone
from utils.db_utils import DatabaseInserter, table_schema_rei_sweep
from utils.scrape_utils import rei_sweep_filter_conditions, fetch_rei_sweep_api
from rei.rei_parser import parse_rei_sweep_page, parse_rei_sweep_all
from utils.log_config import log_config

def main(suffix=None):
    # Log the start time
    start_time = time.time()
    run_id = int(time.time() * 1000)
    logger = log_config("scrape_rei_all.log")
    logger.info(f"\nScript started: {run_id}")
    
    # Create postgresql tables via table schemas
    try:
        with DatabaseInserter() as conn:
            for table_name, schema in table_schema_rei_sweep.items():
                if suffix is None:
                    conn.create_table(table_name, schema) # create tables
                else:
                    conn.create_table(f'{table_name}_{suffix}', schema) # create tables
    except Exception as e:
        logger.error(f"Error creating rei_sweep tables: {e}")
        
    breakpoint()
            
    # Determine the output table names based on optional suffix input
    items_table_name = f'rei_sweep_all_{suffix}' if suffix is not None else 'rei_sweep_all'
    page_table_name = f'rei_sweep_page_{suffix}' if suffix is not None else 'rei_sweep_page'

    item_cap = 100 # set to None for unpage_limited. Per filter
    page_limit = 100
    
    for filter in rei_sweep_filter_conditions:
        offset = 0
        item_count = None
        filter_json = json.loads(filter)  # Index JSON string and convert to dictionary        
        
        while item_count is None or offset < (item_cap or item_count):
            page_n = 1 + int(offset/page_limit) # Calculate page_n to increment by 1 from 1
            json_data, dt = fetch_rei_sweep_api(logger, offset, page_limit, filter_json)
            df_page, condition = parse_rei_sweep_page(json_data, page_n, page_limit, filter, logger)
            df_items = parse_rei_sweep_all(json_data, page_n, logger)
            
            helper_columns = {'run_id': run_id, 'dt': dt, 'page_n':page_n, 'condition': condition}

            try:
                with DatabaseInserter() as db_conn: # context manager closes connetion regardless of errors
                    db_conn.insert_to_sql(df_items, items_table_name, helper_columns, logger)
                    db_conn.insert_to_sql(df_page, page_table_name, helper_columns, logger)
            except Exception as e:
                logger.error(f"Error inserting data into database {str(e)}")
            
            offset += page_limit # increment to next page
            item_count = df_page['count'].item() # Assign item_count so it knows when to stop paginating
            time.sleep(random.uniform(2,6)) # wait between 1-5 seconds
    
    # Calculate and log the time elapsed
    elapsed_time = round((time.time() - start_time) / 60, 1)
    logger.info(f"Script completed. Time elapsed: {elapsed_time} minutes.")
    
# argparse allows you to pass in suffix: python scrape_rei_all.py --suffix=test
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and save REI data")
    parser.add_argument("--suffix", help="Optional suffix for the table name")
    args = parser.parse_args()

    main(args.suffix)