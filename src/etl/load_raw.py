"""
ETL Script to load raw CSV files into PostgreSQL using the COPY command.
Usage: python src/etl/load_raw.py
"""

import os
import pandas as pd
import numpy as np
import psycopg2
import logging
from datetime import datetime
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': 'chapinhall_capstone',
    'user': 'postgres',
    'password': 'mypassword123',  # WARNING: Keep this secure in production!
    'host': 'localhost',
    'port': '5432'
}

# CSV file paths
DATA_DIR = 'data/raw'
CSV_FILES = {
    'children': 'children.csv',
    'cases': 'cases.csv',
    'case_child': 'case_child.csv',
    'episodes': 'episodes.csv',
    'placements': 'placements.csv',
    'allegations': 'allegations.csv',
    'notes': 'notes.csv'
}

# --- Database Connection and Truncation Functions (Unchanged) ---

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def truncate_tables(conn):
    """Truncate all tables before loading (for clean reload)"""
    tables = ['allegations', 'notes', 'placements', 'episodes', 
              'case_child', 'cases', 'children']
    
    try:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                logger.info(f"Truncated table: {table}")
        conn.commit()
        logger.info("All tables truncated successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error truncating tables: {e}")
        raise

# -----------------------------------------------------------------

def load_csv_to_postgres(conn, table_name, csv_path):
    """
    Load a CSV file into a PostgreSQL table using the efficient COPY FROM STDIN method.
    """
    try:
        # Read CSV
        logger.info(f"Reading {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Define date columns for universal cleaning
        date_columns = ['date_of_birth', 'referral_date', 'closure_date', 
                       'entry_date', 'exit_date', 'placement_start', 
                       'placement_end', 'allegation_date', 'note_date']
        
        # --- Data Cleaning (Simplified) ---
        
        for col in date_columns:
            if col in df.columns:
                # Convert to datetime, coercing errors to NaT
        # Replace empty strings with None before converting
                df[col] = df[col].replace('', None)
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Replace all NaN/NaT values with None or an empty string, 
        # which will be correctly interpreted as NULL by the COPY command
        df = df.replace({np.nan: None, pd.NaT: None})
        df = df.fillna('') # Fills remaining NaNs (e.g. in string columns) with empty string

        # Get column names (exclude auto-increment IDs)
        # We must align the DataFrame columns with the target table columns
        columns = [col for col in df.columns if not col.endswith('_id') or 
                  table_name in ['case_child']]
        
        if not columns:
            logger.warning(f"No valid columns found for {table_name}")
            return 0

        # --- Use io.StringIO and COPY FROM STDIN ---

        # 1. Prepare data in a CSV format in memory
        output = StringIO()
        
        # Select and format the relevant columns for the DB. 
        # index=False prevents writing the DataFrame index as a column.
        # header=False prevents writing column names as the first row.
        # na_rep='NULL' tells Pandas to use the string 'NULL' for missing values (None/NaN)
        # which is what COPY FROM expects to treat as a database NULL.
        df[columns].to_csv(output, sep='\t', index=False, header=False, na_rep='NULL')
        output.seek(0)
        
        # 2. Build the COPY command
        cols_str = ', '.join(columns)
        copy_sql = f"COPY {table_name} ({cols_str}) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t', NULL 'NULL')"

        # 3. Execute the COPY command
        with conn.cursor() as cur:
            cur.copy_expert(copy_sql, output)
            rows = cur.rowcount # Get the number of rows inserted
        
        conn.commit()
        logger.info(f"✓ Loaded {rows} rows into {table_name}")
        return rows
        
    except FileNotFoundError:
        logger.warning(f"File not found: {csv_path} - Skipping {table_name}")
        return 0
    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading {table_name}: {e}")
        # Reraise the exception to stop the overall ETL process
        raise

# --- Verification and Main Functions (Unchanged) ---

def verify_data_load(conn):
    """Verify that data was loaded correctly"""
    try:
        with conn.cursor() as cur:
            tables = ['children', 'cases', 'case_child', 'episodes', 
                     'placements', 'allegations', 'notes']
            
            logger.info("\n" + "="*50)
            logger.info("DATA LOAD VERIFICATION")
            logger.info("="*50)
            
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                logger.info(f"{table:20} {count:>10} rows")
            
            logger.info("="*50 + "\n")
            
    except Exception as e:
        logger.error(f"Error verifying data: {e}")

def main():
    """Main ETL pipeline"""
    start_time = datetime.now()
    logger.info("Starting ETL process...")
    logger.info(f"Data directory: {DATA_DIR}")
    
    # Connect to database
    conn = get_db_connection()
    
    try:
        truncate_tables(conn)
        
        # Load each CSV file
        total_rows = 0
        for table_name, csv_file in CSV_FILES.items():
            csv_path = os.path.join(DATA_DIR, csv_file)
            rows = load_csv_to_postgres(conn, table_name, csv_path)
            total_rows += rows
        
        # Verify the load
        verify_data_load(conn)
        
        # Success!
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✓ ETL completed successfully in {duration:.2f} seconds")
        logger.info(f"✓ Total rows loaded: {total_rows}")
        
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        # The exception is already raised in load_csv_to_postgres, 
        # so this will catch the ultimate failure.
        
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()