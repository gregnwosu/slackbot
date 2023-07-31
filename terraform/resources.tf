resource "azurerm_service_plan" "serviceplan" {
  name                = "serviceplan"
  sku_name            = "F1"
  os_type             = "Linux"
  location            = var.resource_group_location
  resource_group_name = "langchain-experiments"


}

resource "azurerm_linux_web_app" "slackbotwebapp" {

  name                = "slackbotwebapp"
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  location            = var.resource_group_location
  service_plan_id     = azurerm_service_plan.serviceplan.id
  app_settings = {
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "1"
    "SLACK_BOT_TOKEN"                = "${var.SLACK_BOT_TOKEN}"
    "SLACK_SIGNING_SECRET"           = "${var.SLACK_SIGNING_SECRET}"
    "SLACK_BOT_USER_ID"              = "${var.SLACK_BOT_USER_ID}"
    "SERPAPI_API_KEY"                = "${var.SERPAPI_API_KEY}"
    "OPENAI_API_KEY"                 = "${var.OPENAI_API_KEY}"
    "HUGGING_FACE_API_KEY"           = "${var.HUGGING_FACE_API_KEY}"
    "VAR_ZAPIER_API_KEY"             = "${var.ZAPIER_API_KEY}"
    "ELEVENLABS_API_KEY"             = "${var.ELEVENLABS_API_KEY}"
    "REDIS_KEY"                      = "${var.REDIS_KEY}"
    "REDIS_URL"                      = "${var.REDIS_URL}"
    "VAULT_URL"                      = "${var.VAULT_URL}"
    "ARM_CLIENT_ID"                  = "${var.ARM_CLIENT_ID}"
    "ARM_CLIENT_SECRET"              = "${var.ARM_CLIENT_SECRET}"
    "ARM_TENANT_ID"                  = "${var.ARM_TENANT_ID}"

    #get variable from the environment

  }
  site_config {
    always_on        = false
    app_command_line = "gunicorn -w 4 -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker slackbot.app:api "
    application_stack {
      python_version = "3.8"
    }
  }
  logs {
    application_logs {

      file_system_level = "Information"

    }
  }


}
