import json
import boto3
import time
region = 'ap-southeast-2'
ami_id = 'ami-0fa4a244ace0c16f1'
ec2 = boto3.client('ec2', region_name=region)
key_pair = 'theswartsfamily'

def start_spot_instance():

    response = ec2.request_spot_instances(
        DryRun=False,
        SpotPrice='0.05',
        InstanceCount=1,
        Type='one-time',
        LaunchSpecification={
            'ImageId': ami_id,  # replace with your AMI ID
            'InstanceType': 't2.micro',  # replace with your instance type
            'KeyName': key_pair,  # replace with your key pair name
            'SecurityGroupIds': ['sg-0c40ebf3255e1239b']
        }
    )

    return response
    
def get_bankstatement_processor_server_details(spot_instance_request_id: str) -> dict:
    #print('spot_instance_request_id: {}'.format(spot_instance_request_id))
    spot_instance_request = ec2.describe_spot_instance_requests(SpotInstanceRequestIds=[spot_instance_request_id])
    response = spot_instance_request['SpotInstanceRequests'][0]
    #print(response)
    
    return response

def start_bankstatement_processor_server() -> dict:
    spot_instance_request = start_spot_instance()
    
    #print('starting your instance: {}'.format(ami_id))
    
    request_data = spot_instance_request['SpotInstanceRequests'][0]
    
    #print(request_data)
    #print(request_data['State'])
    #print(request_data['SpotInstanceRequestId'])
    
    #print('started your instance: {}'.format(ami_id))
    return request_data
    
def wait_for_instance_to_initialise(spot_instance_request_id) -> str:
    time.sleep(2)
    server_details = get_bankstatement_processor_server_details(spot_instance_request_id)
    instance_state = server_details['State']
    #print("State: {}".format(instance_state))
    
    while (instance_state == 'pending'):
        time.sleep(2)
        server_details = get_bankstatement_processor_server_details(spot_instance_request_id)
        instance_state = server_details['State']
        #print("State: {}".format(instance_state))
    
    instance_id = server_details['InstanceId']
    #print('InstanceId: {}'.format(instance_id))
    
    return instance_id

def set_server_name(instance_id: str, server_name: str) -> None:
    ec2.create_tags(Resources=[instance_id],Tags=[{'Key': 'Name', 'Value': server_name}])

def server_initialise():
    request_data = start_bankstatement_processor_server()
    #spot_instance_request_id = 'sir-x9y6vhpg'
    spot_instance_request_id = request_data['SpotInstanceRequestId']
    instance_id = wait_for_instance_to_initialise(spot_instance_request_id)
    set_server_name(instance_id, 'Bankstatement Processor Server')

def lambda_local_run():
    server_initialise()
    

def lambda_handler(event, context):
    server_initialise()

    return {
        'statusCode': 200,
        'body': json.dumps('started your instance: {}'.format(ami_id))
    }
