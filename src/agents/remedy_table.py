
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd
import streamlit as st
import requests
import json
import io

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def generate_remediation_suggestions(mismatched_rules: list) -> dict:
    """
    Generate remediation suggestions for mismatched compliance rules using Azure OpenAI.
    
    Args:
        mismatched_rules: List of dictionaries containing mismatched policies
        
    Returns:
        Dictionary with:
        - 'status': 'success' or 'error'
        - 'remedies': List of remediation suggestions (if successful)
        - 'error': Error message (if error occurred)
    """
    try:
        # Prepare the input text for compliance analysis
        policy_texts = [rule.get("AI GENRATED POLICIES", "") for rule in mismatched_rules]
        numbered_policies = "\n".join([f"{i+1}. {policy}" for i, policy in enumerate(policy_texts)])
        
        prompt = f"""
As a Compliance Expert, analyze these mismatched policies and generate specific remedies.
Return a JSON array where each object has:
- "mismatched_policy": (the original policy text)
- "remedy": (specific action to fix this compliance issue)

Policies:
{numbered_policies}

Respond ONLY with valid JSON in this exact format:
[
    {{
        "mismatched_policy": "policy text here",
        "remedy": "specific remedy here"
    }},
    ...
]
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a compliance expert that provides precise remediation suggestions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000
        )

        remedies_text = response.choices[0].message.content.strip()
        
        # Clean and validate the JSON response
        remedies_text = remedies_text.replace("json", "").replace("", "").strip()
        remedies_data = json.loads(remedies_text)
        
        # Validate the structure
        if not isinstance(remedies_data, list):
            raise ValueError("Response is not a JSON array")
            
        for item in remedies_data:
            if not isinstance(item, dict) or 'mismatched_policy' not in item or 'remedy' not in item:
                raise ValueError("Invalid item structure in response")
        
        return {
            "status": "success",
            "remedies": remedies_data
        }
        
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error": f"JSON parsing failed: {str(e)}",
            "response": remedies_text
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


