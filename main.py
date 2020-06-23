import pandas as pd
import numpy as np
import logging
import pyarrow
import boto3
import ec2, iam, s3
from sys import stdout

# boto3.setup_default_session(profile_name='default1')

logging.basicConfig(
    format="%(levelname)s:%(message)s", level=logging.INFO, stream=stdout
)
logger = logging.getLogger(__name__)
BUCKET = "cnvx2"
REGION = "eu-west-2"

s3_client = boto3.client("s3", region_name=REGION)
s3_resource = boto3.resource("s3", region_name=REGION)


def df_to_parquet(df_in: pd.DataFrame, file: str, idx: bool = False, **kwargs):
    """ Export a DataFrame to a parquet a local file or s3 bucketv"""
    try:
        df_in.to_parquet(path=file, index=idx, engine="pyarrow", **kwargs)
    except Exception as error:
        logger.exception(f"Unable to export DataFrame: {error}")
        raise


def create_rand_int_df():
    """Create a new DataFrame populated with random integers"""
    try:
        df_rand = pd.DataFrame(
            np.random.randint(0, 999, size=(100000, 10)), columns=list("ABCDEFGHIJ")
        )
        return df_rand
    except Exception as error:
        logger.exception(f"Unable to create random integer DataFrame: {error}")
        raise


def main():
    s3.new_bucket_config(BUCKET, REGION, s3_client, s3_resource)
    url = f"s3://{BUCKET}/data.parquet"
    df_to_parquet(create_rand_int_df(), url)
    iam.create_ec2_s3_access_control(BUCKET)
    ec2.launch_ec2_instance(REGION)
    keypair = ec2.create_key_pair("connectEC2",REGION)
    print(f"Your keypair is: {keypair}")


if __name__ == "__main__":
    main()
