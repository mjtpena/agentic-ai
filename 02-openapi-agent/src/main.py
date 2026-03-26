"""
Demo 2: Travel Intelligence Agent — Multi-API Orchestration
────────────────────────────────────────────────────────────
An AI Foundry agent that orchestrates 3 live APIs simultaneously:
  • Weather API (wttr.in) — real-time weather conditions
  • Countries API (restcountries.com) — country facts, languages, currencies
  • Exchange Rate API (open.er-api.com) — live currency conversion rates

The agent synthesizes data from all 3 sources into comprehensive travel briefings.
"""

import os
import time
import jsonref
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    OpenApiAgentTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

AGENT_NAME = "TravelIntelligenceAgent"

SYSTEM_INSTRUCTIONS = """You are an elite travel intelligence analyst. You have access to three
real-time data sources via APIs:

1. **Weather API** — current conditions, temperature, humidity, wind for any city
2. **Countries API** — population, languages, currencies, region, timezone, borders
3. **Exchange Rate API** — live currency exchange rates from any base currency

When generating a travel briefing:
- ALWAYS call all relevant APIs to ground your response in real data
- Present information in a structured, professional format with sections
- Include practical travel advice based on the actual data
- Convert prices using real exchange rates
- Mention language tips, cultural notes, and weather-appropriate packing advice
- Use emoji sparingly for section headers to make it scannable
- End with a "Quick Facts" summary table

You are thorough, data-driven, and focused on actionable intelligence."""


def load_spec(filename):
    """Load and resolve an OpenAPI spec from the assets directory."""
    spec_path = os.path.join(os.path.dirname(__file__), "assets", filename)
    with open(spec_path, "r") as f:
        return jsonref.loads(f.read())


def ask_with_retry(openai_client, question, agent_name, max_retries=5):
    """Ask the agent with retry for rate limits."""
    for attempt in range(max_retries):
        try:
            response = openai_client.responses.create(
                input=question,
                extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
            )
            return response.output_text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 60 * (attempt + 1)
                print(f"  ⏳ Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                return f"Error: {e}"


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # Load all 3 OpenAPI specs
    weather_spec = load_spec("weather_openapi.json")
    countries_spec = load_spec("countries_openapi.json")
    exchange_spec = load_spec("exchange_openapi.json")

    # Configure the 3 API tools
    tools = [
        OpenApiAgentTool(
            openapi=OpenApiFunctionDefinition(
                name="weather",
                description="Get real-time weather conditions for any city worldwide",
                spec=weather_spec,
                auth=OpenApiAnonymousAuthDetails(),
            ),
        ),
        OpenApiAgentTool(
            openapi=OpenApiFunctionDefinition(
                name="countries",
                description="Get detailed country information: capital, population, languages, currencies, region, timezones, and borders",
                spec=countries_spec,
                auth=OpenApiAnonymousAuthDetails(),
            ),
        ),
        OpenApiAgentTool(
            openapi=OpenApiFunctionDefinition(
                name="exchange_rates",
                description="Get live currency exchange rates from any base currency to all world currencies",
                spec=exchange_spec,
                auth=OpenApiAnonymousAuthDetails(),
            ),
        ),
    ]

    # Register the agent
    try:
        project_client.agents.create(
            name=AGENT_NAME,
            definition=PromptAgentDefinition(
                model=model,
                instructions=SYSTEM_INSTRUCTIONS,
                tools=tools,
            ),
            description="Multi-API travel intelligence agent with weather, countries, and exchange rates.",
        )
    except Exception:
        pass

    # Create versioned agent
    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=tools,
        ),
        description="Multi-API travel intelligence agent with weather, countries, and exchange rates.",
    )
    print(f"🌍 Travel Intelligence Agent created (name: {agent.name}, version: {agent.version})")
    print(f"   Model: {model} | Tools: Weather API, Countries API, Exchange Rate API")
    print("=" * 70)

    openai_client = project_client.get_openai_client()

    # Travel briefing requests
    briefings = [
        (
            "Tokyo Travel Briefing",
            "I'm an Australian traveller planning a trip to Tokyo, Japan next week. "
            "Generate a comprehensive travel intelligence briefing. Check the current weather "
            "in Tokyo, get me country facts about Japan (languages, currency, timezone), "
            "and fetch the AUD to JPY exchange rate so I know how much my money is worth. "
            "Include practical tips for an Australian visiting Japan.",
        ),
        (
            "Quick Paris Check",
            "Quick check: what's the weather in Paris right now, and what's the USD to EUR exchange rate? "
            "Give me a 3-bullet summary.",
        ),
    ]

    for i, (title, prompt) in enumerate(briefings, 1):
        print(f"\n{'─' * 70}")
        print(f"🗺️  Briefing {i}: {title}")
        print(f"{'─' * 70}")
        print(f"Request: {prompt[:80]}...\n")

        if i > 1:
            time.sleep(60)  # pause between briefings to respect rate limits

        answer = ask_with_retry(openai_client, prompt, agent.name)
        print(answer)

    # Clean up
    print(f"\n{'=' * 70}")
    print("Cleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("✅ Agent deleted.")
