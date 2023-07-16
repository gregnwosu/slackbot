
# resource "azurerm_network_security_group" "LangChain-Experiments" {
#   name                = "${var.resource_group_name_prefix}SecurityGroup"
#   location            = azurerm_resource_group.LangChain-Experiments.location
#   resource_group_name = azurerm_resource_group.LangChain-Experiments.name

#   security_rule {
#     name                       = "allow-http"
#     priority                   = 100
#     direction                  = "Inbound"
#     access                     = "Allow"
#     protocol                   = "Tcp"
#     source_port_range          = "*"
#     destination_port_range     = "80"
#     source_address_prefix      = "*"
#     destination_address_prefix = "*"
#   }
# }





# resource "azurerm_virtual_network" "LangChain-Experiments" {
#   name                = "example-network"
#   location            = azurerm_resource_group.LangChain-Experiments.location
#   resource_group_name = azurerm_resource_group.LangChain-Experiments.name
#   address_space       = ["10.0.0.0/16"]


#   subnet {
#     name           = "backend"
#     address_prefix = "10.0.1.0/24"
#   }


#   tags = {
#     environment = "chatbot_net"
#   }
# }
