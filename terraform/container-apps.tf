resource "azurerm_container_app" "backend" {
  name                         = "backend"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  secret {
    name                = "queue-connection-string"
    identity            = "System"
    key_vault_secret_id = azurerm_key_vault_secret.queue-connection-string.id
  }
  secret {
    name                = "databaseconnectionstring"
    identity            = "System"
    key_vault_secret_id = azurerm_key_vault_secret.backend-database-connection-string.id
  }
  secret {
    name                = "googleclientid"
    identity            = "System"
    key_vault_secret_id = "${azurerm_key_vault.vault.vault_uri}secrets/google-client-id"
  }
  secret {
    name                = "jwt-secret-key"
    identity            = "System"
    key_vault_secret_id = "${azurerm_key_vault.vault.vault_uri}secrets/jwt-secret-key"
  }

  template {
    container {
      name   = "backend"
      image  = "ghcr.io/mohamedhalassal/betty-backend:latest" # update to the judge image
      cpu    = 0.5
      memory = "1Gi"
      env {
        name        = "AZURE_QUEUE_CONNECTION_STRING"
        secret_name = "queue-connection-string"
      }
      env {
        name  = "AZURE_QUEUE_NAME"
        value = "judge"
      }
      env {
        name        = "DATABASE_URL"
        secret_name = "databaseconnectionstring"
      }
      env {
        name  = "FRONTEND_URL"
        value = "https://betty-judge.vercel.app"
      }
      env {
        name        = "GOOGLE_CLIENT_ID"
        secret_name = "googleclientid"
      }
      env {
        name        = "JWT_SECRET_KEY"
        secret_name = "jwt-secret-key"
      }
    }
    min_replicas = 0
    max_replicas = 4
  }
  ingress {
    target_port      = 8000
    external_enabled = true
    transport        = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
    cors {
      allowed_origins           = ["https://betty-judge.vercel.app"]
      allowed_methods           = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
      allowed_headers           = ["*"]
      exposed_headers           = ["*"]
      allow_credentials_enabled = false
      max_age_in_seconds        = 300
    }
  }

  tags = {
    purpose = "prod"
  }
  workload_profile_name = "Consumption"
}

resource "azurerm_container_app" "judge" {
  name                         = "judge"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  secret {
    name                = "queue-connection-string"
    identity            = "System"
    key_vault_secret_id = azurerm_key_vault_secret.queue-connection-string.id
  }
  secret {
    name                = "databaseconnectionstring"
    identity            = "System"
    key_vault_secret_id = azurerm_key_vault_secret.backend-database-connection-string.id
  }

  template {
    container {
      name   = "judge"
      image  = "ghcr.io/mohamedhalassal/judge:latest" # update to the judge image
      cpu    = 0.5
      memory = "1Gi"
      env {
        name        = "AZURE_QUEUE_CONNECTION_STRING"
        secret_name = "queue-connection-string"
      }
      env {
        name  = "AZURE_QUEUE_NAME"
        value = "judge"
      }
      env {
        name        = "DATABASE_URL"
        secret_name = "databaseconnectionstring"
      }
    }
    azure_queue_scale_rule {
      name         = "testing-rule"
      queue_name   = "judge"
      queue_length = 2
      authentication {
        secret_name       = "queue-connection-string"
        trigger_parameter = "connection"
      }
    }
    min_replicas = 0
    max_replicas = 30
  }

  tags = {
    purpose = "prod"
  }
  workload_profile_name = "Consumption"
}



