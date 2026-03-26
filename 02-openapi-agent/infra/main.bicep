@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Name of the AI Foundry account')
param accountName string = 'ai-foundry-openapi-${uniqueSuffix}'

@description('Name of the AI Foundry project')
param projectName string = 'openapi-agent-project'

@description('Name of the model deployment')
param deploymentName string = 'gpt-5-4-mini'

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
    displayName: 'OpenAPI Agent Demo'
    description: 'Demo project for creating an agent with OpenAPI tools'
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
      name: 'gpt-5.4-mini'
      version: '2026-03-17'
    }
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
