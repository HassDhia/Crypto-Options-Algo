provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ----------- networking -----------
resource "google_compute_network" "gke_vpc" {
  name                    = "gke-core-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "gke_subnet" {
  name          = "gke-core-subnet"
  ip_cidr_range = "10.50.0.0/16"
  network       = google_compute_network.gke_vpc.id
  region        = var.region
}

# ----------- GKE cluster -----------
resource "google_container_cluster" "gke" {
  name     = var.gke_cluster_name
  location = var.region

  network    = google_compute_network.gke_vpc.id
  subnetwork = google_compute_subnetwork.gke_subnet.id

  remove_default_node_pool = true
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel { channel = "REGULAR" }
  enable_autopilot = false
}

resource "google_container_node_pool" "primary" {
  name       = "default-pool"
  location   = var.region
  cluster    = google_container_cluster.gke.name
  node_count = var.node_count

  node_config {
    machine_type = var.node_machine_type
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    tags = var.network_tags
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  lifecycle { ignore_changes = [ node_count ] }
}

# ----------- OIDC SA for GitHub Actions -----------
resource "google_service_account" "gha_oidc" {
  account_id   = "gha-terraform"
  display_name = "GitHub Actions Terraform deployer"
}

resource "google_project_iam_member" "gha_oidc_token" {
  role   = "roles/iam.workloadIdentityUser"
  member = "principalSet://iam.googleapis.com/${google_service_account.gha_oidc.name}/attribute.repository/${var.project_id}/Crypto-Options-Algo"
}

output "gha_service_account_email" {
  value = google_service_account.gha_oidc.email
}
