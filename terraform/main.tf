



resource "azurerm_resource_group" "LangChain-Experiments" {
  location = var.resource_group_location
  name     = var.resource_group_name_prefix
}

data "azurerm_client_config" "current" {}