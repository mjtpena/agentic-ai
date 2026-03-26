"""
Demo 4a: Multi-Agent Research Pipeline (Sequential Workflow)
─────────────────────────────────────────────────────────────
A 3-agent sequential pipeline using Microsoft Agent Framework:

  1. Research Agent (with Web Search) — gathers raw data from the internet
  2. Analyst Agent — synthesizes research into structured insights
  3. Executive Briefing Agent — produces a polished C-suite summary

Uses SequentialBuilder to orchestrate the agents in order,
with each agent building on the previous agent's output.
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework import SequentialBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
deployment = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
credential = AzureCliCredential()

client = AzureOpenAIChatClient(
    endpoint=endpoint,
    deployment_name=deployment,
    credential=credential,
)

# Agent 1: Researcher — deep domain expert
researcher = client.create_agent(
    name="ResearchAgent",
    instructions="""You are a senior research analyst specializing in AI and technology markets.
Your job is to produce a comprehensive research dossier on the given topic.

When researching:
- Cover multiple angles: market data, key players, technology trends, adoption patterns
- Include specific numbers, percentages, and timeframes where possible
- Organize findings into clear categories: Market Overview, Key Players, Technology Landscape, Adoption Trends
- Flag uncertainties and emerging disruptions
- Focus on what's happening RIGHT NOW in the industry

Output your findings as a structured research dossier with clear sections and data points.""",
)

# Agent 2: Analyst — synthesizes research into insights
analyst = client.create_agent(
    name="AnalystAgent",
    instructions="""You are a strategic analyst at a top consulting firm. You receive raw
research data from the Research Agent and must synthesize it into actionable insights.

Your analysis must include:
1. **Key Findings** — the 3-5 most important data points
2. **Trend Analysis** — what direction is this moving and why
3. **Competitive Landscape** — who are the key players and their positions
4. **Risk Assessment** — potential threats and uncertainties (rate High/Medium/Low)
5. **Opportunities** — actionable opportunities identified from the data

Be quantitative wherever possible. Challenge assumptions. Identify what the data
does NOT tell us (knowledge gaps).""",
)

# Agent 3: Executive Briefing — produces polished output
briefer = client.create_agent(
    name="ExecutiveBriefingAgent",
    instructions="""You are the Chief of Staff preparing a briefing for the CEO. You receive
an analyst's report and must distill it into an executive-ready briefing.

Format requirements:
- Start with a 2-sentence "Bottom Line Up Front" (BLUF)
- Include a decision matrix or recommendation table
- Use bullet points, not paragraphs
- Every claim must reference data from the analysis
- End with "Recommended Actions" (numbered, prioritized)
- Total length: concise but complete — aim for quality over quantity
- Use markdown formatting for emphasis and structure

This briefing will be presented to a board of directors.""",
)

# Build the sequential 3-agent pipeline
workflow = SequentialBuilder().participants([researcher, analyst, briefer]).build()

RESEARCH_TOPIC = (
    "Analyze the current state of AI Agent frameworks and orchestration platforms in 2026. "
    "Who are the major players (Microsoft, Google, Anthropic, OpenAI, open-source)? "
    "What are the emerging standards (A2A, MCP)? What's the market size and growth trajectory? "
    "Which industries are adopting AI agents fastest?"
)


async def main():
    print("🔬 Multi-Agent Research Pipeline")
    print("=" * 70)
    print(f"Topic: {RESEARCH_TOPIC[:80]}...")
    print(f"Pipeline: ResearchAgent → AnalystAgent → ExecutiveBriefingAgent")
    print(f"Model: {deployment}")
    print("=" * 70)

    print("\n⏳ Pipeline executing (3 agents in sequence)...\n")

    result = await workflow.run(RESEARCH_TOPIC)

    # Extract conversation from the workflow result
    outputs = result.get_outputs()
    for output in outputs:
        if hasattr(output, '__iter__') and not isinstance(output, str):
            for item in output:
                if hasattr(item, 'contents'):
                    for content in item.contents:
                        if hasattr(content, 'text') and item.role.value == "assistant":
                            print(content.text)
                elif hasattr(item, 'text'):
                    print(item.text)
        elif hasattr(output, 'text'):
            print(output.text)
        elif isinstance(output, str):
            print(output)

    print(f"\n{'=' * 70}")
    print("✅ Pipeline complete — 3 agents collaborated to produce this briefing.")


asyncio.run(main())
