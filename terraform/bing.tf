resource "azurerm_resource_group_template_deployment" "bing_search_deployment" {
  name                = "bing-search-deployment"
  
  resource_group_name = azurerm_resource_group.LangChain-Experiments.name
  deployment_mode     = "Incremental"

  parameters_content = jsonencode({
    "name" = {
      value = "bing_search"
    },
    "location" = {
      value = "Global"
    },
    "sku" = {
      value = "F1"
    },
    "kind" = {
      value = "Bing.Search.v7"
    }
  })
  template_content = <<TEMPLATE
{
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "name": {
            "type": "String"
        },
        "location": {
            "type": "String"
        },
        "sku": {
            "type": "String"
        },
        "kind": {
          "type": "String"
        }

    },
    "resources": [
        {
            "apiVersion": "2020-06-10",
            "name": "[parameters('name')]",
            "location": "[parameters('location')]",
            "type": "Microsoft.Bing/accounts",
            "kind": "[parameters('kind')]",
            "sku": {
                "name": "[parameters('sku')]"
            }
        }
    ],
    "outputs": {
      
      "accessKeys": {
          "type": "Object",
          "value": {
              "key1": "[listKeys(resourceId('Microsoft.Bing/accounts', parameters('name')), '2020-06-10').key1]",
              "key2": "[listKeys(resourceId('Microsoft.Bing/accounts', parameters('name')), '2020-06-10').key2]",
              "endpoint": "[reference(resourceId('Microsoft.Bing/accounts', parameters('name')), '2020-06-10').endpoint]"
          }
        }
    }
}
TEMPLATE
}

# data "azurerm_resource_group_template_deployment" "bing_search_deployment" {
#   name                = "bing-search-deployment"
#   resource_group_name = azurerm_resource_group.LangChain-Experiments.name
# }
