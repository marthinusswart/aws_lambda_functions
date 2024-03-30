import json
import boto3

region = "ap-southeast-2"
ec2 = boto3.client("ec2", region_name=region)
key_pair = "theswartsfamily"
s3_bucket = "aws-applications-and-services"
server_details_key = "bankstatement_processor/running_servers.json"

def get_all_eligble_servers() -> list:    
    s3 = boto3.client("s3")    
    response = s3.get_object(Bucket=s3_bucket, Key=server_details_key)
    running_servers_dict = json.loads(response["Body"].read())
    eligable_servers: list = []
            
    server_instances: list = running_servers_dict["Instances"]

    for server in server_instances:        
        if (is_server_eligable(server["InstanceId"])):            
            eligable_servers.append(server)            
    
    return eligable_servers

def is_server_eligable(instance_id: str) -> bool:    
    is_eligable = False
    
    is_eligable = is_server_running(instance_id)        

    return is_eligable

def is_server_running(instance_id: str) -> bool:
    is_running = False
    
    response = ec2.describe_instances(Filters=[{"Name":"instance-id", "Values":[instance_id]}])
    
    for server in response["Reservations"]:
        server_instance = server["Instances"][0]
        server_state = server_instance["State"]        
        is_running = server_state["Code"] == 16

    return is_running

def call_bankstatement_processor_startup_lambda_func() -> str:
    lambda_client = boto3.client("lambda")

    response = lambda_client.invoke(FunctionName="start_bankstatement_processor_server", InvocationType="RequestResponse", Payload="{}")

    response_payload = json.load(response["Payload"])

    return response_payload

def validate_server_is_running() -> bool:
    server_is_running = False

    all_eligble_servers = get_all_eligble_servers()
    if len(all_eligble_servers) == 0:
        call_bankstatement_processor_startup_lambda_func();
        server_is_running = True
    else:
        server_is_running = True

    return server_is_running

def lambda_local_run() -> None:
    validate_server_is_running()

def lambda_handler(event, context):
    server_is_running = validate_server_is_running()

    return {
        "statusCode": 200,
        "body": json.dumps("A Bankstatement Processor Server is running: {}".format(server_is_running))
    }