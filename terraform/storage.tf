resource "azurerm_storage_account" "storage_account" {
  name                     = "slackbotstorageaccount"
  resource_group_name      = azurerm_resource_group.LangChain-Experiments.name
  location                 = azurerm_resource_group.LangChain-Experiments.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "storage_container" {
  name                  = "slackbotstoragecontainer"
  storage_account_name  = azurerm_storage_account.storage_account.name
  container_access_type = "private"
}