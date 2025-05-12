import openai
import os
from dotenv import load_dotenv
load_dotenv()
# we can add a brief overview of what each agent does for this particular agent.

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY_LOCAL"))

def summarize_action_for_audit(agent_name: str, input_text: str, output_text):
    prompt = f"""
You are an audit assistant.
Summarize the action taken by the '{agent_name}' agent below.
Check if the action aligns with best practices (e.g., transparency, data handling, access control).
Provide output in this format:
- Summary of Action:
- User Involved:
- Risk Flags: [None / Low / Medium / High]
- Recommendations (if any):
- Timestamp:
Action Details:
Input:
\"\"\"{input_text}\"\"\"

Output:
\"\"\"{output_text}\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response['choices'][0]['message']['content']


