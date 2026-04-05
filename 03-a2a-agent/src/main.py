"""
Demo 3: A2A Orchestrator Agent — Agent-to-Agent Communication
──────────────────────────────────────────────────────────────
An AI Foundry orchestrator agent that delegates tasks to a remote
A2A-compatible agent via the Agent-to-Agent protocol.

The orchestrator receives user questions and routes them to a connected
remote agent, streaming the response back delta-by-delta as it arrives.

Requires:
  • A running remote A2A-compatible agent endpoint
  • An A2A project connection configured in the Foundry project
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    A2ATool,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

AGENT_NAME = "A2AOrchestrator"

SYSTEM_INSTRUCTIONS = """You are an orchestrator agent that coordinates with a remote specialist agent
via the Agent-to-Agent (A2A) protocol.

When a user asks a question:
1. Analyze the request and determine what information the remote agent can provide.
2. Delegate the task to the connected remote agent using your A2A tool.
3. Synthesize the remote agent's response into a clear, well-structured answer.
4. If the remote agent cannot fully answer, clearly state what was and wasn't covered.

You excel at: task decomposition, delegation, and synthesizing multi-source responses.
Always be transparent about which information came from the remote agent."""

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
                instructions=SYSTEM_INSTRUCTIONS,
                tools=[tool],
            ),
            description="An orchestrator agent that delegates tasks via A2A protocol.",
        )
    except Exception:
        pass

    # Create a versioned agent definition
    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=[tool],
        ),
        description="An orchestrator agent that delegates tasks via A2A protocol.",
    )
    print(f"🔗 A2A Orchestrator created (name: {agent.name}, version: {agent.version})")
    print(f"   Model: {model} | Tool: A2A (remote agent)")
    print("=" * 70)

    # Get an authenticated OpenAI client
    openai_client = project_client.get_openai_client()

    # Interactive chat with streaming
    user_input = input("\nEnter your question (e.g., 'What can the remote agent do?'):\n> ")

    print()
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
                print(f"  📡 Remote call — ID: {getattr(item, 'call_id')}, Label: {getattr(item, 'label')}")
        elif event.type == "response.completed":
            print(f"\nFull response: {event.response.output_text}")

    # Clean up
    print(f"\n{'=' * 70}")
    print("Cleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("✅ Agent deleted.")
