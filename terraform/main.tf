terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  required_version = ">= 1.1.0"
}


provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "rg" {
  name     = "betty-judge-rg"
  location = "Canada Central"
}

resource "azurerm_key_vault" "vault" {
  name                = "betty-judge-vault"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku_name = "standard"


  tenant_id                  = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days = 7


  rbac_authorization_enabled  = true
  enabled_for_disk_encryption = true
}



resource "random_password" "jwt-secret" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
  min_upper        = 2
  min_lower        = 2
  min_numeric      = 2
  min_special      = 2
}

resource "azurerm_key_vault_secret" "jwt-secret" {
  name         = "jwt-secret-key"
  value        = random_password.jwt-secret.result
  key_vault_id = azurerm_key_vault.vault.id
}


resource "azurerm_log_analytics_workspace" "log-analytics" {
  name                = "betty-judge-log-analytics"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "env" {
  name                       = "backend-env"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  infrastructure_subnet_id   = azurerm_subnet.backend-subnet.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log-analytics.id
  workload_profile {
    maximum_count         = 0
    minimum_count         = 0
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}

resource "azurerm_container_registry" "acr" {
  name                = "bettyjudgeacr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false
}
