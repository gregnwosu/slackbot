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
    site_config {
        always_on = false
        
         application_stack{
            python_version = "3.11"
         } 
   
}
    }
   