resource "azurerm_cognitive_account" "slackbot_synth" {
  name                = "slackbot-synth"
  location            = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  kind               = "SpeechServices"
  sku_name                 = "F0"
}



