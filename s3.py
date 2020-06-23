import logging
import boto3
from botocore.exceptions import ClientError
from sys import stdout

logging.basicConfig(
    format="%(levelname)s:%(message)s", level=logging.INFO, stream=stdout
)
logger = logging.getLogger(__name__)


def create_bucket(
    bucket_name: str,
    region: str,
    s3_client,
    s3_resource,
    acl_type: str = "private",
    versions: bool = True,
) -> bool:
    """Create an S3 bucket in a specified region """
    try:
        location = {"LocationConstraint": region}
        s3_client.create_bucket(
            Bucket=bucket_name, CreateBucketConfiguration=location, ACL=acl_type
        )
    except ClientError as error:
        # S3.Client.exceptions.BucketAlreadyExists
        if error.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            logger.warning(f"Bucket {bucket_name} already exists! Using it.")
        else:
            logger.exception(f"Unable to create bucket {bucket_name}.")
            raise
        return False
    if versions:
        try:
            bucket = s3_resource.Bucket(bucket_name)
            bucket.Versioning().enable()
            logger.info(f"Enabled versioning on bucket {bucket_name}.")
        except ClientError:
            logger.exception(f"Failed to enable versioning on bucket {bucket_name}.")
            raise
    return True


def encrypt_bucket(bucket_name: str, s3_client):
    response = s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [
                {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}},
            ]
        },
    )
    print(response)


def block_bucket_public_access(bucket_name: str, s3_client):
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
    bucket_name,
    region: str,
    s3_client,
    s3_resource,
    block_public: bool = True,
    encrypt: bool = True,
):
    """ Creates, encrypts and restricts public access to a new bucket"""
    create_bucket(bucket_name, region, s3_client, s3_resource)
    if encrypt:
        encrypt_bucket(bucket_name, s3_client)
    if block_public:
        block_bucket_public_access(bucket_name, s3_client)
