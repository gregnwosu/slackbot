resource "azurerm_key_vault" "slackbot_secrets" {
  name                = "slackbot-secrets"
  location            = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  sku_name            = "standard"
  purge_protection_enabled = true
  recoverable_days = 10
  sku {
    name = "standard"
    tier = "Free"
  }
}

resource "azurerm_key_vault_secret" "slackbot_synth_primary_access_key" {
  name         = "primary-access-key"
  value        = data.azurerm_cognitive_services_account.slackbot_synth.primary_access_key
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
}

resource "azurerm_key_vault_secret" "slackbot_synth_endpoint" {
  name         = "slackbot_synth_endpoint"
  value        = data.azurerm_cognitive_services_account.slackbot_synth.endpoint
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
  
}

