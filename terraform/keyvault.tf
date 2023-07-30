resource "azurerm_key_vault" "slackbot_secrets" {
  name                     = "slackbot-secrets"
  location                 = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name      = azurerm_resource_group.LangChain-Experiments.name
  sku_name                 = "standard"
  purge_protection_enabled = true
  enable_rbac_authorization       = true
  tenant_id                = data.azurerm_client_config.current.tenant_id


}

resource "azurerm_key_vault_access_policy" "slackbot_app" {
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  key_permissions = [
    "Get",
    "List",
    "Encrypt",
    "Decrypt",
  ]

  secret_permissions = [
    "List",
    "Get",
    "Set",
  ]
}



resource "azuread_directory_role" "user_admin" {
  display_name = "User administrator"
}

resource "azuread_directory_role_member" "slackbot_user_admin" {
  role_object_id   = azuread_directory_role.user_admin.object_id
  member_object_id = data.azurerm_client_config.current.object_id
}

resource "azurerm_key_vault_secret" "slackbot_synth_primary_access_key" {
  name         = "slackbot-synth-primary-access-key"
  value        = azurerm_cognitive_account.LangChain_Experiments.primary_access_key
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
}

resource "azurerm_key_vault_secret" "slackbot_synth_endpoint" {
  name         = "slackbot-synth-endpoint"
  value        = azurerm_cognitive_account.LangChain_Experiments.endpoint
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
}


resource "azurerm_key_vault_secret" "slackbot_redis_key" {
  name         = "redis-key"
  value        = azurerm_redis_cache.bot-cache.primary_access_key
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
}

resource "azurerm_key_vault_secret" "slackbot_redis_hostname" {
  name         = "redis-key"
  value        = azurerm_redis_cache.bot-cache.hostname
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
}


resource "azurerm_key_vault_secret" "slackbot_azure_cogservices_key" { # all cog services use the same key
  key_vault_id = azurerm_key_vault.slackbot_secrets.id
  name         = "cogservices-key"
  value        = azurerm_cognitive_account.LangChain_Experiments.primary_access_key
}


data "azuread_user" "greg_data" {
  user_principal_name = "greg.nwosu_gmail.com#EXT#@gregnwosugmail.onmicrosoft.com"
  depends_on          = [azuread_directory_role_member.slackbot_user_admin]
}

data "azuread_application" "mySlackBotApp2" {
  display_name = "mySlackBotApp2"
}

data "azuread_service_principal" "mySlackBotApp2" {
  application_id = data.azuread_application.mySlackBotApp2.application_id
}

resource "azuread_directory_role" "UserAdministrator" {
  display_name = "User administrator"
}

data "azuread_application" "slackbot_app" {
  display_name = "mySlackBotApp2"
}
resource "azurerm_role_assignment" "slackbot_secrets_user_assignment" {
  scope                = azurerm_key_vault.slackbot_secrets.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = data.azuread_application.mySlackBotApp2.object_id
}
resource "azurerm_role_assignment" "greg_secrets_user_assignment" {
  scope                = azurerm_key_vault.slackbot_secrets.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = data.azuread_user.greg_data.object_id
}

# resource "azurerm_key_vault_access_policy" "mySlackBotApp2_app_access_policy" {
#   key_vault_id       = azurerm_key_vault.slackbot_secrets.id
#   tenant_id          = data.azurerm_client_config.current.tenant_id
#   object_id          = data.azuread_application.mySlackBotApp2.object_id
#   secret_permissions = ["Get", "List", "Set"]
#   key_permissions = [
#     "Get", "List", "Encrypt", "Decrypt"
#   ]
# }

# resource "azurerm_key_vault_access_policy" "greg_user_access_policy" {
#   key_vault_id       = azurerm_key_vault.slackbot_secrets.id
#   tenant_id          = data.azurerm_client_config.current.tenant_id
#   object_id          = data.azuread_user.greg_data.object_id
#   secret_permissions = ["Get", "List", "Set"]
#   key_permissions = [
#     "Get", "List", "Encrypt", "Decrypt"
#   ]
# }
