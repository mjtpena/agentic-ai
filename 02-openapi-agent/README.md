# Demo 2: Travel Intelligence Agent — Multi-API Orchestration

This demo provisions an Azure AI Foundry account, project, and GPT-5.4-mini deployment, then creates a **Travel Intelligence Agent** that orchestrates 3 live external APIs simultaneously via OpenAPI 3.0 specifications to generate comprehensive travel briefings.

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

1. Loads 3 OpenAPI specifications from `src/assets/`:
   - **Weather API** ([wttr.in](https://wttr.in)) — real-time weather conditions
   - **Countries API** ([restcountries.com](https://restcountries.com)) — country facts, languages, currencies
   - **Exchange Rate API** ([open.er-api.com](https://open.er-api.com)) — live currency conversion rates
2. Creates a **TravelIntelligenceAgent** with all 3 APIs configured as OpenAPI tools with anonymous authentication.
3. Sends travel briefing requests — the agent calls all relevant APIs and synthesizes data into comprehensive, structured travel intelligence.
4. Includes a 60-second pause between requests to respect API rate limits.
5. Cleans up by deleting the agent version.

## OpenAPI Specifications

| Spec File | API | Endpoint |
| --- | --- | --- |
| `weather_openapi.json` | [wttr.in](https://wttr.in) | `GET /{city}?format=j1` — current weather in JSON |
| `countries_openapi.json` | [restcountries.com](https://restcountries.com) | `GET /v3.1/name/{name}` — country details |
| `exchange_openapi.json` | [open.er-api.com](https://open.er-api.com) | `GET /v6/latest/{base}` — live exchange rates |

### Authentication Types Supported

This demo uses **anonymous** auth. The Foundry Agent Service also supports:

- **API Key** (`project_connection` type) — Uses a Foundry project connection storing your API key.
- **Managed Identity** (`managed_identity` type) — Uses Azure Managed Identity for token-based auth.

## Expected Output

```
🌍 Travel Intelligence Agent created (name: TravelIntelligenceAgent, version: 1)
   Model: gpt-5-4-mini | Tools: Weather API, Countries API, Exchange Rate API
======================================================================

──────────────────────────────────────────────────────────────────────
🗺️  Briefing 1: Tokyo Travel Briefing
──────────────────────────────────────────────────────────────────────
Request: I'm an Australian traveller planning a trip to Tokyo, Japan...

[Agent calls all 3 APIs and synthesizes a comprehensive briefing with
 weather, country facts, AUD→JPY exchange rates, and travel tips]

──────────────────────────────────────────────────────────────────────
🗺️  Briefing 2: Quick Paris Check
──────────────────────────────────────────────────────────────────────
Request: Quick check: what's the weather in Paris right now...

[Agent returns a concise 3-bullet summary with weather and exchange rate]

======================================================================
Cleaning up...
✅ Agent deleted.
```

## Clean Up

```bash
az group delete --name rg-openapi-agent --yes --no-wait
```
