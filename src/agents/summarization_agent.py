import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

# Shared memory to store the latest summary
latest_summary = {"content": ""}

def summarize_content(raw_text: str) -> str:
    prompt = f"Summarize the following meeting content into key points, actions, blockers:\n{raw_text}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a summarization assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    summary = response.choices[0].message.content.strip()
    latest_summary["content"] = summary
    return summary
