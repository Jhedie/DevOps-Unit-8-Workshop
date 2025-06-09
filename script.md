Command to web app in Azure:
```bash
az webapp up --sku B1 --location germanywestcentral --name jea-09-06-2025 --resource-group 1-ec760e8a-playground-sandbox

```


Command to create a storage account:
```bash
az storage account create --name jea09062025storage --location germanywestcentral --resource-group 1-ec760e8a-playground-sandbox --sku Standard_LRS
```

Command to create a function app in the storage account:
```bash
az functionapp create --resource-group 1-ec760e8a-playground-sandbox --consumption-plan-location germanywestcentral --runtime python --runtime-version 3.11 --functions-version 4 --name jea-09-06-2025-functions --storage-account jea09062025storage --os-type linux
```

Command to deploy the function app
```bash
func azure functionapp publish jea-09-06-2025-functions
```


Command to create a table in the storage account:
```bash
az storage table create --name AcmeTranslations --account-name jea09062025storage
```

Command to fetch the app settings for the function app so you can add the connection string to the table storage:

```bash
func azure functionapp fetch-app-settings jea-09-06-2025-functions
```

```

```
