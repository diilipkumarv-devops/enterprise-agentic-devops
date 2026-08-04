terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# 1. Dedicated Production Resource Group
resource "azurerm_resource_group" "ai_rg" {
  name     = "rg-enterprise-agentic-ai-prod"
  location = "East US"
}

# 2. Secure Hub-and-Spoke Network Infrastructure
resource "azurerm_virtual_network" "ai_vnet" {
  name                = "vnet-agentic-ai-prod"
  location            = azurerm_resource_group.ai_rg.location
  resource_group_name = azurerm_resource_group.ai_rg.name
  address_space       = ["10.1.0.0/16"]
}

resource "azurerm_subnet" "aks_subnet" {
  name                 = "snet-aks-pods-prod"
  resource_group_name  = azurerm_resource_group.ai_rg.name
  virtual_network_name = azurerm_virtual_network.ai_vnet.name
  address_prefixes     = ["10.1.1.0/24"]
}

# 3. Enterprise-Grade Private AKS Cluster Core
resource "azurerm_kubernetes_cluster" "aks" {
  name                    = "aks-agentic-ops-prod"
  location                = azurerm_resource_group.ai_rg.location
  resource_group_name     = azurerm_resource_group.ai_rg.name
  dns_prefix              = "agenticops"
  private_cluster_enabled = true # Strict zero-trust enterprise isolation

  default_node_pool {
    name            = "systempool"
    node_count      = 3
    vm_size         = "Standard_D4s_v5" # Compute SKU optimized for multi-agent execution loops
    vnet_subnet_id  = azurerm_subnet.aks_subnet.id
    type            = "VirtualMachineScaleSets"
    os_disk_size_gb = 128
  }

  # Eliminates static cloud keys - utilizes native system identity token exchanges
  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure" # Advanced Azure CNI mapping for network isolation policies
    load_balancer_sku = "standard"
    outbound_type     = "loadBalancer"
  }

  tags = {
    Environment  = "Production"
    Architecture = "Forward-Deployed-AI"
  }
}

# Output hooks to link with your deployment tooling layers later
output "aks_cluster_name" {
  value       = azurerm_kubernetes_cluster.aks.name
  description = "The cluster name context of the production AKS instance."
}
