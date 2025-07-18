import argparse
import os
import pandas as pd
from time import time
from sqlalchemy import create_engine
import urllib.request

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    if url:
        csv_name = 'output.csv' 
        print(f'Downloading file from URL: {url}')
        try:
            urllib.request.urlretrieve(url, csv_name)
            print(f'File downloaded successfully as {csv_name}')
        except Exception as e:
            print(f'Error downloading file: {e}')
            return
    else:
        # Nếu không có URL, sử dụng file local
        csv_name = r'C:\Users\me123\Documents\ny_taxi\yellow_tripdata_2021-01.csv'
        print(f'Using local file: {csv_name}')
        
        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(csv_name):
            print(f'Error: File {csv_name} does not exist!')
            return

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        t_start = time()
        
        df = next(df_iter)
        
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        
        df.to_sql(name=table_name, con=engine, if_exists='append')
        
        t_end = time()
        
        print('inserted another chunk..., took %.3f second' % (t_end - t_start))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to PostgreSQL')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table-name', help='name of the table where we will write the results to')
    parser.add_argument('--url', required=False, help='url of the csv file (optional, if not provided will use local file)')


    args = parser.parse_args()
    
    main(args)


