import os, argparse, logging, time
from datetime import datetime, timezone
from utils.db_utils import DatabaseInserter
from utils.scrape_utils import initialize_driver
from rei.rei_parser import parse_rei_all

# Configure the logging settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
# Create a handler to write logs to a file
log_file = "scrape_rei_all.log"
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

def main(suffix=None):
    # Log the start time
    start_time = time.time()
    run_id = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    logger.info(f"Script started: {run_id}")
    
    # initialize selenium driver, extract data
    driver = initialize_driver()
    df = parse_rei_all(driver, run_id)
    
    # Determine the table name based on the suffix
    table_name = f'rei_item_all_{suffix}' if suffix else 'rei_item_all'
    
    # Open postgresql connection, insert rows, close
    db_conn = DatabaseInserter()
    db_conn.insert_rei_all(df, table_name)
    db_conn.close()
    
    # Calculate and log the time elapsed
    elapsed_time = round((time.time() - start_time) / 60, 1)
    logger.info(f"Script completed. Time elapsed: {elapsed_time} minutes.")


# argparse allows you to pass in suffix: python scrape_rei_all.py --suffix=test
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and save REI data")
    parser.add_argument("--suffix", help="Optional suffix for the table name", default=None)
    args = parser.parse_args()

    main(args.suffix)