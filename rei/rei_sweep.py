from db_utils import save_to_postgresql
import os

# Get the URI for saving to postgresql
rei_scraper_uri = os.getenv('MIMIR_POSTGRESQL_URI')

# Assume you have a pandas DataFrame `df` containing the cleaned data
# Save it to the PostgreSQL database
save_to_postgresql(df, 'table_name', rei_scraper_uri)
