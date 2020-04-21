import json
import boto3
import numpy as np
import io

# endpoint name defined in Jupyter notebook when the endpoint is created.
# You will need it to call the endpoint to do a new prediction.
endpoint_name = "<your endpoint>"

def lambda_handler(event, context):
    
    # reshape the data to fit the model
    data = np.array(event)
    data = data.reshape(1,data.shape[0]*data.shape[1])
    data = data.tolist() 

    # call the Sagemaker endpoint
    client = boto3.client("runtime.sagemaker")
    response = client.invoke_endpoint(EndpointName=endpoint_name, Body=json.dumps(data))
    response_body = response['Body']
    bstr = response_body.read().decode("utf-8") 
    
    # check the prediction result
    dbstr = eval(bstr)
    output_list = dbstr["outputs"]["score"]["floatVal"]
    y_class = np.array(output_list).argmax(axis=-1)
    print(y_class)

    # Send the prediction result back to our field sof sensor. 
    iot = boto3.client('iot-data', region_name='eu-central-1')

    # Topic defined here must be the same as the subscribed topic in Node-RED:
    response = iot.publish(topic='status/mls160/', qos=1, payload=str(y_class))
    
    # As an example: If class is 2, then send message to mobile phone. Be sure to have the policy permission set. 
    if(y_class == 2): 
        
        # AWS SNS client
        sns = boto3.client('sns', region_name='eu-west-1') # SNS dont support every region
        number = "<cellphone numer>"
        sns.publish(PhoneNumber = number, Message="Hello this is a message!")
