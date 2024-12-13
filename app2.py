from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
from sqlalchemy import text

# Hardcoded values
INSTANCE_CONNECTION_NAME = "day1-codevipassana:us-central1:feedfrontsql"  # Replace with your instance connection name
DB_USER = "test"  # Replace with your database username
DB_PASS = "test"  # Replace with your database password
DB_NAME = "formdata"  # Replace with your database name
USE_PRIVATE_IP = False  # Set to True if using private IP

def connect_with_connector():
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.
    Uses the Cloud SQL Python Connector package.
    """
    print('inside connect_with_connector')
    ip_type = IPTypes.PRIVATE if USE_PRIVATE_IP else IPTypes.PUBLIC

    # Initialize the Cloud SQL connector
    connector = Connector(ip_type)

    # Connection function
    def getconn():
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pymysql",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        return conn

    print('after getconn function')

    # Create SQLAlchemy connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    print('got pool')
    print(pool)
    return pool, connector

if __name__ == "__main__":
    try:
        # Connect to the database
        print('try')
        engine, connector = connect_with_connector()
        print('after connect_with_connector')

        # Perform database operations
        with engine.connect() as conn:
            print("Reading data from the formdata table...")
            result = conn.execute(text("SELECT * FROM formresponses;"))
            rows = result.fetchall()  # Fetch all rows as a list of tuples
            print(rows)

    except Exception as e:
        print("Error occurred:", e)

    finally:
        # Close the connector to release resources
        if 'connector' in locals() and connector is not None:
            print("Closing the connector...")
            connector.close()
