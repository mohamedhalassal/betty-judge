#
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?" # Azure-safe special chars
  min_upper        = 2
  min_lower        = 2
  min_numeric      = 2
  min_special      = 2
}

resource "azurerm_postgresql_flexible_server" "database" {
  name                          = "betty-judge-prod-db"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  version                       = "18"
  delegated_subnet_id           = azurerm_subnet.psql-subnet.id
  private_dns_zone_id           = azurerm_private_dns_zone.database-dns.id
  public_network_access_enabled = false
  administrator_login           = "psqladmin"
  administrator_password        = random_password.db_password.result

  storage_mb   = 32768
  storage_tier = "P4"

  zone = 1

  sku_name   = "B_Standard_B1ms"
  depends_on = [azurerm_private_dns_zone_virtual_network_link.vnet-dns-link]
  tags = {
    purpose = "prod"
  }

}

resource "azurerm_key_vault_secret" "backend-database-connection-string" {
  name         = "backend-database-connection-string"
  value        = "postgresql://${azurerm_postgresql_flexible_server.database.administrator_login}:${urlencode(random_password.db_password.result)}@${azurerm_postgresql_flexible_server.database.fqdn}:5432/postgres?sslmode=require"
  key_vault_id = azurerm_key_vault.vault.id
  tags = {
    purpose = "prod"
  }

}

resource "azurerm_postgresql_flexible_server_configuration" "pg_stat_statements" {
  name      = "pg_stat_statements.track"
  server_id = azurerm_postgresql_flexible_server.database.id
  value     = "all"
}

resource "azurerm_postgresql_flexible_server_configuration" "track_io_timing" {
  name      = "track_io_timing"
  server_id = azurerm_postgresql_flexible_server.database.id
  value     = "on"
}

resource "azurerm_monitor_diagnostic_setting" "postgres-logs" {
  name                       = "postgres-query-perf"
  target_resource_id         = azurerm_postgresql_flexible_server.database.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log-analytics.id

  enabled_log {
    category = "PostgreSQLLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}
