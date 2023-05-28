resource "azurerm_service_plan" "serviceplan" {
  name                = "serviceplan"
  sku_name = "F1"
  os_type = "Linux"
  location            = var.resource_group_location
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name


}

resource "azurerm_linux_web_app" "slackbotwebapp" {

    name = "slackbotwebapp"
    resource_group_name = azurerm_resource_group.LangChain-Experiments.name 
    location = var.resource_group_location
    service_plan_id = azurerm_service_plan.serviceplan.id 
    app_settings                      = {
          "SCM_DO_BUILD_DURING_DEPLOYMENT" = "1" 
          "SLACK_BOT_TOKEN"="${var.SLACK_BOT_TOKEN}"
          "SLACK_SIGNING_SECRET"="${var.SLACK_SIGNING_SECRET}"
          "SLACK_BOT_USER_ID"="${var.SLACK_BOT_USER_ID}"
          "SERPAPI_API_KEY"="${var.SERPAPI_API_KEY}"
          "OPENAI_API_KEY"="${var.OPENAI_API_KEY}"

          #get variable from the environment
          
        }
    site_config {
      always_on = false
      app_command_line = "startup.txt"
      application_stack{
            python_version = "3.8.16"
      } 
    }

    }
  