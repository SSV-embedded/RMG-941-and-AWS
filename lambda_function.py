import json
import boto3
import numpy as np
import io

endpoint_name = "ssv-sagemaker-2020-03-26-10-30-25"

def lambda_handler(event, context):
    
    data = np.array(event)
    data = data.reshape(1,data.shape[0]*data.shape[1])
    data = data.tolist() 

    client = boto3.client("runtime.sagemaker")
    response = client.invoke_endpoint(EndpointName=endpoint_name, Body=json.dumps(data))
    response_body = response['Body']
    bstr = response_body.read().decode("utf-8") 
    
    dbstr = eval(bstr)
    output_list = dbstr["outputs"]["score"]["floatVal"]
    

    y_class = np.array(output_list).argmax(axis=-1)
    print(y_class)

    # Send the prediction result back to our field sof sensor. 
    iot = boto3.client('iot-data', region_name='eu-central-1')
    response = iot.publish(topic='status/mls160/', qos=1, payload=str(y_class))
    
    # As an example: If class is 2, then send message to mobile phone. Be sure to have the policy permission set. 
    if(y_class == 2): 
        
        sns = boto3.client('sns', region_name='eu-west-1')
        number = "<cellphone numer>"
        sns.publish(PhoneNumber = number, Message="Machine with MLS160 and RMG941 has reported an error")
