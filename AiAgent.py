from azure.ai.projects import AIProjectClient
from azure.identity import InteractiveBrowserCredential
import re
from dotenv import load_dotenv
import os

# load_dotenv()  # Loads variables from .env
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

endpoint = os.getenv("AZURE_ENDPOINT")
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
resource_group = os.getenv("AZURE_RESOURCE_GROUP")
project_name = os.getenv("AZURE_PROJECT_NAME")

# Authenticate using API key
credential = InteractiveBrowserCredential()

# Initialize the project client
# project_client = AIProjectClient(endpoint=endpoint, credential=credential)

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=credential,
    subscription_id=subscription_id,
    resource_group_name=resource_group,
    project_name=project_name
)

agent = project_client.agents.get_agent("asst_*")

thread = project_client.agents.get_thread("thread_*")

# Send a message to the agent
project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="You are a Tax Assistant model, extract tax code, amount, and percentage from the documents."
)

# Trigger the agent run
run = project_client.agents.create_and_process_run(
        agent_id="asst_*",
        thread_id="thread_j*"
)

# Get the responses
messages = project_client.agents.list_messages(thread_id="thread_jDhQCJjyZuiyrocGRqa2FnUB")

# Collect relevant responses into a list
responses = []
for message in messages.text_messages:
    if hasattr(message, 'text') and hasattr(message.text, 'value'):
        responses.append({'value': message.text.value})

# Extract and print only the first valid tax response
for resp in responses:
    value = resp['value']
    lower_value = value.lower()

    if "tax amount" in lower_value or "tax code" in lower_value or "tax percentage" in lower_value:
        tax_amount = tax_code = tax_percentage = ""

        lines = value.split('\n')
        for line in lines:
            line_lower = line.lower()
            if "tax amount" in line_lower and not tax_amount:
                tax_amount = line.strip()
            elif "tax code" in line_lower and not tax_code:
                tax_code = line.strip()
            elif "tax percentage" in line_lower and not tax_percentage:
                tax_percentage = line.strip()

        # Print and break after first match
        print("Extracted Tax Details:")
        if tax_amount:
            print(" -", tax_amount)
        if tax_code:
            print(" -", tax_code)
        if tax_percentage:
            print(" -", tax_percentage)
        break  # Stop after first unique valid response
