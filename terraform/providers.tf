# add terraform providers

# need to do a az login first with az cli

terraform {
  required_version = ">=1.4.6"

  backend "azurerm" {
    resource_group_name  = "LangChain-Experiments"
    storage_account_name = "gnwosutfstatestorageacc"
    container_name       = "gnwosutfstatestoragecont"
    key                  = "terraform.tfstate"
  }
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.57.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "2.40.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}
