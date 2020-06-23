import pandas as pd
import numpy as np
import logging
import pyarrow
import boto3
import ec2, iam, s3
from sys import stdout


logging.basicConfig(
    format="%(levelname)s:%(message)s", level=logging.INFO, stream=stdout
)
logger = logging.getLogger(__name__)
BUCKET = "cnvx2"
REGION = "eu-west-2"

s3_client = boto3.client("s3", region_name=REGION)
s3_resource = boto3.resource("s3", region_name=REGION)


def df_to_parquet(df_in: pd.DataFrame, file: str, idx: bool = False, **kwargs):
    """Export a DataFrame to a parquet file"""
    try:
        df_in.to_parquet(path=file, index=idx, engine="pyarrow", **kwargs)
    except Exception as error:
        logger.exception(f"Unable to export dataframe: {error}")
        raise


def main():
    s3.new_bucket_config(BUCKET, REGION, s3_client, s3_resource)
    url = f"s3://{BUCKET}/data.parquet"
    # randomly generate an integer DataFrame
    df_rand = pd.DataFrame(
        np.random.randint(0, 999, size=(100000, 10)), columns=list("ABCDEFGHIJ")
    )
    df_to_parquet(df_rand, url)
    iam.main(BUCKET)
    ec2.main(REGION)


if __name__ == "__main__":
    main()
