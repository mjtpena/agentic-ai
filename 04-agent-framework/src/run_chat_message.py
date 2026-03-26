"""
Demo 4c: Concurrent Multi-Agent Debate with Structured Messages
───────────────────────────────────────────────────────────────
Two agents with opposing viewpoints debate a topic concurrently,
then a Judge agent synthesizes the verdict.

Uses ConcurrentBuilder for parallel execution + SequentialBuilder
to chain the debate into a final judgment.

Architecture:
  ┌─────────────┐
  │ User Topic   │
  └──────┬───────┘
         │
    ┌────┴────┐
    ▼         ▼        (concurrent)
  [Bull]   [Bear]
    │         │
    └────┬────┘
         ▼
      [Judge]          (sequential)
         │
         ▼
   Final Verdict
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework import (
    ChatMessage,
    TextContent,
    Role,
    SequentialBuilder,
    ConcurrentBuilder,
)
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

# Bull (optimist) agent
bull = client.create_agent(
    name="BullAnalyst",
    instructions="""You are a bullish technology analyst known for identifying opportunities.
You see the positive potential in technology trends.
Present 3-4 compelling arguments FOR the proposition, backed by data and logic.
Be persuasive but intellectually honest. Acknowledge risks briefly.
Keep your response under 200 words. Start with "🟢 BULL CASE:".""",
)

# Bear (skeptic) agent
bear = client.create_agent(
    name="BearAnalyst",
    instructions="""You are a bearish, skeptical analyst known for identifying risks.
You challenge hype and find the hidden dangers.
Present 3-4 compelling arguments AGAINST the proposition, backed by data and logic.
Be persuasive but intellectually honest. Acknowledge potential upside briefly.
Keep your response under 200 words. Start with "🔴 BEAR CASE:".""",
)

# Judge agent — synthesizes both cases
judge = client.create_agent(
    name="JudgeAgent",
    instructions="""You are an impartial senior judge evaluating both sides of a debate.
You've received arguments from both a Bull and Bear analyst.

Your verdict must include:
1. **Verdict**: One sentence — which side has the stronger argument and why
2. **Strongest Bull Point**: The most compelling optimistic argument
3. **Strongest Bear Point**: The most compelling skeptical argument
4. **Consensus View**: What a balanced investor should actually do
5. **Confidence Level**: How confident you are in this verdict (1-10)

Be fair, cite specific arguments from both sides. Format with markdown.""",
)

DEBATE_TOPIC = (
    "AI agents will replace 50% of knowledge worker tasks within 3 years. "
    "Consider: enterprise software companies are rapidly shipping agent features, "
    "Microsoft, Google, and Anthropic all have agent frameworks, "
    "but regulatory uncertainty, hallucination risks, and organizational inertia remain."
)


async def main():
    print("⚖️  Multi-Agent Debate: Bull vs Bear → Judge")
    print("=" * 70)
    print(f"Topic: {DEBATE_TOPIC[:80]}...")
    print(f"Model: {deployment}")
    print(f"Architecture: [Bull] + [Bear] (concurrent) → [Judge] (sequential)")
    print("=" * 70)

    # Phase 1: Run bull and bear concurrently
    print("\n📢 Phase 1: Bull and Bear analyzing concurrently...\n")

    bull_task = asyncio.create_task(bull.run(DEBATE_TOPIC))
    bear_task = asyncio.create_task(bear.run(DEBATE_TOPIC))
    bull_result, bear_result = await asyncio.gather(bull_task, bear_task)

    print(bull_result.text)
    print()
    print(bear_result.text)

    # Phase 2: Judge synthesizes both arguments
    print(f"\n{'─' * 70}")
    print("⚖️  Phase 2: Judge deliberating...\n")

    judge_input = ChatMessage(
        role=Role.USER,
        contents=[
            TextContent(
                text=f"Here are the two analyst arguments on the topic: '{DEBATE_TOPIC}'\n\n"
                f"--- BULL ANALYST ---\n{bull_result.text}\n\n"
                f"--- BEAR ANALYST ---\n{bear_result.text}\n\n"
                f"Please deliver your verdict."
            ),
        ],
    )

    verdict = await judge.run(judge_input)
    print(verdict.text)

    print(f"\n{'=' * 70}")
    print("✅ Debate complete — 3 agents collaborated (2 concurrent + 1 sequential).")


asyncio.run(main())
