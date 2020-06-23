import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
iam = boto3.resource("iam")


def create_policy(name: str, description: str, actions: str, resource_arn: str):
    """ Creates a policy and returns it """
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": actions, "Resource": resource_arn}],
    }
    try:
        policy = iam.create_policy(
            PolicyName=name,
            Description=description,
            PolicyDocument=json.dumps(policy_doc),
        )
        logger.info("Created policy %s.", policy.arn)
    except ClientError as error:
        if error.response["Error"]["Code"] == "EntityAlreadyExists":
            logger.exception(f"Unable to create policy {name} as it already exists.")
        else:
            logger.exception(f"Unexpected error: {error}")
        raise
    else:
        return policy


def create_role(role_name, allowed_services):
    """ Creates a role and lets a list of specified services assume the role """
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": service},
                "Action": "sts:AssumeRole",
            }
            for service in allowed_services
        ],
    }

    try:
        role = iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        logger.info(f"Created role {role.name}.")
    except ClientError:
        logger.exception(f"Unable create role {role_name}.")
        raise
    else:
        return role

def attach_policy_to_role(role_name, policy_arn):
    """ Attaches a policy to a role """
    try:
        iam.Policy(policy_arn).attach_role(RoleName=role_name)
        logger.info(f"Attached policy {policy_arn} to role {role_name}.")
    except ClientError:
        logger.exception(f"Unable to attach policy {policy_arn} to role {role_name}.")
        raise


def create_instance_profile(instance_profile_name: str):
    """ Creates a new instance profile"""
    try:
        iam.create_instance_profile(
            InstanceProfileName=instance_profile_name
        )
        logger.info(f"Created instance profile {instance_profile_name}.")
    except ClientError:
        logger.exception(f"Unable to create instance profile {instance_profile_name}.")
        raise


def main(bucket_name: str):
    """ Shows how to use the policy functions """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    bucket_arn = f"arn:aws:s3:::{bucket_name}"
    policy = create_policy(
        f"AWSEC2-{bucket_name}-S3ReadOnlyAccess-Policy",
        f"Role Policy for EC2 Instance access to named S3 Bucket: {bucket_name}",
        ["s3:GetObject", "s3:ListObjects"],
        bucket_arn,
    )
    create_role("AWSEC2-S3Access", ["ec2.amazonaws.com"])
    attach_policy_to_role("AWSEC2-S3Access", policy.arn)
    create_instance_profile("AWSEC2-S3Access")
