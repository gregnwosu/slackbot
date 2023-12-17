resource "azurerm_linux_function_app" "function_app" {
  name                        = "slackbotfunctionapp"
  resource_group_name         = azurerm_resource_group.LangChain-Experiments.name
  location                    = var.resource_group_location
  service_plan_id             = azurerm_service_plan.serviceplan.id
  https_only                  = true
  functions_extension_version = "~4"
  storage_account {
    access_key   = azurerm_storage_account.gnwosutfstatestorageaccount.primary_access_key
    account_name = azurerm_storage_account.gnwosutfstatestorageaccount.name
    name         = azurerm_storage_account.slackbotfunctionappstoragecont.slackbotfunctionappstoragecont.name
    share_name   = azurerm_storage_account.slackbotfunctionappstoragecont.slackbotfunctionappstoragecont.name
    type         = "AzureBlob"
  }
  app_settings = {

  # "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"

    "ENABLE_ORYX_BUILD"              = "true"
    "ENABLE_ORYX_BUILD"              = "true"
    "SLACK_BOT_TOKEN"                = var.SLACK_BOT_TOKEN
    "SLACK_SIGNING_SECRET"           = var.SLACK_SIGNING_SECRET
    "SLACK_BOT_USER_ID"              = var.SLACK_BOT_USER_ID
    "SERPAPI_API_KEY"                = var.SERPAPI_API_KEY
    "OPENAI_API_KEY"                 = var.OPENAI_API_KEY
    "HUGGING_FACE_API_KEY"           = var.HUGGING_FACE_API_KEY
    "VAR_ZAPIER_API_KEY"             = var.ZAPIER_API_KEY
    "ELEVENLABS_API_KEY"             = var.ELEVENLABS_API_KEY
    "REDIS_KEY"                      = var.REDIS_KEY
    "REDIS_URL"                      = var.REDIS_URL
    "VAULT_URL"                      = var.VAULT_URL
    "ARM_CLIENT_ID"                  = var.ARM_CLIENT_ID
    "ARM_CLIENT_SECRET"              = var.ARM_CLIENT_SECRET
    "ARM_TENANT_ID"                  = var.ARM_TENANT_ID
    #"SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "AzureWebJobsFeatureFlags"       = "EnableWorkerIndexing"
    #"APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.application_insight.instrumentation_key
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }
  logs {
    application_logs {

      file_system_level = "Information"

  zip_deploy_file = data.archive_file.function.output_path
}
}
}
