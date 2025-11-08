"""
ETL Script to load raw CSV files into PostgreSQL using the COPY command.
Usage: python src/etl/load_raw.py
"""

import os
import pandas as pd
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
    Load a CSV file into a PostgreSQL table using the efficient COPY FROM STDIN method.
    """
    try:
        # Read CSV - treat 'NULL' string as actual NULL
        logger.info(f"Reading {csv_path}...")
        df = pd.read_csv(csv_path, na_values=['NULL'], keep_default_na=False)
        
        # Convert float columns to integers if they should be integers
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                # Check if all non-null values are whole numbers
                non_null = df[col].dropna()
                if len(non_null) > 0 and all(non_null == non_null.astype(int)):
                    df[col] = df[col].astype('Int64')  # Nullable integer
        
        # Get columns - exclude only the primary key auto-increment ID
        # Keep all other columns including foreign keys (child_id, case_id, episode_id, etc.)
        primary_keys = {
            'children': 'child_id',
            'cases': 'case_id',
            'episodes': 'episode_id',
            'placements': 'placement_id'
        }
        
        pk = primary_keys.get(table_name)
        if pk:
            columns = [col for col in df.columns if col != pk]
        else:
            # For junction tables or tables without auto-increment PKs, use all columns
            columns = list(df.columns)
        
        if not columns:
            logger.warning(f"No valid columns found for {table_name}")
            return 0

        # Prepare data in CSV format in memory
        output = StringIO()
        # Use CSV format with NULL as the null marker
        df[columns].to_csv(output, sep=',', index=False, header=False, na_rep='NULL')
        output.seek(0)
        
        # Build and execute COPY command
        cols_str = ', '.join(columns)
        copy_sql = f"COPY {table_name} ({cols_str}) FROM STDIN WITH (FORMAT CSV, NULL 'NULL')"

        with conn.cursor() as cur:
            cur.copy_expert(copy_sql, output)
            rows = cur.rowcount
        
        conn.commit()
        logger.info(f"✓ Loaded {rows} rows into {table_name}")
        return rows
        
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
        
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()