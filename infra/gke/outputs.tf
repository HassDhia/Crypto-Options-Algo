output "cluster_name"        { value = module.gke.name }
output "cluster_region"      { value = var.region }
output "network_name"        { value = google_compute_network.vpc.name }
output "subnet_cidr"         { value = google_compute_subnetwork.subnet.ip_cidr_range }
