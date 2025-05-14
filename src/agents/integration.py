# -----------------------Requires ecternal APIS like Jira, Sharepoint, Slack , etc-------------------------


# import os
# import requests
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
# from dotenv import load_dotenv
# import openai

# load_dotenv()

# # OpenAI Azure Setup
# openai.api_type = os.getenv("OPENAI_API_TYPE_LOCAL")
# openai.api_base = os.getenv("OPENAI_API_BASE_LOCAL")
# openai.api_version = os.getenv("OPENAI_API_VERSION_LOCAL")
# openai.api_key = os.getenv("OPENAI_API_KEY_LOCAL")

# def create_jira_ticket(summary, description):
#     url = f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/issue"
#     auth = (os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
#     headers = {"Accept": "application/json", "Content-Type": "application/json"}

#     payload = {
#         "fields": {
#             "project": {"key": "PROJ"},
#             "summary": summary,
#             "description": description,
#             "issuetype": {"name": "Task"}
#         }
#     }

#     response = requests.post(url, auth=auth, json=payload, headers=headers)
#     response.raise_for_status()
#     return response.json()

# def push_to_sharepoint(title, content):
#     # Placeholder - implement real Microsoft Graph logic
#     return f"Spec '{title}' pushed to SharePoint."

# def notify_slack(message):
#     client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
#     try:
#         result = client.chat_postMessage(
#             channel=os.getenv("SLACK_CHANNEL"),
#             text=message
#         )
#         return result.data
#     except SlackApiError as e:
#         raise Exception(f"Slack API Error: {e.response['error']}")

# def generate_summary_from_openai(prompt):
#     try:
#         response = openai.ChatCompletion.create(
#             engine="gpt-4",  # Replace with your Azure deployment name
#             messages=[
#                 {"role": "system", "content": "You are an assistant that summarizes integration tasks."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7
#         )
#         return response["choices"][0]["message"]["content"]
#     except Exception as e:
#         raise Exception(f"OpenAI API Error: {str(e)}")
