# Introduction
Music streaming startup Sparkify, want to move their processes and data onto the cloud. Currently their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

This project builds an ETL pipeline that extracts the data from S3, stages it in Redshift, and transforms data into a set of dimensional tables for the analytics team to continue finding insights in what songs their users are listening to.
# Setup
All configuration is performed in the dwh.cfg file. None of the credentials or cluster specifics are included in this repository version. You will need to spin up a cluster in AWS and fill in the details in the config file prior to running the ETL pipeline

## AWS Infrastructure as Code
All configuration will be stored in the file dwh.cfg and make use of Python's config module for parsing. It sould look like this:
```python
[CLUSTER]
HOST=''
DB_NAME=''
DB_USER=''
DB_PASSWORD=''
DB_PORT=

[IAM_ROLE]
ARN=''

[S3]
LOG_DATA='s3://udacity-dend/log_data'
LOG_JSONPATH='s3://udacity-dend/log_json_path.json'
SONG_DATA='s3://udacity-dend/song_data'
```
You can then spin up your redshift cluster using the following code (or do it via your AWS console):
```python
import configparser
import boto3

### CONFIG ###
config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))
KEY='some_key'
SECRET='some_secret'

# CLUSTER
HOST=config.get('CLUSTER','HOST')
DB_NAME=config.get('CLUSTER','DB_NAME')
DB_USER=config.get('CLUSTER','DB_USER')
DB_PASSWORD=config.get('CLUSTER','DB_PASSWORD')
DB_PORT=config.get('CLUSTER','DB_PORT')

# IAM_ROLE
ARN=config.get('IAM_ROLE','ARN')

# S3
LOG_DATA=config.get('S3','LOG_DATA')
LOG_JSONPATH=config.get('S3','LOG_JSONPATH')
SONG_DATA=config.get('S3','SONG_DATA')

DWH_CLUSTER_TYPE='multi-node'
DWH_NUM_NODES=4
DWH_NODE_TYPE='dc2.large'

DWH_IAM_ROLE_NAME='dwhRole'
DWH_CLUSTER_IDENTIFIER='dwhCluster'
DWH_DB='dwh'
DWH_DB_USER='changeme'
DWH_DB_PASSWORD='password'
DWH_PORT=5439

#### INITIATE AWS INFRASTRUCTURE ####
ec2 = boto3.resource('ec2',
                       region_name="us-west-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                    )

s3 = boto3.resource('s3',
                       region_name="us-west-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                   )

iam = boto3.client('iam',aws_access_key_id=KEY,
                     aws_secret_access_key=SECRET,
                     region_name='us-west-2'
                  )

redshift = boto3.client('redshift',
                       region_name="us-west-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                       )

#### CREATE ROLE #####
from botocore.exceptions import ClientError

#1.1 Create the role, 
try:
    print("1.1 Creating a new IAM Role") 
    dwhRole = iam.create_role(
        Path='/',
        RoleName=DWH_IAM_ROLE_NAME,
        Description = "Allows Redshift clusters to call AWS services on your behalf.",
        AssumeRolePolicyDocument=json.dumps(
            {'Statement': [{'Action': 'sts:AssumeRole',
               'Effect': 'Allow',
               'Principal': {'Service': 'redshift.amazonaws.com'}}],
             'Version': '2012-10-17'})
    )    
except Exception as e:
    print(e)
    
    
print("1.2 Attaching Policy")

iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME,
                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                      )['ResponseMetadata']['HTTPStatusCode']

print("1.3 Get the IAM role ARN")
roleArn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']

print(roleArn)

#### CREATE CLUSTER #####
try:
    response = redshift.create_cluster(        
        #HW
        ClusterType=DWH_CLUSTER_TYPE,
        NodeType=DWH_NODE_TYPE,
        NumberOfNodes=int(DWH_NUM_NODES),

        #Identifiers & Credentials
        DBName=DWH_DB,
        ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
        MasterUsername=DWH_DB_USER,
        MasterUserPassword=DWH_DB_PASSWORD,
        
        #Roles (for s3 access)
        IamRoles=[roleArn]  
    )
except Exception as e:
    print(e)

```
# ETL Pipepline
## Usage
First create the tables:
```bash
python create_tables.py
```
Then populate them with data:
```bash
python etl.py
```
At this point the data is populated and ready for analysis.
