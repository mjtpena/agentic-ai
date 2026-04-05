# Demo 4: Multi-Agent Orchestration with Agent Framework

This demo provisions an Azure OpenAI resource and GPT-5.2 deployment, then uses the **Microsoft Agent Framework** SDK to demonstrate three advanced orchestration patterns: sequential pipelines, streaming with custom tools, and concurrent debate.

## Prerequisites

- Azure CLI authenticated (`az login`)
- Python 3.10+
- **Cognitive Services OpenAI User** or **Cognitive Services OpenAI Contributor** role on the Azure OpenAI resource

## Deploy Infrastructure

```bash
az group create --name rg-agent-framework --location eastus2

az deployment group create \
  --resource-group rg-agent-framework \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam
```

After deployment, note the `endpoint` and `modelDeploymentName` outputs.

## Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with the deployment output values.

## Run the Demos

```bash
pip install -r requirements.txt
```

### Sequential Pipeline — Multi-Agent Research

```bash
python src/run_basic.py
```

A 3-agent sequential pipeline using `SequentialBuilder`:

1. **ResearchAgent** — gathers raw data on a topic (AI agent frameworks in 2026)
2. **AnalystAgent** — synthesizes research into structured insights with risk assessment
3. **ExecutiveBriefingAgent** — produces a polished C-suite summary with recommendations

Each agent builds on the previous agent's output, passing context forward through the pipeline.

### Streaming with Custom Function Tools

```bash
python src/run_streaming.py
```

A **FinancialAdvisor** agent with 3 custom Python functions exposed via `@ai_function`:

| Tool | Description |
| --- | --- |
| `calculate_compound_interest` | Computes compound interest with detailed breakdown |
| `analyze_sentiment` | Keyword-based sentiment scoring of market text |
| `generate_report_id` | Generates unique UUID-based report tracking IDs |

The agent streams its response token-by-token while calling tools inline during generation.

### Concurrent Debate + Judge

```bash
python src/run_chat_message.py
```

A multi-agent debate architecture using `ConcurrentBuilder` + `SequentialBuilder`:

```
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
```

- **BullAnalyst** and **BearAnalyst** argue for/against a proposition concurrently
- **JudgeAgent** receives both arguments via `ChatMessage` with `TextContent` and delivers a structured verdict with confidence score

## How It Works

The Agent Framework provides a higher-level abstraction on top of Azure OpenAI:

1. **`AzureOpenAIChatClient`** — wraps the Azure OpenAI endpoint with Azure CLI credentials
2. **`create_agent()`** — creates an agent with a name, instructions, and optional tools
3. **`agent.run()`** — sends input and returns a complete response
4. **`agent.run_stream()`** — sends input and yields streaming updates
5. **`ChatMessage`** — allows structured multi-content input (text, images via URI, etc.)
6. **`SequentialBuilder`** — chains agents so each builds on the previous output
7. **`ConcurrentBuilder`** — runs agents in parallel for fan-out patterns

## Orchestration Patterns

| Pattern | Script | Agents | Description |
| --- | --- | --- | --- |
| **Sequential** | `run_basic.py` | 3 | Research → Analysis → Briefing pipeline |
| **Streaming + Tools** | `run_streaming.py` | 1 | Agent calls custom Python functions mid-stream |
| **Concurrent + Sequential** | `run_chat_message.py` | 3 | Parallel debate → sequential judgment |

## Clean Up

```bash
az group delete --name rg-agent-framework --yes --no-wait
```
