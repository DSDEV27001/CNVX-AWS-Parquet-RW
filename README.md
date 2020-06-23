# CNVX-AWS-Parquet-RW
Writes a parquet file to a new s3 bucket with randomly generated data. 
Reads the parquet from S3 in a new EC2 instance using R
## Prerequisites
You must have Docker installed. For installation instructions see [Docker's Website](https://docs.docker.com/get-docker/).

To verify your installation of Docker, run the following command and confirm there is an output.

    $ docker --version
    Docker version 19.03.8

## How to run
Run the commands below in the project directory to create a new docker build and run through the task

    $ docker build . 
    $ docker-compose up
## 

## Outstanding actions

* Allow to specify AWS credentials profile to use (the use of pandas and s3fs to write to S3 doesn't appear to allow anything but the default profile)
* Add Unit Tests (eg can we access the created bucket if an anon user etc)
* Write R script and set up instance to run
