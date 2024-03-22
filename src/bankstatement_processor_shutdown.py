import json
import boto3
import datetime

region = "ap-southeast-2"
ami_id = "ami-070c0274040e9b3f2"
ec2 = boto3.client("ec2", region_name=region)
key_pair = "theswartsfamily"
s3_bucket = "aws-applications-and-services"
server_details_key = "bankstatement_processor/running_servers.json"
server_uptime_window = 15*60

def get_all_eligble_servers() -> list:    
    s3 = boto3.client("s3")    
    response = s3.get_object(Bucket=s3_bucket, Key=server_details_key)
    running_servers_dict = json.loads(response["Body"].read())
    eligable_servers: list = []
            
    server_instances: list = running_servers_dict["Instances"]

    for server in server_instances:        
        if (is_server_eligable(server["InstanceId"], server["LastUpdateTime"])):            
            eligable_servers.append(server)            
    
    return eligable_servers
    
def is_server_eligable(instance_id: str, server_last_update_time: float) -> bool:
    current_timestamp = datetime.datetime.now().timestamp()
    is_eligable = False
    
    if (current_timestamp - server_last_update_time > server_uptime_window):
        print("Server Instance {} is over the uptime window of {} as it was last updated at {}".format(instance_id, server_uptime_window, server_last_update_time))
        is_eligable = is_server_running(instance_id)        

    return is_eligable

def is_server_running(instance_id: str) -> bool:
    is_running = False
    
    response = ec2.describe_instances(Filters=[{"Name":"instance-id", "Values":[instance_id]}])
    is_running = len(response["Reservations"]) > 0

    return is_running

def shutdown_server(instance_id: str) -> bool:
    response = ec2.terminate_instances(InstanceIds=[instance_id])
    print("response {}".format(response))
    print("shutdown {}".format(instance_id))

def refresh_running_server_list() -> None:
    s3 = boto3.client("s3")    
    response = s3.get_object(Bucket=s3_bucket, Key=server_details_key)
    running_servers_dict = json.loads(response["Body"].read())
    server_instances: list = running_servers_dict["Instances"]
    running_servers: list = []
   
    for server in server_instances:        
        if is_server_running(server["InstanceId"]):
            running_servers.append(server)
        else:
            print("Server instance {} is not running, entry will be removed from the running list".format(server["InstanceId"]))      

    running_servers_dict["InstanceCount"] = len(running_servers)
    running_servers_dict["Instances"] = running_servers

    s3.put_object(Body=json.dumps(running_servers_dict), Bucket=s3_bucket, Key=server_details_key) 

def shutdown_all_eligble_servers() -> None:
    eligble_servers = get_all_eligble_servers()

    for server in eligble_servers:
        shutdown_server(server["InstanceId"])

    refresh_running_server_list()

def lambda_local_run() -> None:
    shutdown_all_eligble_servers()

def lambda_handler(event, context):
    shutdown_all_eligble_servers()

    return {
        "statusCode": 200,
        "body": json.dumps("started your instance: {}".format(ami_id))
    }