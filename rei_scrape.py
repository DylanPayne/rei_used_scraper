import os, argparse, logging, time, random, json
from datetime import datetime, timezone

from utils.db_utils import DatabaseInserter #, table_schema_rei_sweep
from utils.scrape_utils import fetch_rei_scrape_api
#from rei.rei_parser import parse_rei_sweep_page, parse_rei_sweep_all
from log.log_config import log_config

def main(
    base_urls = ['https://www.rei.com/used/p/rei-co-op-flash-hiking-boots-womens/189065?color=Dusty%20Olive%2FGray']
    ):
    start_time = time.time()
    # Determine script_name, and strip off extension to determine run_name
    script_name = os.path.basename(os.path.abspath(__file__))
    run_name = os.path.splitext(script_name)[0]
    # Configure logging
    logger = log_config(f"{run_name}.log")
    logger.info(f"/n Starting {script_name}")
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
    return None    
    # initialize run_id to handle errors within try block
    run_id = None
    
    try:
        
    




if __name__ == "__main__":
    main()