# WorkRepository
Python Sandbox

# Azure Function Python deployment

Compress-Archive `
  -Path .\python\stubFunctionServicePcloud\function_app.py,
        .\python\stubFunctionServicePcloud\file_processor.py,
        .\python\stubFunctionServicePcloud\requirements.txt,
        .\python\stubFunctionServicePcloud\host.json `
  -DestinationPath .\deploy.zip `
  -Force

  az login

az account set --subscription "subs-dev-001"

az functionapp config appsettings set `
  --resource-group "rg-dev-webservice" `
  --name "func-dev-webservice" `
  --settings "AzureWebJobsStorage=DefaultEndpointsProtocol=https;AccountName=stfuncdevwebservice;AccountKey=/U9Gkag***********************************bk6Q4Tt+7dG+AStNZhVNw==;EndpointSuffix=core.windows.net"

OUTPUT:
[
  {
    "name": "DEPLOYMENT_STORAGE_CONNECTION_STRING",
    "slotSetting": false,
    "value": null
  },
  {
    "name": "AzureWebJobsStorage",
    "slotSetting": false,
    "value": null
  }
]


az functionapp deployment source config-zip `
  --resource-group "rg-dev-webservice" `
  --name "func-dev-webservice" `
  --src ".\deploy.zip" `
  --build-remote true

OUTPUT (with issues):
Getting scm site credentials for zip deployment
Starting zip deployment. This operation can take a while to complete ...
Deployment endpoint responded with status code 202 for deployment id "411e8e6f-5c6c-4165-a08a-2eea8f3a4178"
Waiting for sync triggers...
Checking the health of the function app
!!!Failed to fetch host key to check for function app status!!!

OUTPUT:
Getting scm site credentials for zip deployment
Starting zip deployment. This operation can take a while to complete ...
Deployment endpoint responded with status code 202 for deployment id "4499c7be-5ad4-4734-a593-0f9b006ef7bb"
Waiting for sync triggers...
Checking the health of the function app
"Deployment was successful."


az functionapp function list `
  --resource-group "rg-dev-webservice" `
  --name "func-dev-webservice" `
  --output table

az functionapp config appsettings list --resource-group rg-dev-webservice --name func-dev-webservice --query "[?name=='AzureWebJobsStorage' || name=='AzureWebJobsStorage__accountName' || name=='FUNCTIONS_WORKER_RUNTIME'].{name:name,value:value}" --output json; az functionapp function show --resource-group rg-dev-webservice --name func-dev-webservice --function-name process_file --output json

az storage blob list --account-name stfuncdevwebservice --container-name input --auth-mode login --query "[].{name:name,lastModified:properties.lastModified}" --output table


az functionapp function show --resource-group rg-dev-webservice --name func-dev-webservice --function-name process_file --query "config.bindings" --output json; 

az eventgrid event-subscription list --source-resource-id "/subscriptions/4b5f4da7-0329-47db-8f79-a64d15192d2c/resourceGroups/rg-dev-webservice/providers/Microsoft.Storage/storageAccounts/stfuncdevwebservice" --output json; 



# Register Eventgrid

$subscriptionId = "4b5f4da7-0329-47db-8f79-a64d15192d2c"
$storageId = "/subscriptions/$subscriptionId/resourceGroups/rg-dev-webservice/providers/Microsoft.Storage/storageAccounts/stfuncdevwebservice"

$blobExtensionKey = az functionapp keys list `
  --resource-group rg-dev-webservice `
  --name func-dev-webservice `
  --query "systemKeys.blobs_extension" `
  --output tsv

az eventgrid event-subscription list `
  --source-resource-id $storageId `
  --output table
  
az eventgrid event-subscription create `
  --name func-dev-webservice-blob-trigger `
  --source-resource-id $storageId `
  --endpoint $endpoint `
  --endpoint-type webhook    

az eventgrid event-subscription create `
  --name func-dev-webservice-blob-trigger `
  --source-resource-id $storageId `
  --endpoint-type azurefunction `
  --endpoint "/subscriptions/4b5f4da7-0329-47db-8f79-a64d15192d2c/resourceGroups/rg-dev-webservice/providers/Microsoft.Web/sites/func-dev-webservice/functions/process_file"
  
    