# Demo 1: Create a Basic Foundry Agent

This demo provisions an Azure AI Foundry account, project, and GPT-4o deployment, then creates a basic agent that answers geography questions.

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

## Expected Output

```
Agent created (id: asst_abc123, name: BasicGeoAgent, version: 1)

User: What is the capital of Australia?
Agent: The capital of Australia is Canberra.

User: What are the 5 largest countries by area?
Agent: The 5 largest countries by area are: 1. Russia, 2. Canada, 3. China, 4. United States, 5. Brazil.

User: Which river is the longest in the world?
Agent: The Nile River is generally considered the longest river in the world...

Cleaning up...
Agent deleted.
```

## Clean Up

```bash
az group delete --name rg-basic-agent --yes --no-wait
```
