"""
Demo 4b: Streaming Agent with Custom Tools (Function Calling)
─────────────────────────────────────────────────────────────
An Agent Framework agent with custom Python functions as tools.
The agent can call local functions to compute results, showing
the function-calling loop with streamed output.

Tools:
  • calculate_compound_interest — financial calculation
  • analyze_sentiment — text analysis with scoring
  • generate_report_id — UUID generation for tracking
"""

import asyncio
import os
import uuid
from typing import Annotated
from pydantic import Field
from dotenv import load_dotenv
from agent_framework import ai_function
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

load_dotenv()


@ai_function
def calculate_compound_interest(
    principal: Annotated[float, Field(description="Initial investment amount in dollars")],
    annual_rate: Annotated[float, Field(description="Annual interest rate as a percentage (e.g. 7.5)")],
    years: Annotated[int, Field(description="Number of years to compound")],
    compounds_per_year: Annotated[int, Field(description="Number of times interest compounds per year (e.g. 12 for monthly)")] = 12,
) -> str:
    """Calculate compound interest and return detailed breakdown."""
    r = annual_rate / 100
    n = compounds_per_year
    amount = principal * (1 + r / n) ** (n * years)
    interest = amount - principal
    return (
        f"Principal: ${principal:,.2f} | Rate: {annual_rate}% | Period: {years} years | "
        f"Compounding: {n}x/year\n"
        f"Final Amount: ${amount:,.2f} | Total Interest Earned: ${interest:,.2f} | "
        f"Return: {(amount/principal - 1)*100:.1f}%"
    )


@ai_function
def analyze_sentiment(
    text: Annotated[str, Field(description="The text to analyze for sentiment")],
) -> str:
    """Analyze text sentiment using keyword-based scoring."""
    positive = ["good", "great", "excellent", "amazing", "love", "best", "fantastic", "happy", "wonderful", "profit", "growth", "success", "innovative"]
    negative = ["bad", "terrible", "awful", "hate", "worst", "poor", "fail", "loss", "risk", "decline", "concern", "threat"]
    words = text.lower().split()
    pos = sum(1 for w in words if any(p in w for p in positive))
    neg = sum(1 for w in words if any(n in w for n in negative))
    total = pos + neg or 1
    score = (pos - neg) / total
    label = "POSITIVE" if score > 0.2 else "NEGATIVE" if score < -0.2 else "NEUTRAL"
    return f"Sentiment: {label} (score: {score:+.2f}) | Positive signals: {pos} | Negative signals: {neg}"


@ai_function
def generate_report_id() -> str:
    """Generate a unique report tracking ID."""
    return f"RPT-{uuid.uuid4().hex[:8].upper()}"


agent = AzureOpenAIChatClient(
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    credential=AzureCliCredential(),
).create_agent(
    name="FinancialAdvisor",
    instructions="""You are a senior financial advisor with analytical tools at your disposal.
When a client asks for investment advice:
1. Generate a report ID for tracking
2. Run the financial calculations using your tools
3. Analyze the sentiment of any market descriptions provided
4. Provide a comprehensive, data-backed recommendation

Always show your work — reference the tool outputs in your response.""",
    tools=[calculate_compound_interest, analyze_sentiment, generate_report_id],
)

PROMPT = """I'm considering two investment options:
Option A: $50,000 in a high-yield savings account at 5.2% APY compounded monthly for 10 years.
Option B: $50,000 in an index fund averaging 9.8% annual return compounded quarterly for 10 years.

The market outlook headline reads: "Strong growth expected despite concerns about inflation risk,
but innovative AI companies show excellent profit potential and amazing revenue growth."

Please generate a report, calculate both options, analyze the market sentiment, and give me
your recommendation with the numbers."""


async def main():
    print("💰 Financial Advisor Agent with Custom Tools")
    print("=" * 70)
    print(f"Model: {os.environ['AZURE_OPENAI_DEPLOYMENT_NAME']}")
    print(f"Tools: calculate_compound_interest, analyze_sentiment, generate_report_id")
    print("=" * 70)
    print(f"\nClient: {PROMPT[:80]}...\n")
    print("Advisor (streaming):\n")

    async for update in agent.run_stream(PROMPT):
        if update.text:
            print(update.text, end="", flush=True)
    print()
    print(f"\n{'=' * 70}")
    print("✅ Streaming complete — tools were called inline during generation.")


asyncio.run(main())
