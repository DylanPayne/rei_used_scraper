import os, logging
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Define the table schemas using a dictionary
table_schema_rei_sweep = { # create_table appends primary_key, id (sequential)
    'rei_sweep_page': {
        'count': 'INTEGER',
        'page_limit': 'INTEGER',
        'condition': 'VARCHAR(20)',
        'page_n': 'INTEGER',
        'run_id': 'INTEGER',
        'dt': 'timestamp',
    },
    'rei_sweep_all': {
        'title': 'VARCHAR(100)', # 51 max observed
        'brand': 'VARCHAR(40)', # 17 max obs
        'path': 'VARCHAR(180)', # 116 max obs
        'parent_sku': 'INTEGER',
        'color': 'VARCHAR(60)', # 29 max obs
        'price': 'NUMERIC(7,2)', # Stores up to $99,999.99
        'price_orig': 'NUMERIC(7,2)', # 116 max obs
        'price_range': 'NUMERIC(7,2)[]', # 116 max obs
        'size_range': 'VARCHAR(50)[]', # 26 max obs
        'condition': 'VARCHAR(20)', # 19 max obs, code already breaks if condition names change
        'page_n': 'INTEGER',
        'run_id': 'INTEGER',
        'dt': 'timestamp',
    },
    # Add more tables and their schemas here
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

    def create_table(self, table_name, columns):
        with self.engine.connect() as connection:
            column_definitions = [f"{column} {data_type}" for column, data_type in columns.items()]
            column_definitions.append("id SERIAL PRIMARY KEY")
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
            print("Executing query:", create_table_query)
            connection.execute(text(create_table_query))
            
    def insert_to_sql(self, df: pd.DataFrame, table_name: str, helper_columns, logger):
        if df is None:
            logger.warning(f"No data to save to {table_name}. Skipping.")
            return
        
        # Add columns and values from helper_columns dictionary
        for column, value in helper_columns.items():
            df[column] = value

        # Save DataFrame to PostgreSQL table
        df.to_sql(table_name, self.engine, index=False, if_exists='append')
        logger.info(f"Saved {len(df)} rows to {table_name}")
        return
    
    def close(self):
        self.engine.dispose()  # Close the database engine