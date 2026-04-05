# Azure AI Foundry Agent Service Demos

Four self-contained, progressively advanced demos showcasing [Azure AI Foundry Agent Service](https://learn.microsoft.com/azure/ai-services/agents/) capabilities — from a single agent with code interpretation to multi-agent orchestration with streaming. Each demo includes its own **Bicep infrastructure-as-code** and **Python application code**, so you can go from `az deployment` to a running agent in minutes.

## Demos

| Demo | What You'll Learn | Key Capabilities |
| --- | --- | --- |
| [01-basic-agent](01-basic-agent/) | Create an agent that autonomously writes & runs Python code | Code Interpreter tool, Monte Carlo simulations, statistical analysis, linear programming |
| [02-openapi-agent](02-openapi-agent/) | Connect an agent to multiple live external APIs via OpenAPI specs | OpenAPI tool calling, multi-API orchestration (weather, countries, exchange rates), travel briefings |
| [03-a2a-agent](03-a2a-agent/) | Orchestrate multiple agents across services using A2A protocol | Agent-to-Agent (A2A) communication, streaming responses, task delegation |
| [04-agent-framework](04-agent-framework/) | Build multi-agent pipelines with the Microsoft Agent Framework SDK | Sequential & concurrent orchestration, custom function tools, streaming output, debate pattern |

## Prerequisites

- **Azure CLI** — authenticated via `az login`
- **Python 3.10+**
- **Azure subscription** with one of these roles at subscription scope:
  - Azure AI Account Owner
  - Contributor
  - Cognitive Services Contributor

## Quick Start

```bash
# Set your subscription
az account set --subscription <your-subscription-id>

# Pick a demo and follow its README
cd 01-basic-agent
```

Each demo follows the same pattern:

1. **Deploy infrastructure** — `az deployment group create` with the Bicep template
2. **Configure `.env`** — Copy `.env.example` and fill in deployment outputs
3. **Install dependencies** — `pip install -r requirements.txt`
4. **Run** — `python src/main.py`

## Project Structure

```
agentic-ai/
├── 01-basic-agent/            # Code Interpreter agent for data analysis
│   ├── infra/                 # Bicep templates (AI Services account + project + model)
│   ├── src/main.py            # Agent code
│   ├── requirements.txt
│   └── .env.example
├── 02-openapi-agent/          # Multi-API travel intelligence agent
│   ├── infra/
│   ├── src/
│   │   └── assets/            # OpenAPI specs (weather, countries, exchange rates)
│   ├── requirements.txt
│   └── .env.example
├── 03-a2a-agent/              # Agent-to-Agent orchestration
│   ├── infra/                 # Bicep templates (includes A2A connection)
│   ├── src/main.py
│   ├── requirements.txt
│   └── .env.example
├── 04-agent-framework/        # Microsoft Agent Framework SDK
│   ├── infra/
│   ├── src/
│   │   ├── run_basic.py       # Sequential multi-agent pipeline
│   │   ├── run_streaming.py   # Streaming with custom function tools
│   │   └── run_chat_message.py # Concurrent debate + judge pattern
│   ├── requirements.txt
│   └── .env.example
├── check_models.py            # Query available Azure OpenAI models
├── run_and_log.py             # Execute demos and capture logs
├── reformat_logs.py           # Clean up execution log formatting
└── models.json                # Azure OpenAI model metadata snapshot
```

## Tool Types Demonstrated

| Tool Type | Demo | Description |
| --- | --- | --- |
| **Code Interpreter** | 01 | Agent autonomously writes and executes Python code |
| **OpenAPI** | 02 | Agent calls external REST APIs via OpenAPI 3.0 specs |
| **A2A** | 03 | Agent delegates tasks to remote A2A-compatible agents |
| **Custom Functions** | 04 | Python functions exposed to the agent via `@ai_function` |

## Orchestration Patterns

- **Single Agent** — One agent with tools (Demos 01, 02)
- **Agent-to-Agent** — Orchestrator delegates to remote agents (Demo 03)
- **Sequential Pipeline** — Agents execute in order, passing context forward (Demo 04)
- **Concurrent + Sequential** — Parallel agents feed into a final synthesizer (Demo 04)

## Clean Up

```bash
az group delete --name rg-basic-agent --yes --no-wait
az group delete --name rg-openapi-agent --yes --no-wait
az group delete --name rg-a2a-agent --yes --no-wait
az group delete --name rg-agent-framework --yes --no-wait
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
