resource "azurerm_cognitive_account" "slackbot_azure_cogservices" {
  name                = "Slackbot-CogServices"
  location            = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  kind                = "Bing.Search.v7"
  sku_name            = "F0"
}
