@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Name of the AI Foundry account')
param accountName string = 'ai-foundry-a2a-${uniqueSuffix}'

@description('Name of the AI Foundry project')
param projectName string = 'a2a-agent-project'

@description('Name of the model deployment')
param deploymentName string = 'gpt-5-4-nano'

@description('Name of the A2A connection')
param a2aConnectionName string = 'a2a-remote-agent'

@description('The remote A2A agent endpoint URL')
param a2aEndpointUrl string

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
    displayName: 'A2A Agent Demo'
    description: 'Demo project for agent-to-agent communication'
  }
}

resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: deploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-5.4-nano'
      version: '2026-03-17'
    }
  }
}

// A2A connection to the remote agent endpoint
resource a2aConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = {
  parent: project
  name: a2aConnectionName
  properties: {
    category: 'A2A'
    target: a2aEndpointUrl
    authType: 'None'
  }
}

@description('The endpoint URL for the AI Foundry project (use with AIProjectClient)')
output projectEndpoint string = '${account.properties.endpoints['AI Foundry API']}api/projects/${project.name}'

@description('The model deployment name')
output modelDeploymentName string = deployment.name

@description('The account name')
output accountName string = account.name

@description('The project name')
output projectName string = project.name

@description('The A2A connection resource ID')
output a2aConnectionId string = a2aConnection.id
