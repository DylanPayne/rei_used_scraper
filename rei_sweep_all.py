import os, argparse, logging, time, random, json
from datetime import datetime, timezone
from utils.db_utils import DatabaseInserter, table_schema_rei_sweep
from utils.scrape_utils import rei_sweep_filter_conditions, fetch_rei_sweep_api
from rei.rei_parser import parse_rei_sweep_page, parse_rei_sweep_all
from log.log_config import log_config

def main(prefix, page_cap):
    # Log the start time
    start_time = time.time()
    # Determine script_name, and strip off extension to determine run_name
    script_name = os.path.basename(os.path.abspath(__file__))
    run_name = os.path.splitext(script_name)[0]
    # Configure logging
    logger = log_config(f"{run_name}.log")
    logger.info(f"/n Starting {script_name}")
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR) ## To migrate into log_config.py
    # initialize run_id to handle errors within try block
    run_id = None
    
    # Create tables in postgresql, naming incorporates optional argparse prefix
    try:
        with DatabaseInserter() as db_conn:
            for table_name, schema in table_schema_rei_sweep.items():
                db_conn.create_table(f'{prefix}{table_name}', schema, logger) # create tables
            run_id = db_conn.start_run(run_name, prefix, logger) # start run by inserting row
            logger.info(f"\n {script_name} started run_id: {run_id}")
            
            # Determine output table names based on optional prefix input
            items_table_name = f'{prefix}rei_sweep_all'
            page_table_name = f'{prefix}rei_sweep_page'
    except Exception as e:
        logger.error(f"Error creating rei_sweep tables: {e}")

    page_limit = 100
    item_cap = None if page_cap is None else page_limit * page_cap
    
    for filter in rei_sweep_filter_conditions:
        offset = 0
        item_count = None
        filter_json = json.loads(filter)  # Index JSON string and convert to dictionary        
        
        while item_count is None or offset < (item_cap or item_count):
            page_n = 1 + int(offset/page_limit) # Calculate page_n to increment by 1 from 1
            json_data, dt = fetch_rei_sweep_api(logger, offset, page_limit, filter_json)
            df_page, condition = parse_rei_sweep_page(json_data, page_n, page_limit, filter, logger)
            df_items = parse_rei_sweep_all(json_data, page_n, logger)
            
            helper_columns = {'run_id': run_id, 'dt': dt, 'page_n': page_n, 'condition': condition}

            try:
                with DatabaseInserter() as db_conn:
                    db_conn.insert_to_sql(df_items, items_table_name, logger, helper_columns)
                    db_conn.insert_to_sql(df_page, page_table_name, logger, helper_columns)
            except Exception as e:
                logger.error(f"Error inserting data into database {str(e)}")
            
            offset += page_limit # increment to next page
            item_count = df_page['count'].item() # Assign item_count so it knows when to stop paginating
            time.sleep(random.uniform(2,8)) # wait x-y seconds
    
    # Calculate and log the time elapsed
    elapsed_time = round((time.time() - start_time) / 60, 1)
    logger.info(f"Script completed. Time elapsed: {elapsed_time} minutes.")
    
# argparse to pass in prefix
#> mimir_scraper % python3 rei_sweep_all.py --prefix=test_ --page_cap=1
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and save REI data")
    parser.add_argument("--prefix", help="Optional prefix for table names. ", default="")
    parser.add_argument("--page_cap", help="Cap number of pages for testing. None for unlimited", type=int, default=None)
    args = parser.parse_args()

    main(args.prefix, args.page_cap)