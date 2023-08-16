import os, logging
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime


class DatabaseInserter:
    def __init__(self):
        env_str = "MIMIR_POSTGRESQL_URI"
        self.uri = os.environ.get(env_str)
        if self.uri is None:
            raise ValueError(f"{env_str} not found in environment variables")
        self.engine = create_engine(self.uri)
    
    def insert_rei_all(self, df: pd.DataFrame, table_name: str, run_id : int, dt : datetime, logger):
        # Add run_id as a new column to df
        df['run_id'] = run_id
        df['dt'] = dt
        
        # Create a SQLAlchemy engine using the given database URI
        engine = create_engine(self.uri)

        # Save DataFrame to PostgreSQL table
        df.to_sql(table_name, engine, index=False, if_exists='append')
        logger.info(f"Saved {len(df)} rows to {table_name}")
        return
    
    def close(self):
        self.engine.dispose()  # Close the database engine
        
        
        
# # Usage
# db_conn = DatabaseConnection()
# db_conn.insert_data(df1, 'table_name1')
# db_conn.insert_data(df2, 'table_name2')
# db_conn.close()