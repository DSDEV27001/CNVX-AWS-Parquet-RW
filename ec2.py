import logging
import boto3
from botocore.exceptions import ClientError
from sys import stdout

logging.basicConfig(
    format="%(levelname)s:%(message)s", level=logging.INFO, stream=stdout
)
logger = logging.getLogger(__name__)


def create_ec2_instance(image_id: str, instance_type: str, region: str, key_name: str):
    """Provision and launch an EC2 instance and then returns even if
    instance is not yet running. Returns instance info or none if error
    """

    # Provision and launch the EC2 instance
    ec2_client = boto3.client("ec2", region_name=region)
    try:
        response = ec2_client.run_instances(
            BlockDeviceMappings=[
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "VolumeType": "standard",
                        "Encrypted": True,
                    },
                },
            ],
            ImageId=image_id,
            InstanceType=instance_type,
            KeyName=key_name,
            NetworkInterfaces=[{"AssociatePublicIpAddress": False, "DeviceIndex": 0,}],
            MinCount=1,
            MaxCount=1,
            IamInstanceProfile={"Name": "AWSEC2-S3Access"},
        )

    except ClientError as e:
        logging.error(e)
        return None
    return response["Instances"][0]


def create_key_pair(key_name, region: str, private_key_file_name=None):
    """Creates a key pair that can be used to securely connect to an Amazon EC2 instance."""
    try:
        ec2_client = boto3.client("ec2", region_name=region)
        key_pair = ec2_client.create_key_pair(KeyName=key_name)
        logger.info("Created key")
        if private_key_file_name is not None:
            with open(private_key_file_name, "w") as pk_file:
                pk_file.write(key_pair.key_material)
            logger.info("Wrote private key to %s.", private_key_file_name)
    except ClientError:
        logger.exception("Failed to create {key_name}.", key_name)
        raise
    else:
        return key_pair


def launch_ec2_instance(region: str, key_name: str):
    # amazon linux free tier AMI

    image_id = "ami-0330ffc12d7224386"
    instance_type = "t2.micro"

    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s: %(asctime)s: %(message)s"
    )

    instance_info = create_ec2_instance(image_id, instance_type, region, key_name)
    if instance_info is not None:
        logging.info(f'Launched EC2 Instance {instance_info["InstanceId"]}')
        logging.info(f'    VPC ID: {instance_info["VpcId"]}')
        logging.info(f'    Private IP Address: {instance_info["PrivateIpAddress"]}')
        logging.info(f'    Current State: {instance_info["State"]["Name"]}')
