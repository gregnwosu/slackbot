

data "azurerm_cognitive_services_account" "slackbot_synth" {
  name                = azurerm_cognitive_services_account.slackbot_synth.name
  resource_group_name = azurerm_cognitive_services_account.slackbot_synth.resource_group_name
}

