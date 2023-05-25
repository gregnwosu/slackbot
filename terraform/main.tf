


resource "null_resource" "load_env" {
  provisioner "local-exec" {
    command = "dotenv -f ../.env set"
  }
}

resource "azurerm_resource_group" "LangChain-Experiments" {
  location = var.resource_group_location
  name     = var.resource_group_name_prefix
}