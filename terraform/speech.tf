resource "azurerm_cognitive_services_speech_synthesizer" "slackbot_synth" {
  name                = "slackbot_synth"
  location            = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  sku                 = "F0"
}

data "azurerm_cognitive_services_account" "slackbot_synth" {
  name                = azurerm_cognitive_services_account.slackbot_synth.name
  resource_group_name = azurerm_cognitive_services_account.slackbot_synth.resource_group_name
}

