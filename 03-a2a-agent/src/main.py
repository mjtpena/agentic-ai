import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    A2ATool,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"]

AGENT_NAME = "A2AOrchestrator"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # Configure the A2A tool — requires a project connection to an external A2A server
    tool = A2ATool(
        project_connection_id=os.environ["A2A_PROJECT_CONNECTION_ID"],
    )

    # Register the agent name (ignore if already exists)
    try:
        project_client.agents.create(
            name=AGENT_NAME,
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant that can delegate tasks to a remote agent.",
                tools=[tool],
            ),
        )
    except Exception:
        pass

    # Create a versioned agent definition
    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model,
            instructions="You are a helpful assistant that can delegate tasks to a remote agent. "
            "When a user asks a question, use the connected agent tool to get information "
            "from the secondary agent and relay the response back to the user.",
            tools=[tool],
        ),
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    # Get an authenticated OpenAI client
    openai_client = project_client.get_openai_client()

    # Interactive chat with streaming
    user_input = input("Enter your question (e.g., 'What can the secondary agent do?'): \n")

    stream_response = openai_client.responses.create(
        stream=True,
        tool_choice="required",
        input=user_input,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    for event in stream_response:
        if event.type == "response.created":
            print(f"Response created with ID: {event.response.id}")
        elif event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "response.text.done":
            print("\n\nResponse complete!")
        elif event.type == "response.output_item.done":
            item = event.item
            if item.type == "remote_function_call":
                print(f"Call ID: {getattr(item, 'call_id')}")
                print(f"Label: {getattr(item, 'label')}")
        elif event.type == "response.completed":
            print(f"\nFull response: {event.response.output_text}")

    # Clean up
    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted.")
