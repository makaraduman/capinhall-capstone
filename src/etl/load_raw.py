"""
ETL Script to load raw CSV files into PostgreSQL
Usage: python src/etl/load_raw.py
"""

import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import logging
from datetime import datetime

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
    'password': '',  # empty if using trust authentication
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

def load_csv_to_postgres(conn, table_name, csv_path):
    """
    Load a CSV file into a PostgreSQL table
    """
    try:
        # Read CSV
        logger.info(f"Reading {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Handle NaN values
        df = df.where(pd.notnull(df), None)
        
        # Convert date columns if they exist
        date_columns = ['date_of_birth', 'referral_date', 'closure_date', 
                       'entry_date', 'exit_date', 'placement_start', 
                       'placement_end', 'allegation_date', 'note_date']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Get column names (exclude auto-increment IDs)
        columns = [col for col in df.columns if not col.endswith('_id') or 
                  table_name in ['case_child']]  # case_child doesn't have data for its ID
        
        if not columns:
            logger.warning(f"No valid columns found for {table_name}")
            return 0
        
        # Prepare data for insertion
        data = [tuple(row) for row in df[columns].values]
        
        # Build INSERT query
        cols_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
        
        # Execute batch insert
        with conn.cursor() as cur:
            cur.executemany(query, data)
        
        conn.commit()
        logger.info(f"✓ Loaded {len(data)} rows into {table_name}")
        return len(data)
        
    except FileNotFoundError:
        logger.warning(f"File not found: {csv_path} - Skipping {table_name}")
        return 0
    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading {table_name}: {e}")
        raise

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
        # Optional: Truncate existing data (comment out if you want to append)
        # truncate_tables(conn)
        
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
        raise
    
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()
