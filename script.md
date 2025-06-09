```bash
az webapp up --sku B1 --location germanywestcentral --name jea-09-06-2025 --resource-group 1-ec760e8a-playground-sandbox

```

```bash
az storage account create --name jea09062025storage --location germanywestcentral --resource-group 1-ec760e8a-playground-sandbox --sku Standard_LRS
```

```bash
az functionapp create --resource-group 1-ec760e8a-playground-sandbox --consumption-plan-location germanywestcentral --runtime python --runtime-version 3.11 --functions-version 4 --name jea-09-06-2025-functions --storage-account jea09062025storage --os-type linux
```

```bash
func azure functionapp publish jea-09-06-2025-functions
```

```bash
az storage table create --name AcmeTranslations --account-name jea09062025storage
```
