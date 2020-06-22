import pandas as pd
import numpy as np
import boto3
import pyarrow
import smart_open


def df_to_parquet(df_in: pd.DataFrame, filepath: str, idx: bool = False, **kwargs):
    """Export a DataFrame to a parquet file"""
    df_in.to_parquet(path=filepath, index=idx, engine="pyarrow", **kwargs)


url = 's3://md1234/test.txt'

# randomly generate an integer DataFrame
df_rand = pd.DataFrame(
    np.random.randint(0, 999, size=(100000, 10)), columns=list("ABCDEFGHIJ")
)

df_rand.to_parquet(url)


# def file_to_s3():
#     # client = boto3.client("s3")
#     session = boto3.session.Session()
#     url = 's3://md1234/test.txt'
#     with smart_open.open(url, 'wb', transport_params={'session': session}) as fout:
#         bytes_written = fout.write(b'hello world!')
#     print(bytes_written)




