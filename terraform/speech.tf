resource "azurerm_cognitive_account" "LangChain_Experiments" {
  name                = "LangChain-Experiments"
  location            = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  kind                = "SpeechServices"
  sku_name            = "F0"
}
