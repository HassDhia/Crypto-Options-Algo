terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.44"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

resource "hcloud_server" "edge_vps" {
  name        = "edge-vps-ams1"
  image       = "ubuntu-22.04"
  server_type = "cx21"
  location    = "ams1"
  ssh_keys    = [hcloud_ssh_key.default.id]
}

resource "hcloud_ssh_key" "default" {
  name       = "edge-vps-key"
  public_key = file(var.ssh_public_key_path)
}

output "ipv4_address" {
  value = hcloud_server.edge_vps.ipv4_address
}
