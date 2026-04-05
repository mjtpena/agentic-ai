# Demo 1: Data Analyst Agent with Code Interpreter

This demo provisions an Azure AI Foundry account, project, and GPT-5.3 deployment, then creates a **Data Analyst Agent** that autonomously writes and executes Python code to perform statistical analysis, Monte Carlo simulations, and optimization problems.

## Prerequisites

- Azure CLI authenticated (`az login`)
- Python 3.10+
- Azure subscription with **Azure AI Account Owner**, **Contributor**, or **Cognitive Services Contributor** role

## Deploy Infrastructure

```bash
az group create --name rg-basic-agent --location eastus2

az deployment group create \
  --resource-group rg-basic-agent \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam
```

After deployment completes, note the outputs for `projectEndpoint` and `modelDeploymentName`.

## Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with the values from the deployment outputs.

## Run the Demo

```bash
pip install -r requirements.txt
python src/main.py
```

## How It Works

1. Creates a **DataAnalystAgent** with the Code Interpreter tool, which lets the agent write and execute Python code in a sandboxed environment.
2. Sends 3 progressively complex analytical tasks to the agent:
   - **Monte Carlo Portfolio Simulation** — simulates a $100K investment portfolio over 10 years with 10,000 runs
   - **A/B Test Analysis** — performs chi-squared hypothesis testing on e-commerce conversion data
   - **Supply Chain Optimization** — solves a transportation problem using linear programming
3. The agent autonomously writes Python code (using pandas, numpy, scipy, etc.) to compute precise answers.
4. Includes retry logic for rate-limited API calls.
5. Cleans up by deleting the agent version.

## Key Capabilities

| Capability | Description |
| --- | --- |
| **Code Interpreter** | Agent writes and executes Python code in a sandboxed environment |
| **Statistical Analysis** | Chi-squared tests, confidence intervals, statistical power |
| **Monte Carlo Simulation** | Portfolio modeling with correlated asset returns |
| **Linear Programming** | Transportation cost optimization with supply/demand constraints |

## Expected Output

```
🔬 Data Analyst Agent created (name: DataAnalystAgent, version: 1)
   Model: gpt-5-3-chat | Tool: Code Interpreter
======================================================================

──────────────────────────────────────────────────────────────────────
📊 Task 1: Monte Carlo Portfolio Simulation
──────────────────────────────────────────────────────────────────────
Prompt: Simulate a $100,000 investment portfolio with 60% stocks ...

[Agent writes and executes Python code, returns statistical results
 including median final value, percentile outcomes, Sharpe ratio]

──────────────────────────────────────────────────────────────────────
📊 Task 2: A/B Test Analysis
──────────────────────────────────────────────────────────────────────
[Agent performs chi-squared test, calculates p-value, confidence intervals]

──────────────────────────────────────────────────────────────────────
📊 Task 3: Supply Chain Optimization
──────────────────────────────────────────────────────────────────────
[Agent solves linear programming problem, shows allocation matrix]

======================================================================
Cleaning up...
✅ Agent deleted.
```

## Clean Up

```bash
az group delete --name rg-basic-agent --yes --no-wait
```
