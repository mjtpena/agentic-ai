# Demo 3: Agent-to-Agent (A2A) Communication

> **Note:** This demo requires a **running external A2A-compatible agent endpoint** to function.
> Unlike Demos 1, 2, and 4, it cannot be self-contained — it needs a remote agent service
> (e.g., another Foundry agent, a Fabric Data Agent, or a custom A2A server) already deployed and accessible.

This demo provisions an Azure AI Foundry account, project, GPT-4o deployment, and an A2A connection, then creates an orchestrator agent that delegates tasks to a remote agent via the A2A protocol.

## Prerequisites

- Azure CLI authenticated (`az login`)
- Python 3.10+
- Azure subscription with **Contributor** or **Owner** role, plus **Azure AI User** at the project level
- **A running remote A2A-compatible agent endpoint** (e.g., another Foundry agent, a Fabric Data Agent, or any A2A-compliant server)

## Deploy Infrastructure

First, update `infra/main.bicepparam` with the URL of your remote A2A agent endpoint.

```bash
az group create --name rg-a2a-agent --location eastus2

az deployment group create \
  --resource-group rg-a2a-agent \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam
```

After deployment completes, note the outputs — especially `a2aConnectionId`.

## Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with values from the deployment outputs:

| Variable                        | Source                       |
| ------------------------------- | ---------------------------- |
| `FOUNDRY_PROJECT_ENDPOINT`      | `projectEndpoint` output     |
| `FOUNDRY_MODEL_DEPLOYMENT_NAME` | `modelDeploymentName` output |
| `A2A_PROJECT_CONNECTION_ID`     | `a2aConnectionId` output     |

## Run the Demo

```bash
pip install -r requirements.txt
python src/main.py
```

## How It Works

1. Creates an orchestrator agent with an A2A tool pointing to a remote agent connection.
2. Prompts you for a question interactively.
3. The orchestrator agent delegates the question to the remote agent via A2A protocol.
4. Streams the response delta-by-delta as it arrives.
5. Cleans up by deleting the agent version.

## Setting Up a Remote A2A Agent

The A2A connection requires a remote agent that supports the Agent-to-Agent protocol. Options include:

- **Another Foundry Agent** — Deploy a second Foundry project with its own agent.
- **Microsoft Fabric Data Agent** — Connect to a Fabric workspace data agent.
- **Custom A2A Server** — Any server implementing the A2A protocol with a `/.well-known/agent.json` discovery endpoint.

### Creating the A2A Connection via REST API

If you prefer to create the connection manually instead of via Bicep:

```bash
az rest --method put \
  --uri "https://management.azure.com/subscriptions/<your-subscription-id>/resourceGroups/rg-a2a-agent/providers/Microsoft.CognitiveServices/accounts/<account-name>/projects/a2a-agent-project/connections/a2a-remote-agent?api-version=2025-06-01" \
  --body '{
    "properties": {
      "category": "A2A",
      "target": "https://<remote-agent-endpoint>/.well-known/agent.json",
      "authType": "None"
    }
  }'
```

## Expected Output

```
Agent created (id: asst_abc123, name: A2AOrchestrator, version: 1)
Enter your question (e.g., 'What can the secondary agent do?'):
> What data sources can you query?

Response created with ID: resp_xyz789
The secondary agent can query the following data sources...

Response complete!

Full response: The secondary agent can query the following data sources...

Cleaning up...
Agent deleted.
```

## Security Considerations

- Only connect to A2A endpoints hosted by **trusted service providers**.
- Review all data shared with non-Microsoft services and log it for auditing.
- Use managed identity or API key authentication when connecting to secured endpoints.
- Be aware of third-party data retention and location policies.

## Clean Up

```bash
az group delete --name rg-a2a-agent --yes --no-wait
```
