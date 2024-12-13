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
    print('inside connet with connector')
    ip_type = IPTypes.PRIVATE if USE_PRIVATE_IP else IPTypes.PUBLIC

    # Initialize the Cloud SQL connector
    connector = Connector(ip_type)
    
    print('connector')

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
    return pool

if __name__ == "__main__":
    try:
        # Connect to the database
        print('try')
        engine = connect_with_connector()
        print('after connet with connector')

        # Test query to confirm connection
        
        # with engine.connect() as conn:
        #     print("inside with")
        #     create_table_query = """
        #     CREATE TABLE IF NOT EXISTS formdata (
        #         id INT AUTO_INCREMENT PRIMARY KEY,
        #         form_id VARCHAR(255) NOT NULL,
        #         questiontype VARCHAR(255) NOT NULL,
        #         question VARCHAR(255) NOT NULL,
        #         options VARCHAR(255) NOT NULL,
        #         ratings VARCHAR(255) NOT NULL
        #     );
        #     """
        #     conn.execute(text(create_table_query))
        #     print("formdata table created successfully.")
        #     # print(row["message"])

        # CREATE TABLE IF NOT EXISTS formmappings (
        #     id INT AUTO_INCREMENT PRIMARY KEY,
        #     form_id VARCHAR(255) NOT NULL,
        #     form_mapping_id VARCHAR(7) NOT NULL,
        #     FOREIGN KEY (form_id) REFERENCES formdata(form_id) ON DELETE CASCADE
        # );

        with engine.connect() as conn:
            print("Inserting data into formdata table...")
            # insert_query = """
            #     CREATE TABLE IF NOT EXISTS formdata (
            #     id INT AUTO_INCREMENT PRIMARY KEY,
            #     form_id VARCHAR(255) NOT NULL,
            #     questiontype VARCHAR(255) NOT NULL,
            #     question VARCHAR(255) NOT NULL,
            #     options VARCHAR(255) NOT NULL,
            #     ratings VARCHAR(255) NOT NULL);
            # """

            # insert_query="""CREATE TABLE IF NOT EXISTS formmappings (
            #     id INT AUTO_INCREMENT PRIMARY KEY,
            #     form_id VARCHAR(255) NOT NULL,
            #     form_mapping_id VARCHAR(7) NOT NULL
            # );"""

            # insert_query="""CREATE TABLE formresponses (
            #     id INT AUTO_INCREMENT PRIMARY KEY, 
            #     form_id VARCHAR(255) NOT NULL,     
            #     question_id INT NOT NULL,         
            #     actual_question TEXT NOT NULL,    
            #     answer TEXT NOT NULL,              
            #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
            #     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
            # );"""


            # insert_query="""DROP TABLE IF EXISTS formdata;"""

            # insert_query="""DROP TABLE IF EXISTS formmappings;"""

            # insert_query="""SELECT * from formdata;"""

            result = conn.execute(text("SELECT * FROM formdata;"))
            rows = result.fetchall()  # Fetch all rows as a list of tuples
            print(rows)



            resp = conn.execute(text(insert_query))
            conn.commit()  
            print("Data inserted successfully.")

        # with engine.connect() as conn:
        #     print("Reading data from the formdata table...")
        #     result = conn.execute(text("SELECT * FROM formdata;"))
        #     rows = result.fetchall()  # Fetch all rows as a list of tuples
        #     print(rows)
        #     for row in rows:
        #         print(f"id: {row[0]}, form_id: {row[1]}, questiontype: {row[2]}, question: {row[3]}, options: {row[4]}, ratings: {row[5]}")


    except Exception as e:
        print("Error occurred:", e)