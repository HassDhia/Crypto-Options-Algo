output "edge_vps_ip" {
  description = "Public IPv4 address of the Edge VPS"
  value       = hcloud_server.edge_vps.ipv4_address
}
