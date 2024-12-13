terraform {
  required_providers {
    opennebula = {
      source  = "OpenNebula/opennebula"
      version = "~> 1.4"
    }
    vault = {
      source  = "hashicorp/vault"
      version = ">= 3.0.0"
    }
  }
}

provider "vault" {
  address = "http://127.0.0.1:8200"
}

data "vault_kv_secret_v2" "opennebula_credentials" {
  mount = "secret"
  name  = "opennebula"
}

provider "opennebula" {
  endpoint = var.opennebula_endpoint
  username = data.vault_kv_secret_v2.opennebula_credentials.data["username"]
  password = data.vault_kv_secret_v2.opennebula_credentials.data["password"]
}

data "opennebula_template" "base_template" {
  name = var.template_name
}

data "opennebula_image" "ubuntu_image" {
  name = var.image_name
}

data "opennebula_virtual_network" "frontend_net" {
  name = var.frontend_net_name
}

data "opennebula_virtual_network" "backend_net" {
  name = var.backend_net_name
}

resource "opennebula_virtual_machine" "k8s_master" {
  count       = 2
  template_id = data.opennebula_template.base_template.id
  name        = "k8s-master-${count.index}"
  cpu         = 2
  vcpu        = 2
  memory      = 4096
  context     = {
    HOSTNAME = "$NAME"
  }

  disk {
    image_id = data.opennebula_image.ubuntu_image.id
    size     = 15000
  }

  os {
    arch = "x86_64"
    boot = "disk0"
  }

  nic {
    network_id = data.opennebula_virtual_network.frontend_net.id
    ip         = var.master_fe_ips[count.index]
  }

  nic {
    network_id = data.opennebula_virtual_network.backend_net.id
    ip         = var.master_be_ips[count.index]
  }
}

resource "opennebula_virtual_machine" "k8s_worker" {
  count       = 2
  template_id = data.opennebula_template.base_template.id
  name        = "k8s-worker-${count.index}"
  cpu         = 2
  vcpu        = 2
  memory      = 4096
  context     = {
    HOSTNAME = "$NAME"
  }

  disk {
    image_id = data.opennebula_image.ubuntu_image.id
    size     = 15000
  }

  os {
    arch = "x86_64"
    boot = "disk0"
  }

  nic {
    network_id = data.opennebula_virtual_network.frontend_net.id
    ip         = var.worker_fe_ips[count.index]
  }

  nic {
    network_id = data.opennebula_virtual_network.backend_net.id
    ip         = var.worker_be_ips[count.index]
  }
}

output "master_ips" {
  value = [for vm in opennebula_virtual_machine.k8s_master : vm.ip]
}

output "worker_ips" {
  value = [for vm in opennebula_virtual_machine.k8s_worker : vm.ip]
}
