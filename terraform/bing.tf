resource "azurerm_cognitive_account" "slackbot_azure_cogservices" {
  name                = "Slackbot-CogServices"
  location            = "eastus2" # This needs to be set as a eastus2 service
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  kind                = "Bing.Search.v7"
  sku_name            = "F0"
}
