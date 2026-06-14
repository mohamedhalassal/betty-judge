resource "azurerm_storage_account" "queue" {
  name                            = "bettyjudgesa"
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = false
  tags = {
    purpose = "prod"
  }
}

resource "azurerm_private_endpoint" "queue-pe" {
  name                = "betty-judge-queue-pe"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.private-endpoint-subnet.id

  private_service_connection {
    name                           = "queue-connection"
    private_connection_resource_id = azurerm_storage_account.queue.id
    subresource_names              = ["queue"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "queue-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.queue-dns.id]
  }
}

resource "azurerm_storage_queue" "judge" {
  name               = "judge"
  storage_account_id = azurerm_storage_account.queue.id
}
resource "azurerm_storage_queue" "judge-poison" {
  name               = "judge-poison"
  storage_account_id = azurerm_storage_account.queue.id
}

resource "azurerm_key_vault_secret" "queue-connection-string" {
  name         = "queue-connection-string"
  value        = "DefaultEndpointsProtocol=https;AccountName=${azurerm_storage_account.queue.name};AccountKey=${azurerm_storage_account.queue.primary_access_key};EndpointSuffix=core.windows.net"
  key_vault_id = azurerm_key_vault.vault.id
  tags = {
    purpose = "prod"
  }
}
