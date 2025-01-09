import json
import time
import boto3

S3 = boto3.client('s3')
BUCKET = 'calc-project'

def getIsinstanceErrorString(num: any) -> str:
    return f'{num} should be integer, but got {type(num)}'

def handleGetRoot() -> dict:
    results = {}
    response = S3.list_objects(Bucket=BUCKET)
    for content in response['Contents']:
        curr_file_name = content['Key']
        curr_response = S3.get_object(Bucket=BUCKET, Key=curr_file_name)
        results[curr_file_name] = curr_response['Body'].read().decode('utf-8')

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }

def handleGetCalc() -> dict:
    res = {
        "number_1": "int",
        "number_2": "int",
        "operation": "str, withing {'+', '-', '*', '/'}"
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(res)
    }

def handlePostCalc(event: dict) -> dict:
    body = json.loads(event['body'])
    num1 = body['number_1']
    num2 = body['number_2']
    op = body['operation']

    if not isinstance(num1, int):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': getIsinstanceErrorString(num1)})
        }
    elif not isinstance(num2, int):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': getIsinstanceErrorString(num2)})
        }

    if op == '+':
        res = num1 + num2
    elif op == '-':
        res = num1 - num2
    elif op == '*':
        res = num1 * num2
    elif op == '/':
        if num2 == 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Division by zero'})
            }
        res = num1 / num2
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid operation')
        }
    
    result = f'{num1} {op} {num2} = {res}'
    S3.put_object(
        Bucket=BUCKET,
        Key=f'{time.time()}',
        Body=result
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'result': result})
    }

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']

    if path == '/':
        return handleGetRoot()
    elif path == '/calc':
        if method == 'GET':
            return handleGetCalc()
        elif method == 'POST':
            return handlePostCalc(event)
