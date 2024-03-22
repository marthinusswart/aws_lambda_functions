import json
import boto3
import time

region = "ap-southeast-2"
ami_id = "ami-070c0274040e9b3f2"
ec2 = boto3.client("ec2", region_name=region)
key_pair = "theswartsfamily"
s3_bucket = "aws-applications-and-services"
server_details_key = "bankstatement_processor/running_servers.json"

def get_all_running_servers() -> list:    
    s3 = boto3.client("s3")    
    response = s3.get_object(Bucket=s3_bucket, Key=server_details_key)
    running_servers_dict = json.loads(response["Body"].read())
    running_servers: list = []
        
    server_instances: list = running_servers_dict["Instances"]

    for server in server_instances:        
        if (is_server_running(server["InstanceId"])):            
            running_servers.append(server)        

    running_servers_dict["InstanceCount"] = len(running_servers)
    running_servers_dict["Instances"] = running_servers

    s3.put_object(Body=json.dumps(running_servers_dict), Bucket=s3_bucket, Key=server_details_key) 
    
    return running_servers
    
def is_server_running(instance_id: str) -> bool:
    response = ec2.describe_instances(Filters=[{"Name":"instance-id", "Values":[instance_id]}])
    is_running = len(response["Reservations"]) > 0
    return is_running

def shutdown_server(instance_id: str) -> bool:
    response = ec2.terminate_instances(InstanceIds=[instance_id])
    print("response {}".format(response))
    print("shutdown {}".format(instance_id))

def shutdown_all_servers() -> None:
    running_servers = get_all_running_servers()

    for server in running_servers:
        shutdown_server(server["InstanceId"])

def lambda_local_run() -> None:
    shutdown_all_servers()

def lambda_handler(event, context):
    shutdown_all_servers()

    return {
        "statusCode": 200,
        "body": json.dumps("started your instance: {}".format(ami_id))
    }