from vllm import LLM, SamplingParams
import boto3
import json

s3 = boto3.client(
    "s3",
    aws_access_key_id="AKIAX2N64C7CNXNST4VH",
    aws_secret_access_key="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",
)


def list_txt_files(bucket_name):
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name)
    txt_files = [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".txt")
    ]
    return txt_files


def read_s3_files(bucket_name, file_names, user_question):
    s3 = boto3.client("s3")
    file_contents = {}
    for file_name in file_names:
        clean_file_name = file_name.rsplit(".", 1)[0]  # Remove the '.txt' extension
        obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        content = obj["Body"].read().decode("utf-8")
        modified_content = f"""<<SYS>>
Answer the user question based on the following content. Do not give explanations, just answer the question directly as if you were a function that takes user input and returns an answer.
<</SYS>>
User Question: ```{user_question}```
Content: ```{content}```
Answer: """
        file_contents[clean_file_name] = modified_content
    return file_contents


def write_to_s3(bucket_name, file_name, data):
    s3 = boto3.resource("s3")
    s3object = s3.Object(bucket_name, file_name)
    s3object.put(Body=(bytes(json.dumps(data).encode("UTF-8"))))


max_tokens = 512
sampling_params = SamplingParams(temperature=0, top_p=0.95, max_tokens=max_tokens)

bucket_name = "mymagicai-batch-test"
output_file_name = "ai_response.json"

# List .txt files in the bucket
txt_file_names = list_txt_files(bucket_name)

# Read from S3
file_contents = read_s3_files(
    bucket_name,
    txt_file_names,
    user_question="What are the industries this company operates in?",
)

llm = LLM(
    model="TheBloke/Llama-2-70B-AWQ",
    quantization="AWQ",
    tensor_parallel_size=2,
    tokenizer="hf-internal-testing/llama-tokenizer",
)

prompts = [x for x in file_contents.values()]
outputs = llm.generate(prompts, sampling_params)

output_json = []
for i, output in enumerate(outputs):
    output_dict = {"id": i, "prompt": output.prompt, "output": output.outputs[0].text}
    output_json.append(output_dict)

json_string = json.dumps(output_json)

# Write the result back to S3
write_to_s3(bucket_name, output_file_name, json_string)
