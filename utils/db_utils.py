import os
import pandas as pd
from sqlalchemy import create_engine

def save_to_postgresql(df: pd.DataFrame, table_name: str, db_uri: str):
    """
    Function to save a pandas DataFrame to a PostgreSQL table.
    :param df: DataFrame containing the data to be saved.
    :param table_name: Name of the table where the data will be saved.
    :param db_uri: URI for the PostgreSQL database connection.
    """
    # Create a SQLAlchemy engine using the given database URI
    engine = create_engine(db_uri)

    # Save the DataFrame to the PostgreSQL table
    df.to_sql(table_name, engine, index=False, if_exists='replace')

    # Close the database connection
    engine.dispose()
