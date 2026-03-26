"""
Demo 1: Data Analyst Agent with Code Interpreter
──────────────────────────────────────────────────
An AI Foundry agent that can write and execute Python code live to perform
data analysis, statistical calculations, and mathematical reasoning.
The agent receives analytical questions and autonomously writes code to answer them.
"""

import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

AGENT_NAME = "DataAnalystAgent"

SYSTEM_INSTRUCTIONS = """You are a senior data analyst agent. You use the code interpreter
to write and execute Python code to answer analytical questions with precision.

When answering:
1. Always write Python code to compute answers — never guess or estimate.
2. Use pandas, numpy, matplotlib, or other standard libraries as needed.
3. Show your methodology: describe what you're computing and why.
4. Present results in clear, formatted tables or summaries.
5. If generating charts, describe what the chart shows.
6. Include confidence intervals or error bounds where appropriate.

You excel at: statistical analysis, time-series forecasting, Monte Carlo simulations,
optimization problems, and data transformations."""

ANALYSIS_TASKS = [
    # Task 1: Monte Carlo simulation
    (
        "Monte Carlo Portfolio Simulation",
        "Simulate a $100,000 investment portfolio with 60% stocks (12% annual return, 20% volatility) "
        "and 40% bonds (5% annual return, 8% volatility) over 10 years using 10,000 Monte Carlo simulations. "
        "Report the median final value, 5th and 95th percentile outcomes, probability of losing money, "
        "and the expected Sharpe ratio. Use correlation of 0.2 between stocks and bonds.",
    ),
    # Task 2: Statistical hypothesis test
    (
        "A/B Test Analysis",
        "An e-commerce site ran an A/B test. Control group: 4,521 visitors, 312 conversions. "
        "Treatment group: 4,648 visitors, 378 conversions. "
        "Run a chi-squared test and calculate: conversion rates for each group, "
        "relative lift, p-value, 95% confidence interval for the difference, "
        "statistical power, and the minimum sample size needed for 80% power. "
        "Determine if the result is statistically significant at alpha=0.05.",
    ),
    # Task 3: Optimization problem
    (
        "Supply Chain Optimization",
        "A company has 3 warehouses (A, B, C) supplying 4 stores (1, 2, 3, 4). "
        "Supply capacities: A=300, B=250, C=450 units. "
        "Demand: Store1=200, Store2=150, Store3=350, Store4=300 units. "
        "Transportation costs per unit: A→1=$4, A→2=$8, A→3=$1, A→4=$5, "
        "B→1=$6, B→2=$3, B→3=$7, B→4=$2, C→1=$3, C→2=$5, C→3=$4, C→4=$6. "
        "Find the optimal transportation plan that minimizes total cost using linear programming. "
        "Show the allocation matrix and total minimum cost.",
    ),
]


def ask_with_retry(openai_client, question, agent_name, max_retries=3):
    """Ask the agent a question with retry logic for rate limits."""
    for attempt in range(max_retries):
        try:
            response = openai_client.responses.create(
                input=question,
                extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
            )
            return response.output_text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 30 * (attempt + 1)
                print(f"  ⏳ Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                return f"Error: {e}"


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # Register the agent
    try:
        project_client.agents.create(
            name=AGENT_NAME,
            definition=PromptAgentDefinition(
                model=model,
                instructions=SYSTEM_INSTRUCTIONS,
                tools=[CodeInterpreterTool()],
            ),
            description="A data analyst agent with code interpreter for live computation.",
        )
    except Exception:
        pass

    # Create versioned agent with code interpreter
    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=[CodeInterpreterTool()],
        ),
        description="A data analyst agent with code interpreter for live computation.",
    )
    print(f"🔬 Data Analyst Agent created (name: {agent.name}, version: {agent.version})")
    print(f"   Model: {model} | Tool: Code Interpreter")
    print("=" * 70)

    openai_client = project_client.get_openai_client()

    for i, (title, task) in enumerate(ANALYSIS_TASKS, 1):
        print(f"\n{'─' * 70}")
        print(f"📊 Task {i}: {title}")
        print(f"{'─' * 70}")
        print(f"Prompt: {task[:100]}...")
        print()

        answer = ask_with_retry(openai_client, task, agent.name)
        print(answer)

    # Clean up
    print(f"\n{'=' * 70}")
    print("Cleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("✅ Agent deleted.")
