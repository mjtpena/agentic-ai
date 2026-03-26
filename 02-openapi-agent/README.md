# Demo 2: Foundry Agent with OpenAPI Tool

This demo provisions an Azure AI Foundry account, project, and GPT-4o deployment, then creates an agent that calls a weather API via an OpenAPI 3.0 specification with anonymous authentication.

## Prerequisites

- Azure CLI authenticated (`az login`)
- Python 3.10+
- Azure subscription with **Contributor** or **Owner** role on the Foundry project

## Deploy Infrastructure

```bash
az group create --name rg-openapi-agent --location eastus2

az deployment group create \
  --resource-group rg-openapi-agent \
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

1. Loads the OpenAPI specification from `src/assets/weather_openapi.json` describing the [wttr.in](https://wttr.in) weather API.
2. Creates an agent with the OpenAPI tool configured for anonymous access.
3. Sends weather queries — the agent automatically calls the weather API and returns formatted results.
4. Cleans up by deleting the agent version.

## OpenAPI Specification

The included `weather_openapi.json` defines a single endpoint:

- **GET** `/{city}?format=j1` — Returns current weather conditions in JSON format from wttr.in.

### Authentication Types Supported

This demo uses **anonymous** auth. The Foundry Agent Service also supports:

- **API Key** (`project_connection` type) — Uses a Foundry project connection storing your API key.
- **Managed Identity** (`managed_identity` type) — Uses Azure Managed Identity for token-based auth.

See `src/main.py` comments for examples of each auth type.

## Expected Output

```
Agent created (id: asst_abc123, name: WeatherAgent, version: 1)

User: What's the weather in Seattle?
Agent: The weather in Seattle is currently cloudy with a temperature of 52°F (11°C)...

User: How's the weather in Tokyo right now?
Agent: Tokyo currently has clear skies with a temperature of 72°F (22°C)...

User: Tell me the current weather conditions in London.
Agent: London is experiencing light rain with a temperature of 55°F (13°C)...

Cleaning up...
Agent deleted.
```

## Clean Up

```bash
az group delete --name rg-openapi-agent --yes --no-wait
```
