from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
from sqlalchemy import text

INSTANCE_CONNECTION_NAME = "day1-codevipassana:us-central1:feedfrontproduction" 
DB_USER = "test" 
DB_PASS = "test" 
DB_NAME = "formdata" 
USE_PRIVATE_IP = False  

def connect_with_connector():
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.
    Uses the Cloud SQL Python Connector package.
    """
    print('Inside the connector function')
    ip_type = IPTypes.PRIVATE if USE_PRIVATE_IP else IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn():
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pymysql",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        return conn

    print('After getconn function')

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

        print('try')
        engine, connector = connect_with_connector()
        print('after connect_with_connector in try')

        # Perform database operations
        with engine.connect() as conn:
            print("Creating form data table...")
            insert_query = """
                CREATE TABLE IF NOT EXISTS formdata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                form_id VARCHAR(255) NOT NULL,
                questiontype VARCHAR(255) NOT NULL,
                question VARCHAR(255) NOT NULL,
                options VARCHAR(255) NOT NULL,
                ratings VARCHAR(255) NOT NULL);
            """
            resp = conn.execute(text(insert_query))
            conn.commit()  
            print(resp)
            print("Form data table created successfully...")
        
        with engine.connect() as conn:
            print("Creating form mappings table...")
            insert_query = """
                CREATE TABLE IF NOT EXISTS formmappings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                form_id VARCHAR(255) NOT NULL,
                form_mapping_id VARCHAR(7) NOT NULL
            );
            """
            resp = conn.execute(text(insert_query))
            conn.commit()  
            print(resp)
            print("Form mappings table created successfully...")
        
        with engine.connect() as conn:
            print("Creating form responses table...")
            insert_query="""CREATE TABLE formresponses (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                form_id VARCHAR(255) NOT NULL,     
                question_id INT NOT NULL,         
                actual_question TEXT NOT NULL,    
                answer TEXT NOT NULL,              
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
            );"""
            resp = conn.execute(text(insert_query))
            conn.commit()  
            print(resp)
            print("Form responses table created successfully...")

        # Perform database operations
        with engine.connect() as conn:
            print("Reading data from the formdata table...")
            result = conn.execute(text("SELECT * FROM formdata;"))
            rows = result.fetchall()  # Fetch all rows as a list of tuples
            print(rows)

    except Exception as e:
        print("Error occurred:", e)

    finally:
        # Close the connector to release resources
        if 'connector' in locals() and connector is not None:
            print("Closing the connector...")
            connector.close()