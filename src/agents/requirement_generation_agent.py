import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from agents.summarization_agent import latest_summary  

load_dotenv()


client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def generate_requirements() -> str:
    if not latest_summary["content"]:
        return "No summary available. Please run the summarization agent first."

    prompt = (
        f"Based on the following summary, generate detailed business requirements. "
        f"Follow this format:\n\n"
        f"As a [user], I want to [action], so that [benefit].\n"
        f"Include acceptance criteria, roles, and expected behavior.\n\n"
        f"Summary:\n{latest_summary['content']}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a requirements generation assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content.strip()
