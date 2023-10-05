import os, argparse, logging, time, random, json
from datetime import datetime, timezone

from utils.db_utils import DatabaseInserter #, table_schema_rei_sweep
from utils.scrape_utils import fetch_rei_scrape_api
#from rei.rei_parser import parse_rei_sweep_page, parse_rei_sweep_all
from log.log_config import log_config

def main(
    prefix,
    base_urls = ['https://www.rei.com/used/p/rei-co-op-flash-hiking-boots-womens/189065?color=Dusty%20Olive%2FGray']
    ):
    # Determine time, script_name, and set run_name by stripping ".py", config logging
    start_time = time.time()
    script_name = os.path.basename(os.path.abspath(__file__))
    run_name = os.path.splitext(script_name)[0]
    logger = log_config(f"{run_name}.log")
    
    # Create tables in postgresql, naming incorporates optional argparse prefix
    run_id = None # initialize run_id to avoid erroring out
    try:
        with DatabaseInserter() as db_conn:
            # for table_name, schema in table_schema_rei_sweep.items():
            #     db_conn.create_table(f'{prefix}{table_name}', schema, logger) # create tables
            run_id = db_conn.start_run(run_name, prefix, logger)
    
    try:
        response_content, request_datetime = fetch_rei_scrape_api()
    file_path = 'output.html'
    
    with open(file_path, "w") as file:
        file.write(response_content)
        
    full_json = extract_json_btw_strings(
        response_content,
        logger=simple_logger,
        start_str = '<script>window.__PRELOADED_STATE__ = ',
        end_str = '</script>')
    
    # Serialize the Python object back into a formatted JSON string
    str_full_json = json.dumps(full_json, indent=4)

    # Write the formatted JSON string to a file
    with open('output_full.json', 'w') as file:
        file.write(str_full_json)
        
    if "item" in full_json:
        item_json = full_json["item"]
        str_item_json = json.dumps(item_json, indent=4)
        with open('output_item.json', 'w') as file:
            file.write(str_item_json)
    else:
        print("The key 'item' does not exist in the JSON data.")
    
    # extract_item_level()
    
    # sku_n = extract_skus()
        
    




# Run script with argparse to pass table prefix --> python3 rei_scrape.py --prefix=test_
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and save item-level and item-variants REI data")
    parser.add_argument("--prefix", help="Optional prefix for table names. ", default="")
    args = parser.parse_args()

    main(args.prefix)