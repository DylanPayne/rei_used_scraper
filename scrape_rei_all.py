import os
from utils.db_utils import DatabaseInserter
from utils.scrape_utils import initialize_driver
from rei.rei_parser import parse_rei_all


# Your main scraping logic goes here

def main(table_suffix=None):
    driver = initialize_driver()
    df = parse_rei_all(driver)
    
    # Determine the table name based on the suffix
    table_name = f'rei_item_all_{table_suffix}' if table_suffix else 'rei_item_all'
    
    db_conn = DatabaseInserter()
    db_conn.insert_rei_all(df, table_name)
    db_conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and save REI data")
    parser.add_argument("--table-suffix", help="Optional suffix for the table name", default=None)
    args = parser.parse_args()

    main(args.table_suffix)