from os import getenv
import psycopg
from dotenv import load_dotenv


class database:
    def __init__(self):
        load_dotenv(override=True)
        self.dbname = getenv('DBNAME')
        self.user = getenv('USER')
        self.password = getenv('PASSWORD')
        self.host = getenv('HOST')
        self.port = getenv('PORT')

    def append(self, formatted_data):
        try:
            with psycopg.connect(
                dbname = self.dbname,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port) as conn:

                # Create connection pipeline for commands
                with conn.cursor() as cur:

                    # Execute SQL command and store values
                    cur.executemany(
                        """INSERT INTO pit_antenna 
                        (uuid, date, time, reader_id, tag_id, latitude, 
                        longitude, ip_address, datetime, site) VALUES 
                        (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        ON CONFLICT 
                        (date, time, reader_id, tag_id) DO NOTHING""", 
                        formatted_data)

                # Commit changes 
                conn.commit()    

                # Close postgres connection    
                cur.close()
                conn.close()
        except psycopg.OperationalError as e:
            print("""OperationError, cannot connect to postgres DB
                  Please check connection credentials.
                  Error: {}""".format(e))
