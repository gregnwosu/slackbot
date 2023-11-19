resource "azurerm_redis_cache" "bot-cache" {
  name                          = var.resource_group_name_prefix
  location                      = azurerm_resource_group.LangChain-Experiments.location
  resource_group_name           = azurerm_resource_group.LangChain-Experiments.name
  capacity                      = 0
  family                        = "C"
  sku_name                      = "Basic"
  enable_non_ssl_port           = false
  minimum_tls_version           = "1.2"
  public_network_access_enabled = true

  # redis_configuration {
  #   aof_backup_enabled = false
  #   aof_storage_connection_string_0 = "DefaultEndpointsProtocol=https;BlobEndpoint=${azurerm_storage_account.gnwosutfstatestorageacc.primary_blob_endpoint};AccountName=${azurerm_storage_account.gnwosutfstatestorageacc.name};AccountKey=${azurerm_storage_account.gnwosutfstatestorageacc.primary_access_key}"
  # }
}
