resource "azurerm_storage_account" "gnwosutfstatestorageacc" {
  name                     = "gnwosutfstatestorageacc"
  resource_group_name      = azurerm_resource_group.LangChain-Experiments.name
  location                 = azurerm_resource_group.LangChain-Experiments.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "gnwosutfstatestoragecont" {
  name                  = "gnwosutfstatestoragecont"
  storage_account_name  = azurerm_storage_account.gnwosutfstatestorageacc.name
  container_access_type = "private"
}

