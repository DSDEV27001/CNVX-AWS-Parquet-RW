import pandas as pd
import numpy as np
import boto3
from botocore.exceptions import ClientError
import logging
import pyarrow

BUCKET = "md123"
REGION = "eu-west-2"
s3_client = boto3.client("s3", region_name=REGION)


def df_to_parquet(df_in: pd.DataFrame, filepath: str, idx: bool = False, **kwargs):
    """Export a DataFrame to a parquet file"""
    df_in.to_parquet(path=filepath, index=idx, engine="pyarrow", **kwargs)


# url = "s3://md1234/data.parquet"


def create_bucket(
    bucket_name: str, region: str = None, acl_type: str = "private"
) -> bool:
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client("s3")
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client("s3", region_name=region)
            location = {"LocationConstraint": region}
            s3_client.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration=location, ACL=acl_type
            )
    except ClientError as e:
        # S3.Client.exceptions.BucketAlreadyExists
        # S3.Client.exceptions.BucketAlreadyOwnedByYou
        logging.error(e)
        return False
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
    s3_client.put_public_access_block(Bucket=bucket_name, PublicAccessBlockConfiguration={"BlockPublicAcls": True,"IgnorePublicAcls": True,"BlockPublicPolicy": True,"RestrictPublicBuckets": True})


create_bucket(BUCKET, REGION)
encrypt_bucket(BUCKET)
block_bucket_public_access(BUCKET)

# response = s3_client.create_access_point(
#     AccountId='string',
#     Name='string',
#     Bucket='string',
#     VpcConfiguration={
#         'VpcId': 'string'
#     },
#     PublicAccessBlockConfiguration={
#         'BlockPublicAcls': True|False,
#         'IgnorePublicAcls': True|False,
#         'BlockPublicPolicy': True|False,
#         'RestrictPublicBuckets': True|False
#     }
# )


url = f"s3://{BUCKET}/data.parquet"
# randomly generate an integer DataFrame
df_rand = pd.DataFrame(
    np.random.randint(0, 999, size=(100000, 10)), columns=list("ABCDEFGHIJ")
)

df_rand.to_parquet(url, engine="pyarrow")

print("3")
