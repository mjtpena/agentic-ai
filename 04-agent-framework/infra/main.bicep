@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Name of the AI Foundry account')
param accountName string = 'ai-foundry-af-${uniqueSuffix}'

@description('Name of the AI Foundry project')
param projectName string = 'agent-framework-project'

@description('Name of the model deployment')
param deploymentName string = 'gpt-5-2-chat'

resource account 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: accountName
  location: location
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: accountName
    allowProjectManagement: true
    publicNetworkAccess: 'Enabled'
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: account
  name: projectName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'Agent Framework Demo'
    description: 'Demo project for Agent Framework with Azure OpenAI'
  }
}

resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: deploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 50
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-5.2-chat'
      version: '2026-02-10'
    }
  }
}

@description('The Azure OpenAI endpoint URL')
output endpoint string = account.properties.endpoints['OpenAI Language Model Instance API']

@description('The model deployment name')
output modelDeploymentName string = deployment.name

@description('The account name')
output accountName string = account.name
