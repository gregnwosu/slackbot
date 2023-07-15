resource "azurerm_key_vault" "slackbot_secrets" {
  name                = "slackbot-secrets"
  location            = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  sku_name            = "standard"
  purge_protection_enabled = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get",
      "List",
    ]

    secret_permissions = [
      "Get",
      "List",
    ]
  }
   
  }


resource "azurerm_key_vault_secret" "slackbot_synth_primary_access_key" {
  name         = "primary-access-key"
  value        = azurerm_cognitive_account.slackbot_synth.primary_access_key
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
}

resource "azurerm_key_vault_secret" "slackbot_synth_endpoint" {
  name         = "slackbot-synth-endpoint"
  value        = azurerm_cognitive_account.slackbot_synth.endpoint
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
}

