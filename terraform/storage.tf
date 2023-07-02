resource "azurerm_storage_account" "LangChain-Experiments" {
  name                     = "gnwosutfstatestorageacc"
  resource_group_name      = azurerm_resource_group.LangChain-Experiments.name
  location                 = azurerm_resource_group.LangChain-Experiments.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "terraform_state" {
  name                  = "gnwosutfstatestoragecont"
  storage_account_name  = azurerm_storage_account.LangChain-Experiments.name
  container_access_type = "private"
}

