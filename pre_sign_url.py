import boto3

s3_client = boto3.client('s3')
url = s3_client.generate_presigned_url('get_object',
                                       Params={'Bucket': 'mymagicai-batch-test',
                                               'Key': 'object-key'},
                                       ExpiresIn = 5 * 3600)
print(url)
