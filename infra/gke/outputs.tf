output "cluster_name"        { value = google_container_cluster.gke.name }
output "cluster_region"      { value = google_container_cluster.gke.location }
output "network_name"        { value = google_compute_network.gke_vpc.name }
output "subnet_cidr"         { value = google_compute_subnetwork.gke_subnet.ip_cidr_range }
