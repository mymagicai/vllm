from vllm import LLM, SamplingParams
import time

prompts = []
with open('sentences.txt', 'r') as f:
    prompts = [line.strip() for line in f.readlines()]

max_tokens = 512
sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=max_tokens)

llm = LLM(model="TheBloke/Llama-2-70B-AWQ", quantization="AWQ")

start_time = time.time()
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")

end_time = time.time()
time_taken = end_time - start_time
with open("time_taken.txt", "w") as file:
    file.write(time_taken)

print(f"Time taken: {time_taken} seconds")
