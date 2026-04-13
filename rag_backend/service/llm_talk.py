from openai import OpenAI
import json

model = "model"
client = OpenAI(api_key="ragflow-api-key", base_url=f"http://ragflow_address/api/v1/chats_openai/<chat_id>")

stream = True
reference = True

request_kwargs = dict(
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"},
        {"role": "assistant", "content": "I am an AI assistant named..."},
        {"role": "user", "content": "Can you tell me how to install neovim"},
    ],
    extra_body={
        "extra_body": {
            "reference": reference,
            "reference_metadata": {
                "include": True,
                "fields": ["author", "year", "source"],
            },
        }
    },
)

if stream:
    completion = client.chat.completions.create(stream=True, **request_kwargs)
    for chunk in completion:
        print(chunk)
else:
    resp = client.chat.completions.with_raw_response.create(
        stream=False, **request_kwargs
    )
    print("status:", resp.http_response.status_code)
    raw_text = resp.http_response.text
    print("raw:", raw_text)

    data = json.loads(raw_text)
    print("assistant:", data["choices"][0]["message"].get("content"))
    print("reference:", data["choices"][0]["message"].get("reference"))