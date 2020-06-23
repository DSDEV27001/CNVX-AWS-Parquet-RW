import logging
import boto3
from botocore.exceptions import ClientError


def create_ec2_instance(image_id: str, instance_type: str, region: str):
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
            NetworkInterfaces=[{"AssociatePublicIpAddress": False, "DeviceIndex": 0,}],
            MinCount=1,
            MaxCount=1,
        )

    except ClientError as e:
        logging.error(e)
        return None
    return response["Instances"][0]


def main(region: str):
    # amazon linux free tier
    image_id = "ami-032598fcc7e9d1c7a"
    instance_type = "t2.micro"

    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s: %(asctime)s: %(message)s"
    )

    instance_info = create_ec2_instance(image_id, instance_type, region)
    if instance_info is not None:
        logging.info(f'Launched EC2 Instance {instance_info["InstanceId"]}')
        logging.info(f'    VPC ID: {instance_info["VpcId"]}')
        logging.info(f'    Private IP Address: {instance_info["PrivateIpAddress"]}')
        logging.info(f'    Current State: {instance_info["State"]["Name"]}')


if __name__ == "__main__":
    main()
