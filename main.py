import pandas as pd
import numpy as np
import logging
import pyarrow
import boto3
from botocore.exceptions import ClientError
from sys import stdout

logging.basicConfig(
    format="%(levelname)s:%(message)s", level=logging.INFO, stream=stdout
)
logger = logging.getLogger(__name__)
BUCKET = "md123"
REGION = "eu-west-2"

s3_client = boto3.client("s3", region_name=REGION)
s3_resource = boto3.resource("s3", region_name=REGION)


def df_to_parquet(df_in: pd.DataFrame, filepath: str, idx: bool = False, **kwargs):
    """Export a DataFrame to a parquet file"""
    df_in.to_parquet(path=filepath, index=idx, engine="pyarrow", **kwargs)


def create_bucket(bucket_name: str, region: str, acl_type: str = "private", versions: bool = True) -> bool:
    """Create an S3 bucket in a specified region """
    try:
        location = {"LocationConstraint": region}
        bucket = s3_client.create_bucket(
            Bucket=bucket_name, CreateBucketConfiguration=location, ACL=acl_type
        )
    except ClientError as error:
        # S3.Client.exceptions.BucketAlreadyExists
        if error.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            logger.warning("Bucket %s already exists! Using it.", bucket_name)
            bucket = s3_resource.Bucket(bucket_name)
        else:
            logger.exception("Couldn't create bucket %s.", bucket_name)
            raise
        return False
    if versions:
        try:
            bucket.Versioning().enable()
            logger.info("Enabled versioning on bucket %s.", bucket_name)
        except ClientError:
            logger.exception("Couldn't enable versioning on bucket %s.", bucket_name)
            raise
    return True


def encrypt_bucket(bucket_name: str):
    response = s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [
                {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}},
            ]
        },
    )
    print(response)


def block_bucket_public_access(bucket_name: str):
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )


def new_bucket_config(
    bucket_name, region: str, block_public: bool = True, encrypt: bool = True
):
    create_bucket(bucket_name, region)
    if encrypt:
        encrypt_bucket(bucket_name)
    if block_public:
        block_bucket_public_access(bucket_name)


def main():
    new_bucket_config(BUCKET, REGION)
    url = f"s3://{BUCKET}/data.parquet"
    # randomly generate an integer DataFrame
    df_rand = pd.DataFrame(
        np.random.randint(0, 999, size=(100000, 10)), columns=list("ABCDEFGHIJ")
    )
    df_rand.to_parquet(url, engine="pyarrow")


main()
