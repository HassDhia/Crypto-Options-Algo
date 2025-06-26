resource "google_compute_network" "vpc" {
  name                    = "btc-options-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "btc-options-subnet"
  ip_cidr_range = "10.10.0.0/16"
  region        = var.region
  network       = google_compute_network.vpc.id
}

module "gke" {
  source  = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"
  version = "~> 30.0"

  project_id  = var.project_id
  name        = var.gke_cluster_name
  region      = var.region
  network     = google_compute_network.vpc.name
  subnetwork  = google_compute_subnetwork.subnet.name

  node_pools = [
    {
      name         = "primary"
      machine_type = var.node_machine_type
      min_count    = 3
      max_count    = 3
    },
  ]

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
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
