resource "azurerm_application_insights" "app_insights" {
  name                = "${var.resource_group_name_prefix}-appinsight"
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  location            = azurerm_resource_group.LangChain-Experiments.location
  application_type    = "other"
}
