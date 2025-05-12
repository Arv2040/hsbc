import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY_LOCAL"))

AUDIT_LOG_FILE = "agent_audit_logs.json"

def summarize_action_for_audit(agent_name: str, input_text: str, output_text: str):
   
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
    
    audit_summary = response.choices[0].message.content
    
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "input": input_text,
        "output": output_text,
        "audit_summary": audit_summary
    }
    
   
    try:
        with open(AUDIT_LOG_FILE, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = {}
    
    
    if f"{agent_name}_audit" not in logs:
        logs[f"{agent_name}_audit"] = []
    
    logs[f"{agent_name}_audit"].append(log_entry)
    
    
    with open(AUDIT_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return audit_summary