# Demo 4: Agent Framework with Azure OpenAI

This demo provisions an Azure OpenAI resource and GPT-4o deployment, then uses the **Microsoft Agent Framework** SDK to create and run an agent in three different modes: basic, streaming, and ChatMessage.

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

### Basic run (single response)

```bash
python src/run_basic.py
```

Creates a joke-telling agent and prints a single joke.

### Streaming run (token-by-token)

```bash
python src/run_streaming.py
```

Same agent, but streams the response as it's generated.

### ChatMessage run (structured input)

```bash
python src/run_chat_message.py
```

Sends a structured `ChatMessage` with `TextContent` to the agent.

## How It Works

The Agent Framework provides a higher-level abstraction on top of Azure OpenAI:

1. **`AzureOpenAIChatClient`** — Wraps the Azure OpenAI endpoint with Azure CLI credentials.
2. **`create_agent()`** — Creates an agent with a name and instructions.
3. **`agent.run()`** — Sends input and returns a complete response.
4. **`agent.run_stream()`** — Sends input and yields streaming updates.
5. **`ChatMessage`** — Allows structured multi-content input (text, images via URI, etc.).

## Expected Output

### Basic
```
Why did the pirate go to school? To improve his arrrticulation!
```

### Streaming
```
Why did the pirate... go to school?... To improve his arrrticulation!
```
(tokens appear progressively)

### ChatMessage
```
Why do programmers prefer dark mode? Because light attracts bugs!
```

## Clean Up

```bash
az group delete --name rg-agent-framework --yes --no-wait
```
