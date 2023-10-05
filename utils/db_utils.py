import os, logging, traceback
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() # load env variables, i.e., database URIs, proxies

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Define the table schemas using a dictionary
table_schema_rei_sweep = { # create_table appends primary_key, id (sequential)
    'rei_sweep_page': {
        'count': 'INTEGER',
        'page_limit': 'INTEGER',
        'condition': 'VARCHAR(20)',
        'page_n': 'INTEGER',
        'id': 'SERIAL PRIMARY KEY',
        'run_id': 'INTEGER',
        'dt': 'TIMESTAMP',
    },
    'rei_sweep_all': {
        'title': 'VARCHAR(100)', # 51 max observed
        'brand': 'VARCHAR(40)', # 17 max obs
        'path': 'VARCHAR(180)', # 116 max obs
        'parent_sku': 'INTEGER',
        'color': 'VARCHAR(60)', # 29 max obs
        'price': 'NUMERIC(10,2)', # Stores up to $99,999.99
        'price_orig': 'NUMERIC(10,2)', 
        'price_range': 'NUMERIC(10,2)[]', # 116 max obs
        'size_range': 'VARCHAR(50)[]', # 26 max obs
        'condition': 'VARCHAR(20)', # 19 max obs, code already breaks if condition names change
        'page_n': 'INTEGER',
        'id': 'SERIAL PRIMARY KEY',
        'run_id': 'INTEGER',
        'dt': 'TIMESTAMP',
    },
    'rei_run' : {
        'run_id': 'SERIAL PRIMARY KEY',
        'run_name': 'VARCHAR(200) NOT NULL',
        'run_dt': 'TIMESTAMP NOT NULL',
    },
}

class DatabaseInserter:
    def __init__(self):
        env_str = "MIMIR_POSTGRESQL_URI"
        self.uri = os.environ.get(env_str)
        if self.uri is None:
            raise ValueError(f"{env_str} not found in environment variables")
        self.engine = create_engine(self.uri)
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def create_table(self, table_name, columns, logger):
        # Define the columns and generate "create table" query
        column_definitions = [f"{column} {data_type}" for column, data_type in columns.items()]
        # column_definitions.append("id SERIAL PRIMARY KEY")
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
        try:
            with self.engine.connect() as connection:
                connection.execution_options(isolation_level="AUTOCOMMIT")
                logger.info(f"Executing query: {create_table_query}")
                connection.execute(text(create_table_query))
        except Exception as e:
            print(f"Error executing query {create_table_query} {e}")
            
    def insert_to_sql(self, df: pd.DataFrame, table_name: str, logger, helper_columns=None):
        if df is None:
            logger.warning(f"No data to save to {table_name}. Skipping.")
            return
        # Add optional helper_columns via dictionary
        if helper_columns is not None:
            for column, value in helper_columns.items():
                df[column] = value
        # Save DataFrame to PostgreSQL table
        try:
            df.to_sql(table_name, self.engine, index=False, if_exists='append')
            logger.info(f"Saved {len(df)} rows to {table_name}")
        except Exception as e:
            logger.error(f"Error saving data to {table_name}: \n{traceback.format_exc()}")
            
    def start_run(self, run_name, prefix, logger):
        run_dt = datetime.utcnow()
        table_name = f"{prefix}rei_run"
        insert_query = text(f"INSERT INTO {table_name} (run_dt, run_name) VALUES (:run_dt, :run_name) RETURNING run_id;")
        try:
            with self.engine.connect() as connection:
                connection.execution_options(isolation_level="AUTOCOMMIT") # automatically commit insertions
                result = connection.execute(insert_query, {'run_dt': run_dt, 'run_name': run_name})
                run_id = result.fetchone()[0]
                logger.info(f"{run_name} started run_id: {run_id}")
                return run_id
        except Exception as e:
            logger.error(f"Error adding run {run_id} of {run_name} into {table_name}: {e} \n {insert_query}")
        
    def close(self):
        self.engine.dispose()  # Close the database engine
        
def generate_rei_scrape_queue(db_conn, item_limit, logger):
    # Query another table in PostgreSQL to generate the daily queue
    # This could be any query that suits your use case
    queue_query = "SELECT distinct item_id FROM some_table WHERE some_condition=True;"
    try:
        queue_items = db_conn.execute_query(queue_query)
        # Store these items in a queue table or in-memory data structure
        # ... (implementation depends on your needs)
        logger.info(f"Generated daily queue with {len(queue_items)} items.")
    except Exception as e:
        logger.error(f"Error generating daily queue: {e}")
        
        
table_schema_rei_scrape = { # create_table appends primary_key, id (sequential)
    'rei_scrape_sku': {
        'count': 'INTEGER',
        'page_limit': 'INTEGER',
        'condition': 'VARCHAR(20)',
        'page_n': 'INTEGER',
        'id': 'SERIAL PRIMARY KEY',
        'run_id': 'INTEGER',
        'dt': 'TIMESTAMP',
    },
    'rei_scrape_item': {
        'title': 'VARCHAR(100)', # 51 max observed
        'brand': 'VARCHAR(40)', # 17 max obs
        'path': 'VARCHAR(180)', # 116 max obs
        'parent_sku': 'INTEGER',
        'color': 'VARCHAR(60)', # 29 max obs
        'price': 'NUMERIC(10,2)', # Stores up to $99,999.99
        'price_orig': 'NUMERIC(10,2)', 
        'price_range': 'NUMERIC(10,2)[]', # 116 max obs
        'size_range': 'VARCHAR(50)[]', # 26 max obs
        'condition': 'VARCHAR(20)', # 19 max obs, code already breaks if condition names change
        'page_n': 'INTEGER',
        'id': 'SERIAL PRIMARY KEY',
        'run_id': 'INTEGER',
        'dt': 'TIMESTAMP',
    },
    'rei_scrape_queue' : {
        'parent_sku': 'UNIQUE NOT NULL',
        'path': 'TEXT',
        'status': 'VARCHAR(20) DEFAULT "pending"',
        'id': 'SERIAL PRIMARY  KEY',
        'run_id': 'INTEGER',
        'dt': 'TIMESTAMP NOT NULL',
    },
    'rei_run' : {
        'run_id': 'SERIAL PRIMARY KEY',
        'run_name': 'VARCHAR(200) NOT NULL',
        'run_dt': 'TIMESTAMP NOT NULL',
    },
}