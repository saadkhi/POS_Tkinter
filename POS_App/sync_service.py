import oracledb
import sqlite3
import pandas as pd

# Oracle Configuration (based on Database_connection_test.py)
DB_USER = "botiq"
DB_PASS = "nasir786"
DB_HOST = "79.143.179.51"
DB_PORT = 1539
DB_SERVICE = "oracle"

LOCAL_DB = "local_pos.db"

TABLES_TO_SYNC = [
    "STGS_ARTICLE_CSM",
    "STGS_ARTICLEM",
    "STGS_COLORM",
    "ARTICLE_SIZEM",
    "FACOA",
    "ARTICLE_SIZE_TYPE"
]

def sync_oracle_to_sqlite():
    """Fetches data from Oracle and populates the local SQLite database."""
    try:
        # 1. Connect to Oracle
        dsn = oracledb.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)
        oracle_conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)
        
        # 2. Connect to SQLite
        sqlite_conn = sqlite3.connect(LOCAL_DB)
        
        for table in TABLES_TO_SYNC:
            print(f"Syncing table: {table}...")
            
            # Fetch data using pandas for simplicity
            query = f"SELECT * FROM {table}"
            df = pd.read_sql(query, oracle_conn)
            
            # Drop table if exists to ensure fresh copy (or we could use REPLACE in to_sql)
            # Using REPLACE in to_sql handles table creation and data insertion
            df.to_sql(table, sqlite_conn, if_exists='replace', index=False)
            
            print(f"Successfully synced {len(df)} rows for {table}.")
            
        oracle_conn.close()
        sqlite_conn.close()
        return True, "Synchronization complete!"
        
    except Exception as e:
        error_msg = f"Sync failed: {str(e)}"
        print(error_msg)
        return False, error_msg

if __name__ == "__main__":
    sync_oracle_to_sqlite()
